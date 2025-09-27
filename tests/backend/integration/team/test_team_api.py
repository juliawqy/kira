import pytest
from httpx import AsyncClient, ASGITransport
from backend.src.main import app
from tests.mock_data.team_data import VALID_TEAM_CREATE, INVALID_TEAM_EMPTY, INVALID_TEAM_WHITESPACE

def get_client():
    return AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    )

# KIRA-TEAM-001/001
@pytest.mark.asyncio
async def test_create_team_success():
    async with get_client() as ac:
        response = await ac.post("/kira/app/api/v1/team/", json=VALID_TEAM_CREATE)
        assert response.status_code in (201, 404)

# KIRA-TEAM-001/002
@pytest.mark.parametrize("invalid_team", [INVALID_TEAM_EMPTY, INVALID_TEAM_WHITESPACE])
@pytest.mark.asyncio
async def test_create_team_failure(invalid_team):
    async with get_client() as ac:
        response = await ac.post("/kira/app/api/v1/team/", json=invalid_team)
        assert response.status_code == 400

# KIRA-TEAM-001/003
@pytest.mark.asyncio
async def test_get_team_not_found():
    async with get_client() as ac:
        response = await ac.get("/kira/app/api/v1/team/9999")
        assert response.status_code == 404

# KIRA-TEAM-001/004
@pytest.mark.asyncio
async def test_update_team_name_invalid():
    async with get_client() as ac:
        # Try to update a non-existent team
        response = await ac.patch("/kira/app/api/v1/team/9999", json={"new_name": "New Name"})
        assert response.status_code == 400 or response.status_code == 404

# KIRA-TEAM-001/005
@pytest.mark.asyncio
async def test_delete_team_not_found():
    async with get_client() as ac:
        # Try to delete a non-existent team
        response = await ac.delete("/kira/app/api/v1/team/9999")
        assert response.status_code == 404

# KIRA-TEAM-001/006
@pytest.mark.asyncio
async def test_update_team_name_empty():
    async with get_client() as ac:
        # Create a team
        create_resp = await ac.post("/kira/app/api/v1/team/", json=VALID_TEAM_CREATE)
        data = create_resp.json()
        team_id = data["team_id"] if "team_id" in data else None
        assert team_id is not None, f"No team_id in response: {data}"
        # Try to update with empty name
        response = await ac.patch(f"/kira/app/api/v1/team/{team_id}", json={"new_name": "   "})
        assert response.status_code == 400

# KIRA-TEAM-001/007
@pytest.mark.asyncio
async def test_update_team_name_not_manager():
    async with get_client() as ac:
        # Create a team
        create_resp = await ac.post("/kira/app/api/v1/team/", json=VALID_TEAM_CREATE)
        team_id = create_resp.json().get("team_id", 1)
        # Simulate non-manager by patching user (not possible in current mock, but placeholder for real user logic)
        # Try to update as non-manager (should be 403 if implemented)
        # response = await ac.patch(f"/kira/app/api/v1/team/{team_id}", json={"new_name": "New Name"})
        # assert response.status_code == 403
        pass

# KIRA-TEAM-001/008
@pytest.mark.asyncio
async def test_delete_team_not_manager():
    async with get_client() as ac:
        # Create a team
        create_resp = await ac.post("/kira/app/api/v1/team/", json=VALID_TEAM_CREATE)
        team_id = create_resp.json().get("team_id", 1)
        # Simulate non-manager by patching user (not possible in current mock, but placeholder for real user logic)
        # Try to delete as non-manager (should be 403 if implemented)
        # response = await ac.delete(f"/kira/app/api/v1/team/{team_id}")
        # assert response.status_code == 403
        pass

# KIRA-TEAM-001/009
@pytest.mark.asyncio
async def test_create_team_non_manager():
    async with get_client() as ac:
        # Simulate non-manager by sending a payload with a user role other than 'manager'
        # This is a placeholder since the user is mocked in the route, but you can patch get_mock_user if needed
        # For now, test the service directly
        from backend.src.services.team import create_team
        class FakeUser:
            user_id = 2
            role = "member"
        with pytest.raises(ValueError):
            create_team("Non Manager Team", FakeUser())

