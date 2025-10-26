from __future__ import annotations

from typing import Iterable, List

from sqlalchemy import and_, select

from backend.src.database.db_setup import SessionLocal
from backend.src.database.models.task import Task
from backend.src.database.models.user import User
from backend.src.database.models.task_assignment import TaskAssignment
from backend.src.database.models.team import Team
from backend.src.database.models.team_assignment import TeamAssignment
from backend.src.schemas.user import UserRead


# -------------------------- Internal validators -------------------------------

def _ensure_task_active(session, task_id: int) -> Task:
    task = session.get(Task, task_id)
    if not task:
        raise ValueError("Task not found")
    if not bool(task.active):
        raise ValueError("Cannot assign users to an inactive task")
    return task

def _ensure_users_exist(session, user_ids: list[int]) -> list[User]:
    """Ensure all user ids exist (no active/inactive concept)."""
    if not user_ids:
        return []
    users = session.execute(select(User).where(User.user_id.in_(user_ids))).scalars().all()
    found = {u.user_id for u in users}
    missing = [uid for uid in user_ids if uid not in found]
    if missing:
        raise ValueError(f"User(s) not found: {missing}")
    return users


# ------------------------------ Core ops --------------------------------------

def assign_users(task_id: int, user_ids: Iterable[int]) -> int:
    """
    Bulk-assign users to a task (atomic).
    Returns the number of newly created links. Idempotent.
    """
    ids = sorted({int(uid) for uid in (user_ids or [])})
    if not ids:
        return 0

    with SessionLocal.begin() as session:
        _ensure_task_active(session, task_id)
        _ensure_users_exist(session, ids)

        existing = session.execute(
            select(TaskAssignment.user_id).where(
                and_(TaskAssignment.task_id == task_id, TaskAssignment.user_id.in_(ids))
            )
        ).scalars().all()
        existing_set = set(existing)

        to_create = [uid for uid in ids if uid not in existing_set]
        for uid in to_create:
            session.add(TaskAssignment(task_id=task_id, user_id=uid))

        return len(to_create)


def unassign_users(task_id: int, user_ids: list[int]) -> int:
    """Remove multiple assignment links for a task. Returns number of assignments removed."""
    ids = sorted({int(uid) for uid in (user_ids or [])})
    if not ids:
        return 0

    with SessionLocal.begin() as session:
        _ensure_task_active(session, task_id)
        _ensure_users_exist(session, ids)

        links = session.execute(
            select(TaskAssignment).where(
                and_(TaskAssignment.task_id == task_id, TaskAssignment.user_id.in_(ids))
            )
        ).scalars().all()
        
        if not links:
            return 0
            
        for link in links:
            session.delete(link)
            
        return len(links)


def clear_task_assignees(task_id: int) -> int:
    """Remove all assignees from a task. Returns number removed."""
    with SessionLocal.begin() as session:
        _ensure_task_active(session, task_id)
        deleted = session.query(TaskAssignment).filter(
            TaskAssignment.task_id == task_id
        ).delete(synchronize_session=False)
        return int(deleted)


def list_assignees(task_id: int) -> list[UserRead]:
    """Return User rows assigned to the task."""
    with SessionLocal() as session:
        # First check if task exists
        task = session.get(Task, task_id)
        if not task:
            raise ValueError(f"Task with id {task_id} not found")
        
        user_ids = session.execute(
            select(TaskAssignment.user_id).where(TaskAssignment.task_id == task_id)
        ).scalars().all()
        if not user_ids:
            return []
        users = session.execute(select(User).where(User.user_id.in_(user_ids))).scalars().all()
        return [UserRead.model_validate(user) for user in users]


def list_tasks_for_user(
    user_id: int,
    *,
    active_only: bool = True,
) -> list[Task]:
    """
    Return tasks assigned to a user.
    """
    with SessionLocal() as session:
        stmt = (
            select(Task)
            .join(TaskAssignment, TaskAssignment.task_id == Task.id)
            .where(TaskAssignment.user_id == user_id)
        )
        if active_only:
            stmt = stmt.where(Task.active.is_(True))

        return session.execute(stmt).scalars().all()


# ------------------------------ Team Integration Functions ------------------------------

def assign_team_to_task(team_id: int, task_id: int) -> int:
    """
    Assign all team members to a task (atomic).
    Returns the number of newly created task assignments. Idempotent.
    """
    with SessionLocal.begin() as session:
        # Ensure team and task exist
        team = session.get(Team, team_id)
        if not team:
            raise ValueError(f"Team with id {team_id} not found.")
        
        task = _ensure_task_active(session, task_id)

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
        team = session.get(Team, team_id)
        if not team:
            raise ValueError(f"Team with id {team_id} not found.")
        
        task = _ensure_task_active(session, task_id)

        # Get all team members
        team_members = session.execute(
            select(User.user_id).join(TeamAssignment).where(TeamAssignment.team_id == team_id)
        ).scalars().all()
        
        if not team_members:
            return 0

        # Remove task assignments for team members
        assignments = session.execute(
            select(TaskAssignment).where(
                and_(
                    TaskAssignment.task_id == task_id,
                    TaskAssignment.user_id.in_(team_members)
                )
            )
        ).scalars().all()
        
        for assignment in assignments:
            session.delete(assignment)
            
        return len(assignments)


def get_teams_assigned_to_task(task_id: int) -> List[Team]:
    """
    Get all teams that have members assigned to a task.
    """
    with SessionLocal() as session:
        task = session.get(Task, task_id)
        if not task:
            raise ValueError(f"Task with id {task_id} not found.")
        
        teams = session.execute(
            select(Team).distinct()
            .join(TeamAssignment, Team.team_id == TeamAssignment.team_id)
            .join(TaskAssignment, TeamAssignment.user_id == TaskAssignment.user_id)
            .where(TaskAssignment.task_id == task_id)
        ).scalars().all()
        
        return list(teams)


def assign_users_from_teams(task_id: int, team_ids: List[int]) -> int:
    """
    Assign all members from multiple teams to a task (atomic).
    Returns the number of newly created task assignments. Idempotent.
    """
    if not team_ids:
        return 0
        
    team_ids = sorted({int(tid) for tid in team_ids})
    
    with SessionLocal.begin() as session:
        task = _ensure_task_active(session, task_id)
        
        # Ensure all teams exist
        teams = session.execute(
            select(Team).where(Team.team_id.in_(team_ids))
        ).scalars().all()
        
        if len(teams) != len(team_ids):
            found_ids = {t.team_id for t in teams}
            missing_ids = set(team_ids) - found_ids
            raise ValueError(f"Teams not found: {sorted(missing_ids)}")

        # Get all team members from all teams
        team_members = session.execute(
            select(User.user_id).join(TeamAssignment).where(TeamAssignment.team_id.in_(team_ids))
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
