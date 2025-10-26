from typing import Optional, Any, Union
from backend.src.database.db_setup import SessionLocal
from backend.src.database.models.team import Team 
from backend.src.database.models.team_assignment import TeamAssignment
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError


def create_team(team_name: str, user_id, department_id: int, prefix: str) -> dict:
    """Create a team and return it. Only managers can create a team.
    """

    with SessionLocal() as session:
        team_name_clean = team_name.strip()
        team = Team(
            team_name=team_name_clean,
            manager_id=user_id,
            department_id=department_id,
            team_number=str(prefix),
        )
        session.add(team)
        session.flush()                
        session.refresh(team)          
        
        team_number = f"{str(prefix).zfill(2)}{str(team.team_id).zfill(2)}".ljust(6, "0")
        team.team_number = team_number
        
        session.commit()             
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
            return None

        assignments = (
            session.query(TeamAssignment).filter_by(team_id=team_id).all()
        )
        assignments_list = [
            {"team_id": a.team_id, "user_id": a.user_id} for a in assignments
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
            .filter(func.substr(Team.team_number, 1, 2) == str(department_id).zfill(2))
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

def get_subteam_by_team_number(team_number: str) -> list[dict]:
    """Return all subteams under a given team number prefix."""
    prefix = team_number[:4]
    with SessionLocal() as session:
        subteams = (
            session.query(Team)
            .filter(func.substr(Team.team_number, 1, 4) == prefix)
            .filter(Team.team_number != team_number)
            .all()
        )
        if not subteams:
            return []

        return [
            {
                "team_id": t.team_id,
                "team_name": t.team_name,
                "manager_id": t.manager_id,
                "department_id": t.department_id,
                "team_number": t.team_number,
            }
            for t in subteams
        ]
    
def assign_to_team(team_id: int, assignee_id: int) -> dict:
    """Assign a user to a team. Only managers and directors allowed."""

    with SessionLocal.begin() as session:

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

        return {
            "team_id": assignment.team_id,
            "user_id": assignment.user_id,
        }

def get_users_in_team(team_id: int) -> list[dict]:
    """Return all users assigned to a given team."""
    with SessionLocal() as session:
        assignments = (
            session.query(TeamAssignment).filter_by(team_id=team_id).all()
        )
        user_ids = [a.user_id for a in assignments]
        users = []
        for uid in user_ids:
            users.append({"user_id": uid})
        return users
    
def get_teams_of_user(user_id: int) -> list[dict]:
    """Return all teams a user is assigned to."""
    with SessionLocal() as session:
        assignments = (
            session.query(TeamAssignment).filter_by(user_id=user_id).all()
        )
        team_ids = [a.team_id for a in assignments]
        teams = []
        for tid in team_ids:
            team = session.get(Team, tid)
            teams.append({
                "team_id": team.team_id,
                "team_name": team.team_name,
                "manager_id": team.manager_id,
                "department_id": team.department_id,
                "team_number": team.team_number,
            })
        return teams
    
def get_team_by_manager(manager_id: int) -> list[dict]:
    """Return all teams managed by a given user."""
    with SessionLocal() as session:
        teams = (
            session.query(Team).filter_by(manager_id=manager_id).all()
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