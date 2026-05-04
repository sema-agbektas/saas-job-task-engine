from src.application.interfaces.task_repository import TaskRepository

class ListTasks:
    def __init__(self, task_repository: TaskRepository):
        self.task_repository = task_repository

    async def execute(self):
        return await self.task_repository.get_all()