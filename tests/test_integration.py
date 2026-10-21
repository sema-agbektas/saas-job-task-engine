import pytest
from uuid import uuid4

from src.domain.entities.task import Task
from src.infrastructure.repositories.pg_task_repository import PostgreSQLTaskRepository
from src.domain.enums.task_status import TaskStatus

@pytest.mark.asyncio
async def test_save_and_get_by_id(db_session):
    repo = PostgreSQLTaskRepository(db_session)
    task = Task(title="Integration Test Task", user_id=uuid4(), payload={"key": "value"})

    await repo.save(task)

    fetched = await repo.get_by_id(task.id)

    assert fetched is not None
    assert fetched.id == task.id
    assert fetched.title == "Integration Test Task"

@pytest.mark.asyncio
async def test_update_and_delete(db_session):
    repo = PostgreSQLTaskRepository(db_session)
    task = Task(title="Guncellenecek", user_id=uuid4(), payload={})
    await repo.save(task)

    task.status = task.status.__class__.SUCCESS
    await repo.update(task)
    updated = await repo.get_by_id(task.id)
    assert updated.status == "success"

    await repo.delete(task.id)
    deleted = await repo.get_by_id(task.id)
    assert deleted is None
