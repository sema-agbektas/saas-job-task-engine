import pytest
from uuid import uuid4
from unittest.mock import AsyncMock
from httpx import AsyncClient, ASGITransport

from src.api.app import app
from src.core.dependencies import get_repository, get_create_task,get_current_user
from src.domain.entities.task import Task
from src.domain.enums.task_status import TaskStatus
from src.domain.entities.user import User
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
def mock_user():
    return User(email="test@example.com",hashed_password="x")


@pytest.fixture
def test_app(mock_repo, mock_create_use_case,mock_user):
    app.dependency_overrides[get_repository] = lambda: mock_repo
    app.dependency_overrides[get_create_task] = lambda: mock_create_use_case
    app.dependency_overrides[get_current_user] = lambda: mock_user
    yield app
    app.dependency_overrides.clear()



@pytest.mark.asyncio
async def test_create_task(test_app, mock_create_use_case):
    task = make_task(title="My Task")
    mock_create_use_case.execute.return_value = task

    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
        response = await client.post(
            "/tasks/",
            json={"title": "My Task", "payload": {}},
            headers={"Idempotency-Key": "test-key-123"},
        )

    assert response.status_code == 200
    assert response.json()["title"] == "My Task"
    assert response.json()["status"] == "pending"
    mock_create_use_case.execute.assert_called_once()
    assert mock_create_use_case.execute.call_args[0][3] == "test-key-123"
@pytest.mark.asyncio
async def test_get_task_status(test_app, mock_repo,mock_user):
    task = make_task(title="My Task", status=TaskStatus.SUCCESS,user_id=mock_user.id)
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
    mock_repo.get_by_user_id.return_value = tasks

    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
        response = await client.get("/tasks/")

    assert response.status_code == 200
    assert len(response.json()) == 2

@pytest.mark.asyncio
async def test_cancel_task_forbidden(test_app, mock_repo, mock_user):
    other_users_task = make_task(title="Baskasinin Task'i", user_id=uuid4())
    mock_repo.get_by_id.return_value = other_users_task

    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
        response = await client.delete(f"/tasks/{other_users_task.id}")

    assert response.status_code == 403
@pytest.mark.asyncio
async def test_cancel_task_success(test_app, mock_repo, mock_user):
    own_task = make_task(title="Benim Task'im", user_id=mock_user.id)
    mock_repo.get_by_id.return_value = own_task

    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
        response = await client.delete(f"/tasks/{own_task.id}")

    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"