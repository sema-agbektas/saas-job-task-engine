from src.domain.exceptions.domain_exceptions import TaskNotFoundError
from src.application.interfaces.task_repository import TaskRepository
from src.domain.entities.task import Task
from src.domain.enums.task_status import TaskStatus
class CancelTask:
    def __init__(self,task_repository):
        self.task_repository=task_repository
    
    async def execute(self,task_id,current_user):
        db_task = await self.task_repository.get_by_id(task_id)
        if db_task is None:
         raise TaskNotFoundError(task_id)

        if db_task.user_id != current_user.id:
         raise PermissionError("Bu task'ı iptal etme yetkin yok")
        db_task.status=TaskStatus.CANCELLED
        await self.task_repository.update(db_task)
        return db_task
