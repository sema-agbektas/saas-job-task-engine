from src.application.interfaces.task_repository import TaskRepository
from src.domain.entities.task import Task

class GetTaskStatus:
    def __init__(self,task_repository):
        self.task_repository = task_repository
    
    async def execute(self,task_id):
        task =await self.task_repository.get_by_id(task_id)
        return task.status