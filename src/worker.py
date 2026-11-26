import asyncio
import logging
import os 
import socket
from src.infrastructure.logging_config import setup_logging, task_id_var, worker_id_var
from uuid import UUID

import redis.asyncio as aioredis
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.core.config import settings
from src.domain.enums.task_status import TaskStatus
from src.infrastructure.repositories.pg_task_repository import PostgreSQLTaskRepository
import time
logger = logging.getLogger(__name__)

QUEUE_NAME = "task_queue"
MAX_RETRIES = 3
DEAD_LETTER_QUEUE="dead_letter_queue"
STUCK_TIMEOUT_SECONDS = 300
RECOVERY_INTERVAL_SECONDS = 60
# Database URL'i config'den oluştur
DATABASE_URL = (
    f"postgresql+asyncpg://{settings.POSTGRES_USER}:"
    f"{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:"
    f"{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
)

engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def process_task(task_id: str,redis):
    task_id_var.set(task_id)
    async with AsyncSessionLocal() as session:
        repository = PostgreSQLTaskRepository(session)

        task = await repository.get_by_id(UUID(task_id))
        if not task:
            logger.warning(f"Task bulunamadı: {task_id}")
            return
        if task.status not in (TaskStatus.PENDING,TaskStatus.RETRYING):
            logger.warning(f"Task zaten işleniyor veya bitmiş: {task_id}")
            return
        claimed = await repository.claim_task(task.id)
        if not claimed:
            logger.warning(f"Task başka worker tarafından alındı: {task_id}")
            return

        task.status = TaskStatus.RUNNING
        logger.info(f"İşleniyor: {task.title}")


        try:
            # Asıl iş buraya gelecek
            start_time = time.time()
            await asyncio.sleep(2)
            if task.payload and task.payload.get("fail"):
                raise Exception("Simüle edilmiş hata")

            finished=await repository.finish_task(task.id,TaskStatus.SUCCESS.value)
            if not finished:
                logger.warning(f"Task{task.id}success yazılırken iptal edilmiş")
                return
            logger.info(
                "task tamamlandı",
                extra={
                    "duration_ms": int((time.time() - start_time) * 1000),
                    "retry_count": task.retry_count,
                },

            )
        except Exception as e:
            logger.exception("Task işlenirken hata")
            if task.retry_count < MAX_RETRIES:
                task.retry_count += 1
                updated=await repository.mark_retrying(task.id,task.retry_count)
                if not updated:
                    logger.warning(f"Task{task.id}retry sırasında iptal edilmiş, kuyruğa eklenmedi")
                    return
                delay=2**task.retry_count
                score = time.time() + delay
                await redis.zadd("retry_queue", {task_id: score}) 
                logger.info(f"Tekrar deniyor ({task.retry_count}/{MAX_RETRIES})")
            else:
                updated=await repository.finish_task(task.id,TaskStatus.FAILED.value)
                if not updated:
                    logger.warning(f"Task{task.id} failed yazılırken iptal edilmiş")
                    return
                await redis.rpush(DEAD_LETTER_QUEUE,task_id)
                logger.error(f"Başarısız: {task_id}")

async def recover_stuck_tasks(redis):
    async with AsyncSessionLocal() as session:
        repository = PostgreSQLTaskRepository(session)

        recovered=await repository.recover_stuck_tasks(STUCK_TIMEOUT_SECONDS, MAX_RETRIES)
        for task_id in recovered:
            await redis.rpush(QUEUE_NAME,str(task_id))
            logger.warning(f"Takılı task kurtarıldı:{task_id}")

        failed=await repository.fail_stuck_tasks(STUCK_TIMEOUT_SECONDS,MAX_RETRIES)
        for task_id in failed:
            await redis.rpush(DEAD_LETTER_QUEUE,str(task_id))
            logger.error(f"Takılı task başarısız sayıldı:{task_id}")


async def run_worker():
    setup_logging()
    worker_id_var.set(f"{socket.gethostname()}-{os.getpid()}")
    redis = await aioredis.from_url(settings.REDIS_URL)
    logger.info("Worker başladı, kuyruk dinleniyor...")
    last_recovery = 0

    while True:
        try:
            if time.time() - last_recovery > RECOVERY_INTERVAL_SECONDS:
                try:
                    await recover_stuck_tasks(redis)
                except Exception as e:
                    logger.error(f"Kurtarma hatası: {e}")
                last_recovery = time.time()
            now = time.time()
            due = await redis.zrangebyscore("retry_queue", 0, now)
            for item in due:
                removed = await redis.zrem("retry_queue", item)
                if removed:
                    await redis.rpush(QUEUE_NAME, item)

            result = await redis.blpop(QUEUE_NAME, timeout=5)
            if result:
                _, task_id = result
                await process_task(task_id.decode("utf-8"), redis)

        except Exception as e:
            logger.error(f"Worker hatası: {e}")
            await asyncio.sleep(1)
if __name__ == "__main__":
    asyncio.run(run_worker())