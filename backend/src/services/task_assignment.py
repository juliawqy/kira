from __future__ import annotations

from typing import Iterable

from sqlalchemy import and_, select

from backend.src.database.db_setup import SessionLocal
from backend.src.database.models.task import Task
from backend.src.database.models.user import User
from backend.src.database.models.task_assignment import TaskAssignment


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
    users = session.execute(select(User).where(User.id.in_(user_ids))).scalars().all()
    found = {u.id for u in users}
    missing = [uid for uid in user_ids if uid not in found]
    if missing:
        raise ValueError(f"User(s) not found: {missing}")
    return users


# ------------------------------ Core ops --------------------------------------

def assign_user(task_id: int, user_id: int) -> bool:
    """
    Assign a single user to a task.
    Idempotent: returns False if the link already exists; True if created.
    """
    with SessionLocal.begin() as session:
        _ensure_task_active(session, task_id)
        _ensure_users_exist(session, [user_id])

        exists_link = session.execute(
            select(TaskAssignment).where(
                and_(TaskAssignment.task_id == task_id, TaskAssignment.user_id == user_id)
            )
        ).scalar_one_or_none()

        if exists_link:
            return False

        session.add(TaskAssignment(task_id=task_id, user_id=user_id))
        return True


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


def unassign_user(task_id: int, user_id: int) -> bool:
    """Remove a single assignment link. Raises if the link does not exist."""
    with SessionLocal.begin() as session:
        link = session.execute(
            select(TaskAssignment).where(
                and_(TaskAssignment.task_id == task_id, TaskAssignment.user_id == user_id)
            )
        ).scalar_one_or_none()
        if not link:
            raise ValueError("Assignment not found")
        session.delete(link)
        return True


def clear_task_assignees(task_id: int) -> int:
    """Remove all assignees from a task. Returns number removed."""
    with SessionLocal.begin() as session:
        _ensure_task_active(session, task_id)
        deleted = session.query(TaskAssignment).filter(
            TaskAssignment.task_id == task_id
        ).delete(synchronize_session=False)
        return int(deleted)


# ------------------------------ Queries ---------------------------------------

def is_assigned(task_id: int, user_id: int) -> bool:
    with SessionLocal() as session:
        link = session.execute(
            select(TaskAssignment.user_id).where(
                and_(TaskAssignment.task_id == task_id, TaskAssignment.user_id == user_id)
            )
        ).scalar_one_or_none()
        return link is not None


def count_assignees(task_id: int) -> int:
    with SessionLocal() as session:
        return len(
            session.execute(
                select(TaskAssignment.user_id).where(TaskAssignment.task_id == task_id)
            ).scalars().all()
        )


def list_assignees(task_id: int) -> list[User]:
    """Return User rows assigned to the task."""
    with SessionLocal() as session:
        user_ids = session.execute(
            select(TaskAssignment.user_id).where(TaskAssignment.task_id == task_id)
        ).scalars().all()
        if not user_ids:
            return []
        return session.execute(select(User).where(User.id.in_(user_ids))).scalars().all()


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