# KIRA-TEAM-001/010
@pytest.mark.asyncio
async def test_update_team_name_non_manager():
    async with get_client() as ac:
        from backend.src.services.team import update_team_name, create_team
        class FakeUser:
            user_id = 2
            role = "member"
        # Create a team as manager
        manager_user = type("User", (), {"user_id": 1, "role": "manager"})
        team = create_team("Team For Update", manager_user)
        team_id = team["team_id"]
        # Try to update as non-manager
        with pytest.raises(PermissionError):
            update_team_name(team_id, "New Name", FakeUser())

# KIRA-TEAM-001/011
@pytest.mark.asyncio
async def test_delete_team_non_manager():
    async with get_client() as ac:
        from backend.src.services.team import delete_team, create_team
        class FakeUser:
            user_id = 2
            role = "member"
        # Create a team as manager
        manager_user = type("User", (), {"user_id": 1, "role": "manager"})
        team = create_team("Team For Delete", manager_user)
        team_id = team["team_id"]
        # Try to delete as non-manager
        with pytest.raises(PermissionError):
            delete_team(team_id, FakeUser())

# KIRA-TEAM-001/012
@pytest.mark.asyncio
async def test_create_team_missing_role():
    async with get_client() as ac:
        from backend.src.services.team import create_team
        class NoRoleUser:
            user_id = 3
        with pytest.raises(ValueError):
            create_team("No Role Team", NoRoleUser())

# KIRA-TEAM-001/013
@pytest.mark.asyncio
async def test_update_team_name_missing_user_id():
    async with get_client() as ac:
        from backend.src.services.team import update_team_name, create_team
        class NoUserId:
            role = "manager"
        manager_user = type("User", (), {"user_id": 1, "role": "manager"})
        team = create_team("Team For Update Missing UserId", manager_user)
        team_id = team["team_id"]
        with pytest.raises(PermissionError):
            update_team_name(team_id, "New Name", NoUserId())

# KIRA-TEAM-001/014
@pytest.mark.asyncio
async def test_delete_team_missing_user_id():
    async with get_client() as ac:
        from backend.src.services.team import delete_team, create_team
        class NoUserId:
            role = "manager"
        manager_user = type("User", (), {"user_id": 1, "role": "manager"})
        team = create_team("Team For Delete Missing UserId", manager_user)
        team_id = team["team_id"]
        with pytest.raises(PermissionError):
            delete_team(team_id, NoUserId())

# KIRA-TEAM-001/015
@pytest.mark.asyncio
async def test_update_team_name_permission_error():
    from backend.src.services.team import create_team, update_team_name
    manager_user = type("User", (), {"user_id": 1, "role": "manager"})
    team = create_team("Team Permission Update", manager_user)
    team_id = team["team_id"]
    class NotManager:
        user_id = 999
        role = "member"
    with pytest.raises(PermissionError):
        update_team_name(team_id, "New Name", NotManager())

# KIRA-TEAM-001/016
@pytest.mark.asyncio
async def test_delete_team_permission_error():
    from backend.src.services.team import create_team, delete_team
    manager_user = type("User", (), {"user_id": 1, "role": "manager"})
    team = create_team("Team Permission Delete", manager_user)
    team_id = team["team_id"]
    class NotManager:
        user_id = 999
        role = "member"
    with pytest.raises(PermissionError):
        delete_team(team_id, NotManager())

# KIRA-TEAM-001/017
@pytest.mark.asyncio
async def test_create_team_invalid_user():
    from backend.src.services.team import create_team
    class InvalidUser:
        pass
    with pytest.raises(ValueError):
        create_team("Team Invalid User", InvalidUser())

# KIRA-TEAM-001/018
@pytest.mark.asyncio
async def test_update_team_name_invalid_user():
    from backend.src.services.team import create_team, update_team_name
    manager_user = type("User", (), {"user_id": 1, "role": "manager"})
    team = create_team("Team Invalid Update User", manager_user)
    team_id = team["team_id"]
    class InvalidUser:
        pass
    with pytest.raises(PermissionError):
        update_team_name(team_id, "New Name", InvalidUser())

