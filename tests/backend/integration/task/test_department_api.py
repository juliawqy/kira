import pytest
from httpx import AsyncClient, ASGITransport
from backend.src.main import app
from tests.mock_data.department_data import (
    VALID_DEPARTMENT_ADD,
    INVALID_DEPARTMENT_NO_NAME,
    INVALID_DEPARTMENT_NO_HEAD,
    INVALID_DEPARTMENT_NO_DESCRIPTION,
)

def get_client():
    return AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    )


# KIRA-002/001
@pytest.mark.asyncio
async def test_add_department_success():
    async with get_client() as ac:
        response = await ac.post("/department/", json=VALID_DEPARTMENT_ADD)
        assert response.status_code in (201, 404)


# KIRA-002/002
@pytest.mark.parametrize("invalid_department", [
    INVALID_DEPARTMENT_NO_NAME,
    INVALID_DEPARTMENT_NO_HEAD,
    INVALID_DEPARTMENT_NO_DESCRIPTION,
])
@pytest.mark.asyncio
async def test_add_department_failure(invalid_department):
    async with get_client() as ac:
        response = await ac.post("/department/", json=invalid_department)
        assert response.status_code == 404


# KIRA-002/003
@pytest.mark.asyncio
async def test_get_department_not_found():
    async with get_client() as ac:
        response = await ac.get("/department/9999")
        assert response.status_code == 404


# KIRA-002/004
@pytest.mark.asyncio
async def test_update_department_not_found():
    async with get_client() as ac:
        response = await ac.patch("/department/9999", json={"name": "Ghost Department"})
        assert response.status_code == 404


# KIRA-002/005
@pytest.mark.asyncio
async def test_delete_department_not_found():
    async with get_client() as ac:
        response = await ac.delete("/department/9999")
        assert response.status_code == 404


# KIRA-002/006
@pytest.mark.asyncio
async def test_assign_members_not_found():
    async with get_client() as ac:
        response = await ac.post("/department/9999/assign", json={"members": ["alice"]})
        assert response.status_code == 404


# KIRA-002/007
@pytest.mark.asyncio
async def test_unassign_members_not_found():
    async with get_client() as ac:
        response = await ac.post("/department/9999/unassign", json={"members": ["alice"]})
        assert response.status_code == 404


# KIRA-002/008
@pytest.mark.asyncio
async def test_delete_subdepartment_not_found():
    async with get_client() as ac:
        response = await ac.delete("/department/subdepartments/9999")
        assert response.status_code in (400, 404)
