import pytest
from unittest.mock import AsyncMock,patch
from uuid import uuid4

from src.worker import process_task

@pytest.mark.asyncio
async def test_process_task_not_found():
    mock_repo=AsyncMock()
    mock_redis=AsyncMock()
    mock_repo.get_by_id.return_value=None

    with patch("src.worker.PostgreSQLTaskRepository", return_value=mock_repo), \
         patch("src.worker.AsyncSessionLocal"):
        await process_task(str(uuid4()), mock_redis)

    mock_repo.update.assert_not_called()

@pytest.mark.asyncio
async def test_process_task_success():
    from src.domain.entities.task import Task

    task = Task(title="Test", user_id=uuid4(), payload={})
    mock_repo = AsyncMock()
    mock_redis = AsyncMock()
    mock_repo.get_by_id.return_value = task

    with patch("src.worker.PostgreSQLTaskRepository", return_value=mock_repo), \
         patch("src.worker.AsyncSessionLocal"):
        await process_task(str(task.id), mock_redis)

    assert task.status.value == "success"


@pytest.mark.asyncio
async def test_process_task_retries_on_failure():
    from src.domain.entities.task import Task

    task = Task(title="Test", user_id=uuid4(), payload={})
    mock_repo = AsyncMock()
    mock_redis = AsyncMock()
    mock_repo.get_by_id.return_value = task

    with patch("src.worker.PostgreSQLTaskRepository", return_value=mock_repo), \
         patch("src.worker.AsyncSessionLocal"), \
         patch("src.worker.asyncio.sleep", side_effect=Exception("Simulated failure")):
        await process_task(str(task.id), mock_redis)

    assert task.status.value == "retrying"
    assert task.retry_count == 1
    mock_redis.zadd.assert_called_once()
@pytest.mark.asyncio
async def test_task_moves_to_dead_letter_queue_after_max_retries():
    from src.domain.entities.task import Task

    task = Task(title="Test", user_id=uuid4(), payload={},retry_count=3)
    mock_repo = AsyncMock()
    mock_redis = AsyncMock()
    mock_repo.get_by_id.return_value = task

    with patch("src.worker.PostgreSQLTaskRepository", return_value=mock_repo), \
         patch("src.worker.AsyncSessionLocal"), \
         patch("src.worker.asyncio.sleep", side_effect=Exception("Simulated failure")):
        await process_task(str(task.id), mock_redis)

    assert task.status.value == "failed"
    mock_redis.rpush.assert_called_once_with("dead_letter_queue", str(task.id))
    mock_redis.zadd.assert_not_called()
@pytest.mark.asyncio
async def test_retrying_task_is_added_to_retry_queue():
    """
    Hata alan bir task RETRYING olur ve bekleme süresiyle birlikte
    retry_queue sorted set'ine eklenir (artık kuyruktan düşüp kaybolmaz).
    """
    from src.domain.entities.task import Task

    task = Task(title="Test", user_id=uuid4(), payload={})
    mock_repo = AsyncMock()
    mock_redis = AsyncMock()
    mock_repo.get_by_id.return_value = task

    with patch("src.worker.PostgreSQLTaskRepository", return_value=mock_repo), \
         patch("src.worker.AsyncSessionLocal"), \
         patch("src.worker.asyncio.sleep", side_effect=Exception("Simulated failure")):
        await process_task(str(task.id), mock_redis)

    mock_redis.zadd.assert_called_once()
    assert mock_redis.zadd.call_args[0][0] == "retry_queue"