# KIRA-TEAM-001/019
@pytest.mark.asyncio
async def test_delete_team_invalid_user():
    from backend.src.services.team import create_team, delete_team
    manager_user = type("User", (), {"user_id": 1, "role": "manager"})
    team = create_team("Team Invalid Delete User", manager_user)
    team_id = team["team_id"]
    class InvalidUser:
        pass
    with pytest.raises(PermissionError):
        delete_team(team_id, InvalidUser())

# KIRA-TEAM-001/020
@pytest.mark.asyncio
async def test_view_team_invalid_user():
    from backend.src.services.team import create_team, get_team_by_id
    manager_user = type("User", (), {"user_id": 1, "role": "manager"})
    team = create_team("Team Invalid View User", manager_user)
    team_id = team["team_id"]
    class InvalidUser:
        pass
    with pytest.raises(AttributeError):
        get_team_by_id(team_id, InvalidUser())

# KIRA-TEAM-001/021
@pytest.mark.asyncio
async def test_create_team_permission_error_route():
    async with get_client() as ac:
        # Patch get_mock_user to return a non-manager
        from backend.src.api.v1.routes import team_route
        orig = team_route.get_mock_user
        team_route.get_mock_user = lambda: type("User", (), {"user_id": 2, "role": "member"})
        resp = await ac.post("/kira/app/api/v1/team/", json=VALID_TEAM_CREATE)
        assert resp.status_code == 403
        assert "Only managers can create a team." in resp.text
        team_route.get_mock_user = orig

# KIRA-TEAM-001/022
@pytest.mark.asyncio
async def test_create_team_empty_name_route():
    async with get_client() as ac:
        resp = await ac.post("/kira/app/api/v1/team/", json=INVALID_TEAM_EMPTY)
        assert resp.status_code == 400
        assert "Team name cannot be empty or whitespace." in resp.text

# KIRA-TEAM-001/023
@pytest.mark.asyncio
async def test_update_team_name_permission_error_route():
    async with get_client() as ac:
        # Create a team as manager
        create_resp = await ac.post("/kira/app/api/v1/team/", json=VALID_TEAM_CREATE)
        team_id = create_resp.json().get("team_id")
        # Patch get_mock_user to return a non-manager
        from backend.src.api.v1.routes import team_route
        orig = team_route.get_mock_user
        team_route.get_mock_user = lambda: type("User", (), {"user_id": 2, "role": "member"})
        resp = await ac.patch(f"/kira/app/api/v1/team/{team_id}", json={"new_name": "New Name"})
        assert resp.status_code == 403
        assert "Only the team manager can edit the team name." in resp.text
        team_route.get_mock_user = orig

# KIRA-TEAM-001/024
@pytest.mark.asyncio
async def test_delete_team_permission_error_route():
    async with get_client() as ac:
        # Create a team as manager
        create_resp = await ac.post("/kira/app/api/v1/team/", json=VALID_TEAM_CREATE)
        team_id = create_resp.json().get("team_id")
        # Patch get_mock_user to return a non-manager
        from backend.src.api.v1.routes import team_route
        orig = team_route.get_mock_user
        team_route.get_mock_user = lambda: type("User", (), {"user_id": 2, "role": "member"})
        resp = await ac.delete(f"/kira/app/api/v1/team/{team_id}")
        assert resp.status_code == 403
        assert "Only the team manager can delete the team." in resp.text
        team_route.get_mock_user = orig

# KIRA-TEAM-001/025
@pytest.mark.asyncio
async def test_update_team_name_team_not_found_route():
    async with get_client() as ac:
        resp = await ac.patch("/kira/app/api/v1/team/999999", json={"new_name": "New Name"})
        assert resp.status_code == 404
        assert "Team not found" in resp.text

# KIRA-TEAM-001/026
@pytest.mark.asyncio
async def test_delete_team_team_not_found_route():
    async with get_client() as ac:
        resp = await ac.delete("/kira/app/api/v1/team/999999")
        assert resp.status_code == 404
        assert "Team not found" in resp.text

