

from fastapi import APIRouter, HTTPException, Body
from backend.src.schemas.team import TeamCreate, TeamRead
from backend.src.services.team import create_team, get_team_by_id, delete_team, update_team_name

router = APIRouter(prefix="/team", tags=["team"])

def get_mock_user():
    """Return a mock manager user object for testing."""
    return type("User", (), {"user_id": 1, "name": "Test User", "email": "test@example.com", "role": "manager"})

@router.patch("/{team_id}", response_model=TeamRead)
def update_team_name_route(team_id: int, new_name: str = Body(..., embed=True)):
    """Update the name of a team if user is manager."""
    user = get_mock_user()
    try:
        team = update_team_name(team_id, new_name, user)
        # Return all fields required by TeamRead
        return {
            "team_id": team["team_id"],
            "team_name": team["team_name"],
            "manager_id": team["manager_id"],
            "user_id": user.user_id,
            "name": getattr(user, "name", "Test User"),
            "email": getattr(user, "email", "test@example.com"),
        }
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        msg = str(e)
        if msg == "Team not found":
            raise HTTPException(status_code=404, detail=msg)
        raise HTTPException(status_code=400, detail=msg)

@router.delete("/{team_id}", status_code=204)
def delete_team_route(team_id: int):
    """Delete a team if user is manager."""
    user = get_mock_user()
    try:
        delete_team(team_id, user)
        return
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        msg = str(e)
        if msg == "Team not found":
            raise HTTPException(status_code=404, detail=msg)
        raise HTTPException(status_code=400, detail=msg)

@router.post("/", status_code=201)
def create_team_route(payload: TeamCreate):
    """Create a team; return the team created."""
    user = get_mock_user()
    try:
        team = create_team(team_name=payload.team_name, user=user)
        return team
    except ValueError as e:
        msg = str(e)
        if msg == "Only managers can create a team.":
            raise HTTPException(status_code=403, detail=msg)
        if msg == "Team name cannot be empty or whitespace.":
            raise HTTPException(status_code=400, detail=msg)
        raise HTTPException(status_code=400, detail=msg)

@router.get("/{team_id}", response_model=TeamRead)
def view_team(team_id: int):
    """View a team by ID."""
    user = get_mock_user()
    try:
        team_data = get_team_by_id(team_id, user)
        return team_data
    except ValueError as e:
        msg = str(e)
        if msg == "Team not found":
            raise HTTPException(status_code=404, detail=msg)
        raise HTTPException(status_code=400, detail=msg)


