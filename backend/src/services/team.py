from typing import Optional, Any, Union, List, Iterable
from backend.src.database.db_setup import SessionLocal
from backend.src.database.models.team import Team 
from backend.src.database.models.team_assignment import TeamAssignment
from backend.src.database.models.user import User
from backend.src.database.models.task import Task
from backend.src.database.models.task_assignment import TaskAssignment
from sqlalchemy import func, select, and_, delete
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

        return {
            "team_id": assignment.team_id,
            "user_id": assignment.user_id,
        }


# ------------------------------ Bulk Team Assignment Operations ------------------------------

def _ensure_team_exists(session, team_id: int) -> Team:
    """Ensure team exists and is active."""
    team = session.get(Team, team_id)
    if not team:
        raise ValueError(f"Team with id {team_id} not found.")
    return team


def _ensure_users_exist(session, user_ids: List[int]) -> List[User]:
    """Ensure all users exist."""
    users = session.execute(
        select(User).where(User.user_id.in_(user_ids))
    ).scalars().all()
    
    if len(users) != len(user_ids):
        found_ids = {u.user_id for u in users}
        missing_ids = set(user_ids) - found_ids
        raise ValueError(f"Users not found: {sorted(missing_ids)}")
    
    return users


def assign_users_to_team(team_id: int, user_ids: Iterable[int]) -> int:
    """
    Bulk-assign users to a team (atomic).
    Returns the number of newly created assignments. Idempotent.
    """
    ids = sorted({int(uid) for uid in (user_ids or [])})
    if not ids:
        return 0

    with SessionLocal.begin() as session:
        _ensure_team_exists(session, team_id)
        _ensure_users_exist(session, ids)

        existing = session.execute(
            select(TeamAssignment.user_id).where(
                and_(TeamAssignment.team_id == team_id, TeamAssignment.user_id.in_(ids))
            )
        ).scalars().all()
        existing_set = set(existing)

        to_create = [uid for uid in ids if uid not in existing_set]
        for uid in to_create:
            session.add(TeamAssignment(team_id=team_id, user_id=uid))

        return len(to_create)


def unassign_users_from_team(team_id: int, user_ids: List[int]) -> int:
    """
    Bulk-unassign users from a team (atomic).
    Returns the number of removed assignments.
    """
    ids = sorted({int(uid) for uid in (user_ids or [])})
    if not ids:
        return 0

    with SessionLocal.begin() as session:
        _ensure_team_exists(session, team_id)

        result = session.execute(
            delete(TeamAssignment).where(
                and_(
                    TeamAssignment.team_id == team_id,
                    TeamAssignment.user_id.in_(ids)
                )
            )
        )
        return result.rowcount


def clear_team_members(team_id: int) -> int:
    """
    Remove all users from a team (atomic).
    Returns the number of removed assignments.
    """
    with SessionLocal.begin() as session:
        _ensure_team_exists(session, team_id)

        result = session.execute(
            delete(TeamAssignment).where(TeamAssignment.team_id == team_id)
        )
        return result.rowcount


def get_team_members(team_id: int) -> List[User]:
    """
    Get all users assigned to a team.
    """
    with SessionLocal() as session:
        _ensure_team_exists(session, team_id)
        
        members = session.execute(
            select(User).join(TeamAssignment).where(TeamAssignment.team_id == team_id)
        ).scalars().all()
        
        return list(members)


# ------------------------------ Team-Task Integration ------------------------------

def assign_team_to_task(team_id: int, task_id: int) -> int:
    """
    Assign all team members to a task (atomic).
    Returns the number of newly created task assignments. Idempotent.
    """
    with SessionLocal.begin() as session:
        # Ensure team and task exist
        team = _ensure_team_exists(session, team_id)
        task = session.get(Task, task_id)
        if not task:
            raise ValueError(f"Task with id {task_id} not found.")
        if not task.active:
            raise ValueError(f"Task {task_id} is not active.")

        # Get all team members
        team_members = session.execute(
            select(User.user_id).join(TeamAssignment).where(TeamAssignment.team_id == team_id)
        ).scalars().all()
        
        if not team_members:
            return 0

        # Check existing task assignments
        existing = session.execute(
            select(TaskAssignment.user_id).where(
                and_(TaskAssignment.task_id == task_id, TaskAssignment.user_id.in_(team_members))
            )
        ).scalars().all()
        existing_set = set(existing)

        # Create new assignments for team members not already assigned
        to_create = [uid for uid in team_members if uid not in existing_set]
        for uid in to_create:
            session.add(TaskAssignment(task_id=task_id, user_id=uid))

        return len(to_create)


def unassign_team_from_task(team_id: int, task_id: int) -> int:
    """
    Unassign all team members from a task (atomic).
    Returns the number of removed task assignments.
    """
    with SessionLocal.begin() as session:
        # Ensure team and task exist
        team = _ensure_team_exists(session, team_id)
        task = session.get(Task, task_id)
        if not task:
            raise ValueError(f"Task with id {task_id} not found.")

        # Get all team members
        team_members = session.execute(
            select(User.user_id).join(TeamAssignment).where(TeamAssignment.team_id == team_id)
        ).scalars().all()
        
        if not team_members:
            return 0

        # Remove task assignments for team members
        result = session.execute(
            delete(TaskAssignment).where(
                and_(
                    TaskAssignment.task_id == task_id,
                    TaskAssignment.user_id.in_(team_members)
                )
            )
        )
        return result.rowcount


def get_teams_for_user(user_id: int) -> List[Team]:
    """
    Get all teams that a user is assigned to.
    """
    with SessionLocal() as session:
        user = session.get(User, user_id)
        if not user:
            raise ValueError(f"User with id {user_id} not found.")
        
        teams = session.execute(
            select(Team).join(TeamAssignment).where(TeamAssignment.user_id == user_id)
        ).scalars().all()
        
        return list(teams)


def list_teams() -> List[dict]:
    """
    List all teams with basic information.
    """
    with SessionLocal() as session:
        teams = session.execute(select(Team)).scalars().all()
        return [
            {
                "team_id": team.team_id,
                "team_name": team.team_name,
                "manager_id": team.manager_id,
                "department_id": team.department_id,
                "team_number": team.team_number,
            }
            for team in teams
        ]
