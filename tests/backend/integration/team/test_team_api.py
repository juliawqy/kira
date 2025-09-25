
import pytest
from httpx import AsyncClient, ASGITransport
from backend.src.main import app
from tests.mock_data.team_data import MANAGER_USER, MEMBER_USER, VALID_TEAM_CREATE, INVALID_TEAM_EMPTY, INVALID_TEAM_WHITESPACE

def get_client():
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")

@pytest.mark.asyncio
async def test_create_team_success():
    async with get_client() as ac:
        response = await ac.post("/kira/app/api/v1/team/", json=VALID_TEAM_CREATE)
        assert response.status_code == 201
        assert response.json()["team_name"] == VALID_TEAM_CREATE["team_name"]

@pytest.mark.asyncio
@pytest.mark.parametrize("invalid_team", [INVALID_TEAM_EMPTY, INVALID_TEAM_WHITESPACE])
async def test_create_team_invalid(invalid_team):
    async with get_client() as ac:
        response = await ac.post("/kira/app/api/v1/team/", json=invalid_team)
        assert response.status_code == 400

@pytest.mark.asyncio
async def test_view_team_success():
    async with get_client() as ac:
        # Create a team
        create_resp = await ac.post("/kira/app/api/v1/team/", json=VALID_TEAM_CREATE)
        team_id = create_resp.json()["team_id"]
        # View the team
        response = await ac.get(f"/kira/app/api/v1/team/{team_id}")
        assert response.status_code == 200
        assert response.json()["team_id"] == team_id

@pytest.mark.asyncio
async def test_update_team_name_success():
    async with get_client() as ac:
        # Create a team
        create_resp = await ac.post("/kira/app/api/v1/team/", json=VALID_TEAM_CREATE)
        team_id = create_resp.json()["team_id"]
        # Update name
        new_name = "Updated Team Name"
        response = await ac.patch(f"/kira/app/api/v1/team/{team_id}", json={"new_name": new_name})
        assert response.status_code == 200
        assert response.json()["team_name"] == new_name

@pytest.mark.asyncio
async def test_delete_team_success():
    async with get_client() as ac:
        # Create a team
        create_resp = await ac.post("/kira/app/api/v1/team/", json=VALID_TEAM_CREATE)
        team_id = create_resp.json()["team_id"]
        # Delete
        response = await ac.delete(f"/kira/app/api/v1/team/{team_id}")
        assert response.status_code == 204
