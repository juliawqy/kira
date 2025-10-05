from typing import Optional, Any, Union
from backend.src.database.db_setup import SessionLocal
from backend.src.database.models.team import Team, TeamAssignment
from backend.src.enums.user_role import UserRole




def create_team(team_name: str, user, department_id: Optional[int] = None, team_number: Optional[int] = None) -> dict:
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

def assign_to_team(team_id: int, assignee_id: int, user) -> dict:
    user_role = getattr(user, "role", None)
    user_id = getattr(user, "user_id", None)
    if not user_role or str(user_role).lower() not in [
        UserRole.MANAGER.value.lower(),
        UserRole.DIRECTOR.value.lower(),
    ]:
        raise ValueError("Only managers and directors can assign to a team.")

    with SessionLocal.begin() as session:
        # Check if the team exists
        team = session.get(Team, team_id)
        if not team:
            raise ValueError(f"Team with id {team_id} not found.")

        # Create the assignment using the TeamAssignment model's user_id
        assignment = TeamAssignment(team_id=team_id, user_id=assignee_id)
        session.add(assignment)
        try:
            session.flush()
        except Exception as e:
            session.rollback()
            raise ValueError(f"Failed to assign: {str(e)}")

        return {
            "team_id": team.team_id,
            "user_id": assignee_id,
            "assigned_by": user_id,
            "status": "assigned",
        }