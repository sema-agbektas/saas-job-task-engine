import pytest
from uuid import uuid4
from datetime import datetime, timedelta, timezone
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

@pytest.mark.asyncio
async def test_claim_task_only_succeeds_once(db_session):
    repo = PostgreSQLTaskRepository(db_session)
    task = Task(title="Claim Test", user_id=uuid4(), payload={})

    await repo.save(task)

    first = await repo.claim_task(task.id)      # task'ın id'si
    second = await repo.claim_task(task.id)     # aynı id, ikinci kez

    db_session.expire_all()
    fetched = await repo.get_by_id(task.id)

    assert first is True         # True olmalı
    assert second is False         # False olmalı
    assert fetched.status == "running"

@pytest.mark.asyncio
async def test_recover_stuck_tasks_requeues_old_running_task(db_session):
    repo = PostgreSQLTaskRepository(db_session)
    task = Task(
        title="stuck",
        user_id=uuid4(),
        payload={},
        status=TaskStatus.RUNNING,
        started_at=datetime.now(timezone.utc) - timedelta(minutes=10),
    )
    await repo.save(task)

    recovered = await repo.recover_stuck_tasks(300, 3)

    assert task.id in recovered
    db_session.expire_all()
    saved = await repo.get_by_id(task.id)
    assert saved.status == "retrying"
    assert saved.retry_count == 1
