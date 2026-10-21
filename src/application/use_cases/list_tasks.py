from src.application.interfaces.task_repository import TaskRepository

class ListTasks:
    def __init__(self, task_repository: TaskRepository):
        self.task_repository = task_repository

    async def execute(self,current_user, limit: int = 20, offset: int = 0):
        return await self.task_repository.get_by_user_id(current_user.id,limit,offset)