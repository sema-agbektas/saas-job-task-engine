
from src.infrastructure.database.session import get_session
from src.infrastructure.repositories.pg_task_repository import  PostgreSQLTaskRepository
from fastapi import Depends
async def get_repository(session=Depends(get_session)):
    return PostgreSQLTaskRepository(session)