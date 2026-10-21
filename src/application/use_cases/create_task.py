from src.application.interfaces.task_repository import TaskRepository 
from src.domain.entities.task import Task
import redis.asyncio as aioredis
from sqlalchemy.exc import IntegrityError
QUEUE_NAME = "task_queue"

class CreateTask:
    def __init__(self,task_repository:TaskRepository,redis_url:str):
        self.task_repository = task_repository
        self.redis_url=redis_url

    async def execute(self, title,user_id,payload,idempotency_key: str) :
        task= Task(title=title,user_id=user_id,payload=payload,idempotency_key=idempotency_key)
        try:
            await self.task_repository.save(task)
        except IntegrityError:
         existing_task = await self.task_repository.get_by_idempotency_key(idempotency_key)
         return existing_task
        redis=await aioredis.from_url(self.redis_url)
        await redis.rpush( QUEUE_NAME, str(task.id) )
        return task
        