
from src.infrastructure.database.session import get_session
from src.infrastructure.repositories.pg_task_repository import  PostgreSQLTaskRepository
from src.application.use_cases.create_task import CreateTask
from src.core.config import settings
from fastapi import Depends
async def get_repository(session=Depends(get_session)):
    return PostgreSQLTaskRepository(session)

async def get_create_task(repository=Depends(get_repository)):
    return CreateTask(
        task_repository=repository,
        redis_url=settings.REDIS_URL
    )