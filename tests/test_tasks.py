import pytest
from uuid import uuid4
from unittest.mock import AsyncMock
from httpx import AsyncClient, ASGITransport

from src.api.app import app
from src.core.dependencies import get_repository, get_create_task
from src.domain.entities.task import Task
from src.domain.enums.task_status import TaskStatus


USER_ID = str(uuid4())


def make_task(**kwargs):
    defaults = dict(title="Test", user_id=uuid4(), payload={})
    defaults.update(kwargs)
    return Task(**defaults)


@pytest.fixture
def mock_repo():
    return AsyncMock()


@pytest.fixture
def mock_create_use_case():
    return AsyncMock()


@pytest.fixture
def test_app(mock_repo, mock_create_use_case):
    app.dependency_overrides[get_repository] = lambda: mock_repo
    app.dependency_overrides[get_create_task] = lambda: mock_create_use_case
    yield app
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_task(test_app, mock_create_use_case):
    task = make_task(title="My Task")
    mock_create_use_case.execute.return_value = task

    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
        response = await client.post("/tasks/", json={
            "title": "My Task",
            "user_id": USER_ID,
            "payload": {}
        })

    assert response.status_code == 200
    assert response.json()["title"] == "My Task"
    assert response.json()["status"] == "pending"


@pytest.mark.asyncio
async def test_get_task_status(test_app, mock_repo):
    task = make_task(title="My Task", status=TaskStatus.SUCCESS)
    mock_repo.get_by_id.return_value = task

    task_id = str(task.id)
    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
        response = await client.get(f"/tasks/{task_id}")

    assert response.status_code == 200
    assert response.json() == "success"


@pytest.mark.asyncio
async def test_get_task_not_found(test_app, mock_repo):
    mock_repo.get_by_id.return_value = None

    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
        response = await client.get(f"/tasks/{uuid4()}")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_tasks(test_app, mock_repo):
    tasks = [make_task(title="Task 1"), make_task(title="Task 2")]
    mock_repo.get_all.return_value = tasks

    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
        response = await client.get("/tasks/")

    assert response.status_code == 200
    assert len(response.json()) == 2
