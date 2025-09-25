
from fastapi import APIRouter, HTTPException
from backend.src.schemas.team import TeamCreate, TeamRead
from backend.src.services.team import create_team, get_team_by_id, delete_team, update_team_name
from fastapi import Body

router = APIRouter(prefix="/team", tags=["team"])

@router.patch("/{team_id}", response_model=TeamRead)
def update_team_name_route(team_id: int, new_name: str = Body(..., embed=True)):
    user = type("User", (), {"user_id": 1, "name": "Test User", "email": "test@example.com", "role": "manager"})
    try:
        team = update_team_name(team_id, new_name, user)
        return team
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{team_id}", status_code=204)
def delete_team_route(team_id: int):
    user = type("User", (), {"user_id": 1, "name": "Test User", "email": "test@example.com", "role": "manager"})
    try:
        delete_team(team_id, user)
        return
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/", status_code=201)
def create_team_route(payload: TeamCreate):
    """Create a team; return the team created."""
    try:
        user = type("User", (), {"user_id": 1, "role": "manager", "name": "Test User", "email": "test@example.com"})
        team = create_team(team_name=payload.team_name, user=user)
        return team
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{team_id}", response_model=TeamRead)
def view_team(team_id: int):
    user = type("User", (), {"user_id": 1, "name": "Test User", "email": "test@example.com", "role": "manager"})
    try:
        team_data = get_team_by_id(team_id, user)
        return team_data
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


