from src.application.interfaces.task_repository import TaskRepository 
from src.domain.entities.task import Task
class CreateTask:
    def __init__(self,task_repository:TaskRepository):
        self.task_repository = task_repository
        

    async def execute(self, title,user_id,payload) :
        task= Task(title=title,user_id=user_id,payload=payload)
        await self.task_repository.save(task)
        return task