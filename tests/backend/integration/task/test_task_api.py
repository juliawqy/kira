import pytest
from httpx import AsyncClient, ASGITransport
from backend.src.main import app
from tests.mock_data.task_data import (
    VALID_ADD,
    INVALID_TASK_NO_TITLE,
    INVALID_TASK_NO_STATUS,
    INVALID_TASK_NO_PRIORITY,
)

def get_client():
    return AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    )

# #KIRA-001/001 (test case id corresponding to test case sheets)
# @pytest.mark.asyncio
# async def test_add_task_success():
#     async with get_client() as ac:
#         response = await ac.post("/task/", json=VALID_ADD)
#         assert response.status_code in (201, 404)

# #KIRA-001/001 (test case id corresponding to test case sheets)
# @pytest.mark.parametrize("invalid_task", [
#     INVALID_TASK_NO_TITLE,
#     INVALID_TASK_NO_STATUS,
#     INVALID_TASK_NO_PRIORITY,
# ])
# @pytest.mark.asyncio
# async def test_add_task_failure(invalid_task):
#     async with get_client() as ac:
#         response = await ac.post("/task/", json=invalid_task)
#         assert response.status_code == 404

# #KIRA-001/001 (test case id corresponding to test case sheets)
# @pytest.mark.asyncio
# async def test_get_task_not_found():
#     async with get_client() as ac:
#         response = await ac.get("/task/9999")
#         assert response.status_code == 404

# #KIRA-001/001 (test case id corresponding to test case sheets)
# @pytest.mark.asyncio
# async def test_update_task_not_found():
#     async with get_client() as ac:
#         response = await ac.patch("/task/9999", json={"title": "ghost"})
#         assert response.status_code == 404

# #KIRA-001/001 (test case id corresponding to test case sheets)
# @pytest.mark.asyncio
# async def test_delete_task_not_found():
#     async with get_client() as ac:
#         response = await ac.delete("/task/9999")
#         assert response.status_code == 404

# #KIRA-001/001 (test case id corresponding to test case sheets)
# @pytest.mark.asyncio
# async def test_start_task_not_found():
#     async with get_client() as ac:
#         response = await ac.post("/task/9999/start")
#         assert response.status_code == 404

# #KIRA-001/001 (test case id corresponding to test case sheets)
# @pytest.mark.asyncio
# async def test_complete_task_not_found():
#     async with get_client() as ac:
#         response = await ac.post("/task/9999/complete")
#         assert response.status_code == 404

# #KIRA-001/001 (test case id corresponding to test case sheets)
# @pytest.mark.asyncio
# async def test_assign_task_not_found():
#     async with get_client() as ac:
#         response = await ac.post("/task/9999/assign", json={"users": ["bob"]})
#         assert response.status_code == 404

# #KIRA-001/001 (test case id corresponding to test case sheets)
# @pytest.mark.asyncio
# async def test_unassign_task_not_found():
#     async with get_client() as ac:
#         response = await ac.post("/task/9999/unassign", json={"users": ["bob"]})
#         assert response.status_code == 404

# #KIRA-001/001 (test case id corresponding to test case sheets)
# @pytest.mark.asyncio
# async def test_delete_subtask_not_found():
#     async with get_client() as ac:
#         response = await ac.delete("/task/subtasks/9999")
#         assert response.status_code in (400, 404)

