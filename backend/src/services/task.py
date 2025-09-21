from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Optional, Iterable

from sqlalchemy import nulls_last, select
from sqlalchemy.orm import selectinload

from database.db_setup import SessionLocal
from database.models.task import Task


# ---- Status --------------------------------------------------------------

class TaskStatus(str, Enum):
    TODO = "To-do"
    IN_PROGRESS = "In-progress"
    COMPLETED = "Completed"

ALLOWED_STATUSES = {s.value for s in TaskStatus}


def _normalize_members(members: Optional[Iterable[str]]) -> list[str]:
    """Strip, dedupe, sort collaborator names."""
    if not members:
        return []
    cleaned = {m.strip() for m in members if m and m.strip()}
    return sorted(cleaned)

def _csv_to_list(csv: Optional[str]) -> list[str]:
    return _normalize_members(csv.split(",")) if csv else []

def _list_to_csv(members: Iterable[str]) -> str:
    return ",".join(_normalize_members(members))


def add_task(
    title: str,
    description: Optional[str],
    start_date: Optional[date],
    deadline: Optional[date],
    priority: str = "Medium",
    status: str = TaskStatus.TODO.value,
    collaborators: Optional[str] = None,
    notes: Optional[str] = None,
    parent_id: Optional[int] = None,
) -> Task:
    """Create a task and return it."""
    collaborators_csv = _list_to_csv(_csv_to_list(collaborators))
    with SessionLocal.begin() as session:
        task = Task(
            title=title,
            description=description,
            start_date=start_date,
            deadline=deadline,
            priority=priority,
            status=status,
            collaborators=collaborators_csv,
            notes=notes,
            parent_id=parent_id,
        )
        session.add(task)
        session.flush()
        session.refresh(task)
        return task


def get_task_with_subtasks(task_id: int):
    with SessionLocal() as session:
        stmt = (
            select(Task)
            .where(Task.id == task_id)
            .options(selectinload(Task.subtasks))
        )
        return session.execute(stmt).scalar_one_or_none()

def list_parent_tasks():
    with SessionLocal() as session:
        stmt = (
            select(Task)
            .where(Task.parent_id.is_(None))
            .options(selectinload(Task.subtasks))
            .order_by(nulls_last(Task.deadline.asc()), Task.id.asc())
        )
        return session.execute(stmt).scalars().all()


def update_task(
    task_id: int,
    *,
    title: Optional[str] = None,
    description: Optional[str] = None,
    start_date: Optional[date] = None,
    deadline: Optional[date] = None,
    priority: Optional[str] = None,
    # status intentionally excluded
    collaborators: Optional[str] = None,
    notes: Optional[str] = None,
    parent_id: Optional[int] = None,
) -> Optional[Task]:
    """Update non-status fields; return updated task or None."""
    with SessionLocal.begin() as session:
        task = session.get(Task, task_id)
        if task is None:
            return None

        if title is not None:
            task.title = title
        if description is not None:
            task.description = description
        if start_date is not None:
            task.start_date = start_date
        if deadline is not None:
            task.deadline = deadline
        if priority is not None:
            task.priority = priority
        if collaborators is not None:
            task.collaborators = _list_to_csv(_csv_to_list(collaborators))
        if notes is not None:
            task.notes = notes
        if parent_id is not None:
            task.parent_id = parent_id

        session.add(task)
        session.flush()
        session.refresh(task)
        return task


def update_task_status(task_id: int, new_status: str) -> Task:
    """Set status and return updated task."""
    if new_status not in ALLOWED_STATUSES:
        raise ValueError(f"Invalid status '{new_status}'. Allowed: {sorted(ALLOWED_STATUSES)}")

    with SessionLocal.begin() as session:
        task = session.get(Task, task_id)
        if not task:
            raise ValueError(f"Task id {task_id} not found")
        task.status = new_status
        session.add(task)
        session.flush()
        session.refresh(task)
        return task


def start_task(task_id: int) -> Task:
    """Mark task as In progress."""
    return update_task_status(task_id, TaskStatus.IN_PROGRESS.value)


def complete_task(task_id: int) -> Task:
    """Mark task as Completed (single task)."""
    return update_task_status(task_id, TaskStatus.COMPLETED.value)


def mark_blocked(task_id: int) -> Task:
    """Mark task as Blocked."""
    return update_task_status(task_id, TaskStatus.BLOCKED.value)


def assign_task(task_id: int, new_members: list[str]) -> Task:
    """Assign collaborators and return updated task."""
    with SessionLocal.begin() as session:
        task = session.get(Task, task_id)
        if not task:
            raise ValueError("Task not found")

        existing = _csv_to_list(task.collaborators)
        updated = _normalize_members([*existing, *new_members])
        task.collaborators = _list_to_csv(updated)

        session.add(task)
        session.flush()
        session.refresh(task)
        return task


def unassign_task(task_id: int, members_to_remove: list[str]) -> Task:
    """Unassign collaborators and return updated task."""
    with SessionLocal.begin() as session:
        task = session.get(Task, task_id)
        if not task:
            raise ValueError("Task not found")

        existing = set(_csv_to_list(task.collaborators))
        updated = sorted(existing - set(_normalize_members(members_to_remove)))
        task.collaborators = _list_to_csv(updated) if updated else None

        session.add(task)
        session.flush()
        session.refresh(task)
        return task


# ---- Deletes --------------------------------------------------------------

def delete_subtask(subtask_id: int) -> bool:
    """Delete a subtask; return True if deleted, False if not found."""
    with SessionLocal.begin() as session:
        sub = session.get(Task, subtask_id)
        if sub is None:
            return False
        if sub.parent_id is None:
            raise ValueError(f"Task {subtask_id} is not a subtask (no parent). Use delete_task().")
        session.delete(sub)
        return True


def delete_task(task_id: int) -> dict:
    """Delete a task and detach its subtasks; return {'deleted': id, 'subtasks_detached': n}."""
    with SessionLocal.begin() as session:
        task = session.get(Task, task_id)
        if task is None:
            raise ValueError(f"Task id {task_id} not found")

        detached = 0
        if hasattr(task, "subtasks"):
            for st in list(task.subtasks):
                st.parent_id = None
                detached += 1
        else:
            subs = session.execute(select(Task).where(Task.parent_id == task_id)).scalars().all()
            for st in subs:
                st.parent_id = None
                detached += 1

        session.flush()
        session.delete(task)
        return {"deleted": task_id, "subtasks_detached": detached}
