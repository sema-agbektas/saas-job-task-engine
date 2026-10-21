import asyncio
import logging
from uuid import UUID

import redis.asyncio as aioredis
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.core.config import settings
from src.domain.enums.task_status import TaskStatus
from src.infrastructure.repositories.pg_task_repository import PostgreSQLTaskRepository
import time
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

QUEUE_NAME = "task_queue"
MAX_RETRIES = 3
DEAD_LETTER_QUEUE="dead_letter_queue"

# Database URL'i config'den oluştur
DATABASE_URL = (
    f"postgresql+asyncpg://{settings.POSTGRES_USER}:"
    f"{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:"
    f"{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
)

engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def process_task(task_id: str,redis):
    async with AsyncSessionLocal() as session:
        repository = PostgreSQLTaskRepository(session)

        task = await repository.get_by_id(UUID(task_id))
        if not task:
            logger.warning(f"Task bulunamadı: {task_id}")
            return

        task.status = TaskStatus.RUNNING
        await repository.update(task)
        logger.info(f"İşleniyor: {task.title}")

        try:
            # Asıl iş buraya gelecek
            await asyncio.sleep(2)

            task.status = TaskStatus.SUCCESS
            await repository.update(task)
            logger.info(f"Tamamlandı: {task.title}")

        except Exception as e:
            logger.error(f"Hata: {e}")

            if task.retry_count < MAX_RETRIES:
                task.retry_count += 1
                task.status = TaskStatus.RETRYING
                await repository.update(task)
                delay = 2 ** task.retry_count
                score = time.time() + delay
                await redis.zadd("retry_queue", {task_id: score}) 
                logger.info(f"Tekrar deniyor ({task.retry_count}/{MAX_RETRIES})")
            else:
                task.status = TaskStatus.FAILED
                await repository.update(task)
                await redis.rpush(DEAD_LETTER_QUEUE,task_id)
                logger.error(f"Başarısız: {task_id}")


async def run_worker():
    redis = await aioredis.from_url(settings.REDIS_URL)
    logger.info("Worker başladı, kuyruk dinleniyor...")

    while True:
        try:
            now = time.time()
            due=await redis.zrangebyscore("retry_queue",0,now,)
            for item in due:
                removed=await redis.zrem("retry_queue",item)
                if removed:
                    await redis.rpush(QUEUE_NAME,item)
            
            result = await redis.blpop(QUEUE_NAME, timeout=5)
            if result:
                _, task_id = result
                await process_task(task_id.decode("utf-8"),redis)

        except Exception as e:
            logger.error(f"Worker hatası: {e}")
            await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(run_worker())