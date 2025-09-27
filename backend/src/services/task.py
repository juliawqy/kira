# backend/src/services/task.py
from __future__ import annotations

from datetime import date
from enum import Enum
from operator import and_
from token import OP
from typing import Iterable, Optional

from sqlalchemy import select, exists
from sqlalchemy.orm import selectinload

from backend.src.database.db_setup import SessionLocal
from backend.src.database.models.task import Task
from database.models.parent_assignment import ParentAssignment
from backend.src.enums.task_priority import TaskPriority
from backend.src.enums.task_status import TaskStatus, ALLOWED_STATUSES


# ---- Helpers ----------------------------------------------------------------
def _assert_no_cycle(session, parent_id: int, child_id: int) -> None:
    """
    Prevent cycles: parent must not be a descendant of child.
    Lightweight BFS over the association table.
    """
    to_visit = [child_id]
    seen = set()
    while to_visit:
        cur = to_visit.pop()
        if cur in seen:
            continue  # pragma: no cover  (defensive; single-parent invariant prevents revisits)
        seen.add(cur)
        rows = session.execute(
            select(ParentAssignment.subtask_id).where(ParentAssignment.parent_id == cur)
        ).scalars().all()
        if parent_id in rows:
            raise ValueError("Cycle detected: the chosen parent is a descendant of the subtask.")
        to_visit.extend(rows)


# ---- CRUD -------------------------------------------------------------------

def add_task(
    title: str,
    description: Optional[str],
    start_date: Optional[date],
    deadline: Optional[date],
    *,
    priority: str = TaskPriority.MEDIUM.value,
    status: str = TaskStatus.TO_DO.value,
    project_id: Optional[int] = None,
    active: bool = True,
    parent_id: Optional[int] = None,
) -> Optional[Task]:
    """
    Create a task. If parent_id is provided, link this new task as a subtask of that parent.
    Returns the new task created.
    """
    if priority not in ALLOWED_PRIORITIES:
        raise ValueError(f"Invalid priority '{priority}'")
    if status not in ALLOWED_STATUSES:
        raise ValueError(f"Invalid status '{status}'")

    with SessionLocal.begin() as session:
        task = Task(
            title=title,
            description=description,
            start_date=start_date,
            deadline=deadline,
            status=status,
            priority=priority,
            project_id=project_id,
            active=active,
        )
        session.add(task)
        session.flush()  

        if parent_id is not None:
            if parent_id == task.id: # pragma: no cover - cannot happen for a brand-new task
                raise ValueError("A task cannot be its own parent.") # pragma: no cover
            parent = session.get(Task, parent_id)
            if not parent:
                raise ValueError(f"Parent task {parent_id} not found.")
            
            if not parent.active:
                raise ValueError(f"Parent task {parent_id} is inactive and cannot accept subtasks.")

            _assert_no_cycle(session, parent_id=parent_id, child_id=task.id)

            session.add(ParentAssignment(parent_id=parent_id, subtask_id=task.id))

        return task

def update_task(
    task_id: int,
    *,
    title: Optional[str] = None,
    description: Optional[str] = None,
    start_date: Optional[date] = None,
    deadline: Optional[date] = None,
    priority: Optional[str] = None,
    project_id: Optional[int] = None,
    active: Optional[bool] = None,
) -> Optional[Task]:
    """
    Update details of a task.

    Return the updated task.

    Use start_task/complete_task/block_task for status transitions.

    """
    with SessionLocal.begin() as session:
        task = session.get(Task, task_id)
        if not task:
            return None

        if title is not None:       task.title = title
        if description is not None: task.description = description
        if start_date is not None:  task.start_date = start_date
        if deadline is not None:    task.deadline = deadline
        if priority is not None:
            if priority not in ALLOWED_PRIORITIES:
                raise ValueError(f"Invalid priority '{priority}'")
            task.priority = priority
        if project_id is not None:  task.project_id = project_id
        if active is not None:      task.active = active

        session.add(task)
        session.flush()
        return task

def attach_subtasks(parent_id: int, subtask_ids: Iterable[int]) -> Task:
    """
    Attach one or more subtasks to a parent in a single transaction (all-or-nothing).
    - Parent must exist and be active.
    - Each subtask must exist and be active.
    - Enforces single-parent rule; idempotent if a subtask is already linked to the same parent.
    - Guards against cycles.
    Returns the parent Task with subtasks eagerly loaded.
    """
    # Normalize & dedupe ids
    ids = sorted({int(sid) for sid in subtask_ids or []})
    with SessionLocal.begin() as session:
        # Validate parent
        parent = session.get(Task, parent_id)
        if not parent:
            raise ValueError(f"Parent task {parent_id} not found")
        if not parent.active:
            raise ValueError(f"Parent task {parent_id} is inactive and cannot accept subtasks")

        if not ids:
            # Nothing to do; return hydrated parent
            return session.execute(
                select(Task)
                .where(Task.id == parent_id)
                .options(selectinload(Task.subtask_links).selectinload(ParentAssignment.subtask))
            ).scalar_one()

        if parent_id in ids:
            raise ValueError("A task cannot be its own parent")

        # Fetch subtask rows
        sub_rows = session.execute(
            select(Task).where(Task.id.in_(ids))
        ).scalars().all()
        found = {t.id for t in sub_rows}
        missing = [sid for sid in ids if sid not in found]
        if missing:
            raise ValueError(f"Subtask(s) not found: {missing}")

        inactive = [t.id for t in sub_rows if not t.active]
        if inactive:
            raise ValueError(f"Subtask(s) inactive: {inactive}")

        # Check existing links for these subtasks
        existing_links = session.execute(
            select(ParentAssignment).where(ParentAssignment.subtask_id.in_(ids))
        ).scalars().all()

        # Conflicts: already owned by a different parent
        conflicts = [lnk.subtask_id for lnk in existing_links if lnk.parent_id != parent_id]
        if conflicts:
            raise ValueError(f"Task(s) already have a parent: {conflicts}")

        # Cycle guard for each subtask
        for st in sub_rows:
            _assert_no_cycle(session, parent_id=parent_id, child_id=st.id)

        # Create links for those not already linked to this parent (idempotent)
        already = {lnk.subtask_id for lnk in existing_links if lnk.parent_id == parent_id}
        to_link = [sid for sid in ids if sid not in already]
        for sid in to_link:
            session.add(ParentAssignment(parent_id=parent_id, subtask_id=sid))

        session.flush()

        # Return hydrated parent with subtasks loaded (avoid lazy-load after commit)
        parent = session.execute(
            select(Task)
            .where(Task.id == parent_id)
            .options(selectinload(Task.subtask_links).selectinload(ParentAssignment.subtask))
        ).scalar_one()
        return parent


