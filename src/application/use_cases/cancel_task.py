from src.application.interfaces.task_repository import TaskRepository
from src.domain.entities.task import Task
from src.domain.enums.task_status import TaskStatus
class CancelTask:
    def __init__(self,task_repository):
        self.task_repository=task_repository
    
    async def execute(self,task_id):
        db_task = await self.task_repository.get_by_id(task_id)
        db_task.status=TaskStatus.CANCELLED
        await self.task_repository.update(db_task)
        return db_task
