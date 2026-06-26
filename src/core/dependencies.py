from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from src.core.config import settings
from src.infrastructure.database.session import get_session
from src.infrastructure.repositories.pg_task_repository import PostgreSQLTaskRepository
from src.infrastructure.repositories.pg_user_repository import PostgreSQLUserRepository
from src.application.use_cases.create_task import CreateTask
from src.core.security import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


async def get_repository(session=Depends(get_session)):
    return PostgreSQLTaskRepository(session)


async def get_create_task(repository=Depends(get_repository)):
    return CreateTask(
        task_repository=repository,
        redis_url=settings.REDIS_URL
    )


async def get_current_user(token: str = Depends(oauth2_scheme), session=Depends(get_session)):
    email = decode_token(token)
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token")
    repo = PostgreSQLUserRepository(session)
    user = await repo.get_by_email(email)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user
