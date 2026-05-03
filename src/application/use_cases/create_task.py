from src.application.interfaces.task_repository import TaskRepository 
from src.domain.entities.task import Task
import redis.asyncio as aioredis

QUEUE_NAME = "task_queue"

class CreateTask:
    def __init__(self,task_repository:TaskRepository,redis_url:str):
        self.task_repository = task_repository
        self.redis_url=redis_url

    async def execute(self, title,user_id,payload) :
        task= Task(title=title,user_id=user_id,payload=payload)
        await self.task_repository.save(task)
        
    
        redis=await aioredis.from_url(self.redis_url)
        await redis.rpush( QUEUE_NAME, str(task.id) )
        return task