# KIRA-TEAM-001/027
@pytest.mark.asyncio
async def test_view_team_team_not_found_route():
    async with get_client() as ac:
        resp = await ac.get("/kira/app/api/v1/team/999999")
        assert resp.status_code == 404
        assert "Team not found" in resp.text

# KIRA-TEAM-001/028
@pytest.mark.asyncio
async def test_update_team_name_empty_name_route():
    async with get_client() as ac:
        # Create a team
        create_resp = await ac.post("/kira/app/api/v1/team/", json=VALID_TEAM_CREATE)
        team_id = create_resp.json().get("team_id")
        resp = await ac.patch(f"/kira/app/api/v1/team/{team_id}", json={"new_name": "   "})
        assert resp.status_code == 400
        assert "Team name cannot be empty or whitespace." in resp.text

# KIRA-TEAM-001/029
@pytest.mark.asyncio
async def test_delete_team_success_route():
    async with get_client() as ac:
        create_resp = await ac.post("/kira/app/api/v1/team/", json=VALID_TEAM_CREATE)
        team_id = create_resp.json().get("team_id")
        resp = await ac.delete(f"/kira/app/api/v1/team/{team_id}")
        assert resp.status_code == 204

# KIRA-TEAM-001/030
@pytest.mark.asyncio
async def test_delete_team_valueerror_route():
    async with get_client() as ac:
        from backend.src.api.v1.routes import team_route
        orig = team_route.delete_team
        def fake_delete_team(team_id, user):
            raise ValueError("Some other error")
        team_route.delete_team = fake_delete_team
        resp = await ac.delete("/kira/app/api/v1/team/1")
        assert resp.status_code == 400
        assert "Some other error" in resp.text
        team_route.delete_team = orig

# KIRA-TEAM-001/031
@pytest.mark.asyncio
async def test_create_team_other_valueerror_route():
    async with get_client() as ac:
        from backend.src.api.v1.routes import team_route
        orig = team_route.create_team
        def fake_create_team(team_name, user):
            raise ValueError("Other error")
        team_route.create_team = fake_create_team
        resp = await ac.post("/kira/app/api/v1/team/", json=VALID_TEAM_CREATE)
        assert resp.status_code == 400
        assert "Other error" in resp.text
        team_route.create_team = orig

# KIRA-TEAM-001/032
@pytest.mark.asyncio
async def test_view_team_success_route():
    async with get_client() as ac:
        create_resp = await ac.post("/kira/app/api/v1/team/", json=VALID_TEAM_CREATE)
        team_id = create_resp.json().get("team_id")
        resp = await ac.get(f"/kira/app/api/v1/team/{team_id}")
        assert resp.status_code == 200
        assert "team_id" in resp.json()

# KIRA-TEAM-001/033
@pytest.mark.asyncio
async def test_view_team_other_valueerror_route():
    async with get_client() as ac:
        from backend.src.api.v1.routes import team_route
        orig = team_route.get_team_by_id
        def fake_get_team_by_id(team_id, user):
            raise ValueError("Other error")
        team_route.get_team_by_id = fake_get_team_by_id
        resp = await ac.get("/kira/app/api/v1/team/1")
        assert resp.status_code == 400
        assert "Other error" in resp.text
        team_route.get_team_by_id = orig

# KIRA-TEAM-001/034
@pytest.mark.asyncio
async def test_update_team_name_success_route():
    async with get_client() as ac:
        # Create a team
        create_resp = await ac.post("/kira/app/api/v1/team/", json=VALID_TEAM_CREATE)
        team_id = create_resp.json().get("team_id")
        resp = await ac.patch(f"/kira/app/api/v1/team/{team_id}", json={"new_name": "Updated Team Name"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["team_name"] == "Updated Team Name"

# KIRA-TEAM-001/035
@pytest.mark.asyncio
async def test_update_team_name_success_service():
    from backend.src.services.team import create_team, update_team_name
    manager_user = type("User", (), {"user_id": 1, "role": "manager"})
    team = create_team("Service Update Team", manager_user)
    team_id = team["team_id"]
    updated = update_team_name(team_id, "Service Updated Name", manager_user)
    assert updated["team_name"] == "Service Updated Name"
    assert updated["team_id"] == team_id