def detach_subtask(parent_id: int, subtask_id: int) -> bool:
    """
    Detach a single subtask from a parent.
    - Raises ValueError if the link does not exist.
    Returns True when detached.
    """
    with SessionLocal.begin() as session:
        link = session.execute(
            select(ParentAssignment).where(
                and_(
                    ParentAssignment.parent_id == parent_id,
                    ParentAssignment.subtask_id == subtask_id,
                )
            )
        ).scalar_one_or_none()
        if not link:
            raise ValueError(f"Link not found for parent={parent_id}, subtask={subtask_id}")

        session.delete(link)
        return True


# ---- Status transitions -----------------------------------------------------

def _set_status(task_id: int, new_status: str) -> Task:
    if new_status not in ALLOWED_STATUSES:
        raise ValueError(f"Invalid status '{new_status}'")
    with SessionLocal.begin() as session:
        task = session.get(Task, task_id)
        if not task:
            raise ValueError("Task not found")
        task.status = new_status
        session.add(task)
        session.flush()
        return task

def start_task(task_id: int) -> Task:
    """Set status -> In-progress."""
    return _set_status(task_id, TaskStatus.IN_PROGRESS.value)

def complete_task(task_id: int) -> Task:
    """Set status -> Completed (single task)."""
    return _set_status(task_id, TaskStatus.COMPLETED.value)

def block_task(task_id: int) -> Task:
    """Set status -> Blocked."""
    return _set_status(task_id, TaskStatus.BLOCKED.value)

# In case, we need this in the future
# def complete_task_with_cascade(task_id: int) -> Task:
#     """
#     Set the task to Completed; if it has subtasks, complete all of them
#     in the same transaction.
#     """
#     with SessionLocal.begin() as session:
#         task = session.get(Task, task_id)
#         if not task:
#             raise ValueError("Task not found")
#         task.status = TaskStatus.COMPLETED.value
#         # iterate over association-proxied list (loads lazily inside tx if needed)
#         for st in task.subtasks:
#             st.status = TaskStatus.COMPLETED.value
#             session.add(st)
#         session.add(task)
#         session.flush()
#         return task

def get_task_with_subtasks(task_id: int) -> Optional[Task]:
    """
    Return a task with its subtasks
    """
    with SessionLocal() as session:
        stmt = (
            select(Task)
            .where(Task.id == task_id)
            .options(
                # load link rows and their subtask Task objects
                selectinload(Task.subtask_links).selectinload(ParentAssignment.subtask)
            )
        )
        return session.execute(stmt).scalar_one_or_none()


def list_parent_tasks(*, active_only: bool = True, project_id: Optional[int] = None) -> list[Task]:
    """
    Return all top-level tasks (tasks that are not referenced as a subtask),
    with their subtasks eagerly loaded. Ordered by deadline (nulls last), then id.
    """
    with SessionLocal() as session:
        # correlated NOT EXISTS: task.id not present as a subtask_id in parent_assignment
        not_a_subtask = ~exists(
            select(ParentAssignment.subtask_id).where(ParentAssignment.subtask_id == Task.id)
        )
        stmt = (
            select(Task)
            .where(not_a_subtask)
            .options(selectinload(Task.subtask_links).selectinload(ParentAssignment.subtask))
            .order_by(Task.deadline.is_(None), Task.deadline.asc(), Task.id.asc())
        )
        if active_only:
            stmt = stmt.where(Task.active.is_(True))
        if project_id is not None:
            stmt = stmt.where(Task.project_id == project_id)
        return session.execute(stmt).scalars().all()


# ---- Soft-Deletion ---------------------------------------------------------------
def archive_task(task_id: int, *, detach_links: bool = True) -> Task:
    """
    Soft-delete a task by setting active=False.
    By default, detach all links so archived tasks are not part of any hierarchy.

    Returns the updated Task.
    """
    with SessionLocal.begin() as session:
        task = session.get(Task, task_id)
        if not task:
            raise ValueError("Task not found")

        if detach_links:
            # Remove links where this task is parent or subtask
            session.query(ParentAssignment).filter(
                ParentAssignment.parent_id == task_id
            ).delete()
            session.query(ParentAssignment).filter(
                ParentAssignment.subtask_id == task_id
            ).delete()

        task.active = False
        session.add(task)
        session.flush()
        return task


def restore_task(task_id: int) -> Task:
    """
    Restore a previously archived task by setting active=True.
    Note: does not reattach any previous parent/subtask links.
    Use attach_subtask(...) if you need to re-parent after restoring.
    """
    with SessionLocal.begin() as session:
        task = session.get(Task, task_id)
        if not task:
            raise ValueError("Task not found")
        task.active = True
        session.add(task)
        session.flush()
        return task
