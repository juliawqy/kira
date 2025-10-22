from typing import Optional, Any, Union
from backend.src.database.db_setup import SessionLocal
from backend.src.database.models.team import Team 
from backend.src.database.models.team_assignment import TeamAssignment
from sqlalchemy.exc import IntegrityError


def create_team(team_name: str, user_id, department_id: int, team_number: str) -> dict:
    """Create a team and return it. Only managers can create a team.
    """

    with SessionLocal.begin() as session:
        team_name_clean = team_name.strip()
        team = Team(
            team_name=team_name_clean,
            manager_id=user_id,
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

        assignments = (
            session.query(TeamAssignment).filter_by(team_id=team_id).all()
        )
        assignments_list = [
            {"id": a.id, "team_id": a.team_id, "user_id": a.user_id} for a in assignments
        ]

        return {
            "team_id": team.team_id,
            "team_name": team.team_name,
            "manager_id": team.manager_id,
            "department_id": team.department_id,
            "team_number": team.team_number,
            "assignments": assignments_list,
        }

def get_teams_by_department(department_id: int) -> list[dict]:
    """Return all teams in a given department."""
    with SessionLocal() as session:
        teams = (
            session.query(Team)
            .filter(Team.team_number[3:5] == str(department_id))
            .all()
        )
        result = []
        for team in teams:
            result.append({
                "team_id": team.team_id,
                "team_name": team.team_name,
                "manager_id": team.manager_id,
                "department_id": team.department_id,
                "team_number": team.team_number,
            })
        return result

def get_subteam_by_team_number(team_number: str) -> Optional[dict]:
    with SessionLocal() as session:
        team = (
            session.query(Team)
            .filter(
                Team.team_number[0:8] == team_number
            )
            .first()
        )
        if not team:
            return None
        return {
            "team_id": team.team_id,
            "team_name": team.team_name,
            "manager_id": team.manager_id,
            "department_id": team.department_id,
            "team_number": team.team_number,
        }
    

def assign_to_team(team_id: int, assignee_id: int) -> dict:
    """Assign a user to a team. Only managers and directors allowed."""

    with SessionLocal.begin() as session:
        team = session.get(Team, team_id)
        if not team:
            raise ValueError(f"Team with id {team_id} not found.")

        assignment = TeamAssignment(team_id=team_id, user_id=assignee_id)
        session.add(assignment)
        try:
            session.flush()
            session.refresh(assignment)
        except IntegrityError:
            session.rollback()
            raise ValueError(
                f"User {assignee_id} is already assigned to team {team_id}."
            )
        except Exception as e:
            session.rollback()
            raise ValueError(f"Failed to assign: {str(e)}")

        return {
            "team_id": assignment.team_id,
            "user_id": assignment.user_id,
        }
