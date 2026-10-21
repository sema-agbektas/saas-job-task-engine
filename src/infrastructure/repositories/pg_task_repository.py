from src.application.interfaces.task_repository import TaskRepository 
from src.domain.entities.task import Task
from src.infrastructure.database.models import TaskModel
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError


class PostgreSQLTaskRepository(TaskRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, task: Task):
        db_task = TaskModel(
            id=task.id,
            title=task.title,
            status=task.status,
            user_id=task.user_id,
            retry_count=task.retry_count,
            created_at=task.created_at,
            payload=task.payload,
            idempotency_key=task.idempotency_key
        )
        self.session.add(db_task)
        try:
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            raise

    async def get_by_id(self, task_id: UUID):
        result = await self.session.execute(select(TaskModel).where(TaskModel.id == task_id))
        return result.scalar_one_or_none()

    async def update(self, task: Task):
        db_task = await self.get_by_id(task.id)
        db_task.status = task.status
        db_task.retry_count = task.retry_count
        db_task.payload = task.payload
        await self.session.commit()

    async def delete(self, task_id: UUID):
        db_task = await self.get_by_id(task_id)
        await self.session.delete(db_task)
        await self.session.commit()

    async def get_all(self):
        result = await self.session.execute(select(TaskModel))
        return result.scalars().all()

    async def get_by_user_id(self, user_id: UUID, limit: int = 20, offset: int = 0):
        result = await self.session.execute(
            select(TaskModel).where(TaskModel.user_id == user_id).limit(limit).offset(offset)
        )
        return result.scalars().all()

    async def get_by_idempotency_key(self, idempotency_key: str):
        result = await self.session.execute(select(TaskModel).where(TaskModel.idempotency_key == idempotency_key))
        return result.scalar_one_or_none()