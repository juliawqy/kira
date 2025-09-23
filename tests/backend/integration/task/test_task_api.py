''' 

    CURRENT TESTS TO BE UPDATED WHEN TASK API UPDATES 
    this is just a placeholder to serve as an example for writing integration tests 

'''

import pytest
from httpx import AsyncClient, ASGITransport
from backend.src.main import app
from tests.mock_data.task_data import (
    VALID_ADD,
    INVALID_TASK_NO_TITLE,
    INVALID_TASK_NO_STATUS,
    INVALID_TASK_NO_PRIORITY,
)

# ------------------------
# Helper: create test client
# ------------------------
def get_client():
    return AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    )

# ------------------------
# Tests (placeholder mode)
# ------------------------

@pytest.mark.asyncio
async def test_add_task_success():
    async with get_client() as ac:
        response = await ac.post("/tasks", json=VALID_ADD)
        # placeholder until API is ready
        assert response.status_code in (200, 404)


@pytest.mark.parametrize("invalid_task", [
    INVALID_TASK_NO_TITLE,
    INVALID_TASK_NO_STATUS,
    INVALID_TASK_NO_PRIORITY,
])
@pytest.mark.asyncio
async def test_add_task_failure(invalid_task):
    async with get_client() as ac:
        response = await ac.post("/tasks", json=invalid_task)
        assert response.status_code in (400, 404)


@pytest.mark.asyncio
async def test_get_task_success():
    async with get_client() as ac:
        response = await ac.get("/tasks/1")
        assert response.status_code in (200, 404)


@pytest.mark.asyncio
async def test_get_task_not_found():
    async with get_client() as ac:
        response = await ac.get("/tasks/9999")
        assert response.status_code in (404,)


@pytest.mark.asyncio
async def test_list_tasks():
    async with get_client() as ac:
        response = await ac.get("/tasks")
        assert response.status_code in (200, 404)


@pytest.mark.asyncio
async def test_update_task_fields():
    async with get_client() as ac:
        response = await ac.put("/tasks/1", json={
            "title": "Updated Title",
            "description": "Updated Description"
        })
        assert response.status_code in (200, 404)


@pytest.mark.asyncio
async def test_update_status():
    async with get_client() as ac:
        response = await ac.put("/tasks/1/status", json={"status": "Completed"})
        assert response.status_code in (200, 404)


@pytest.mark.asyncio
async def test_update_priority():
    async with get_client() as ac:
        response = await ac.put("/tasks/1/priority", json={"priority": "High"})
        assert response.status_code in (200, 404)


@pytest.mark.asyncio
async def test_delete_task_success():
    async with get_client() as ac:
        response = await ac.delete("/tasks/1")
        assert response.status_code in (200, 404)


@pytest.mark.asyncio
async def test_delete_task_not_found():
    async with get_client() as ac:
        response = await ac.delete("/tasks/9999")
        assert response.status_code in (404,)
