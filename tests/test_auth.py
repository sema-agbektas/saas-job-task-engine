import pytest
from unittest.mock import AsyncMock
from httpx import AsyncClient, ASGITransport

from src.api.app import app
from src.core.dependencies import get_user_repository
from src.domain.entities.user import User


@pytest.fixture
def mock_user_repo():
    return AsyncMock()


@pytest.fixture
def test_app(mock_user_repo):
    app.dependency_overrides[get_user_repository] = lambda: mock_user_repo
    yield app
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_register_success(test_app, mock_user_repo):
    mock_user_repo.get_by_email.return_value = None
    mock_user_repo.save.return_value = User(email="yeni@example.com", hashed_password="hash")

    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
        response = await client.post("/auth/register", json={
            "email": "yeni@example.com",
            "password": "Guvenli123"
        })

    assert response.status_code == 201
    assert response.json()["email"] == "yeni@example.com"

@pytest.mark.asyncio
async def test_register_duplicate_email(test_app, mock_user_repo):
    mock_user_repo.get_by_email.return_value = User(email="yeni@example.com", hashed_password="hash")

    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
        response = await client.post("/auth/register", json={
            "email": "yeni@example.com",
            "password": "Guvenli123"
        })

    assert response.status_code == 400

@pytest.mark.asyncio
async def test_login_success(test_app,mock_user_repo):
    from src.core.security import get_password_hash
    real_hash=get_password_hash("Guvenli123")
    mock_user_repo.get_by_email.return_value=User(email="yeni@example.com",hashed_password=real_hash)
    async with AsyncClient(transport=ASGITransport(app=test_app),base_url="http://test") as client:
        response = await client.post("/auth/login",json={
            "email":"yeni@example.com",
            "password":"Guvenli123"
        })
    assert response.status_code==200
    assert "access_token" in response.json()

@pytest.mark.asyncio
async def test_login_wrong_password(test_app, mock_user_repo):
    from src.core.security import get_password_hash
    real_hash = get_password_hash("Guvenli123")
    mock_user_repo.get_by_email.return_value = User(email="yeni@example.com", hashed_password=real_hash)
    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
        response = await client.post("/auth/login", json={
            "email": "yeni@example.com",
            "password": "YanlisSifre123"
        })
        assert response.status_code == 401