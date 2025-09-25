from typing import Optional
from backend.src.database.db_setup import SessionLocal
from backend.src.database.models.team import Team
from backend.src.enums.user_role import UserRole


def create_team(team_name: str, user, department_id: int, team_number: int) -> dict:
    """Create a team and return it. Only managers can create a team.
    """
    # normalize and check against UserRole enum
    user_role = getattr(user, "role", None)
    if not user_role or str(user_role).lower() != UserRole.MANAGER.value.lower():
        raise ValueError("Only managers can create a team.")
    if not team_name or not team_name.strip():
        raise ValueError("Team name cannot be empty or whitespace.")
    with SessionLocal.begin() as session:
        team_name_clean = team_name.strip()
        team = Team(
            team_name=team_name_clean,
            manager_id=user.user_id,
            department_id=department_id,
            team_number=team_number,
        )
        session.add(team)
        session.flush()
        session.refresh(team)
        return {
            "team_id": team.team_id,
            "team_name": team.team_name,
            "manager_id": team.manager_id,
            "department_id": team.department_id,
            "team_number": team.team_number,
        }


def get_team_by_id(team_id: int) -> dict:
    """Return team details by id. Raises ValueError if not found."""
    with SessionLocal() as session:
        team = session.get(Team, team_id)
        if not team:
            raise ValueError("Team not found")
        return {
            "team_id": team.team_id,
            "team_name": team.team_name,
            "manager_id": team.manager_id,
            "department_id": team.department_id,
            "team_number": team.team_number,
        }
