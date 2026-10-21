from src.application.interfaces.task_repository import TaskRepository
from src.domain.entities.task import Task
from src.domain.exceptions.domain_exceptions import TaskNotFoundError
class GetTaskStatus:
    def __init__(self,task_repository):
        self.task_repository = task_repository
    
    async def execute(self, task_id , current_user ):
        task = await self.task_repository.get_by_id(task_id)
        if task is None:
            raise TaskNotFoundError(task_id)
        if task.user_id != current_user.id:
           raise PermissionError("Bu task'ı iptal etme yetkin yok")
        return task.status