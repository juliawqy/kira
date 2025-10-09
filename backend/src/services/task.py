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
from backend.src.database.models.parent_assignment import ParentAssignment
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

def _validate_bucket(n: int) -> None:
    if not isinstance(n, int):
        raise TypeError("priority must be an integer")
    if not (1 <= n <= 10):
        raise ValueError("priority must be between 1 and 10")

# ---- Task CRUD -------------------------------------------------------------------

def add_task(
    title: str,
    *,
    description: Optional[str] = None,
    start_date: Optional[date] = None,
    deadline: Optional[date] = None,
    priority: int = 5,
    status: str = TaskStatus.TO_DO.value,
    project_id: int,
    active: bool = True,
    parent_id: Optional[int] = None,
) -> Optional[Task]:
    """
    Create a task. If parent_id is provided, link this new task as a subtask of that parent.
    Returns the new task created.
    """

    _validate_bucket(priority)

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
    priority: Optional[int] = None,
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
            _validate_bucket(priority)
            task.priority = priority
        if project_id is not None:  task.project_id = project_id
        if active is not None:      task.active = active

        session.add(task)
        session.flush()
        return task

def set_task_status(task_id: int, new_status: str) -> Task:
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

def list_parent_tasks(
    *, 
    active_only: bool = True, 
    project_id: Optional[int] = None,
    sort_by: str = "priority_desc",
    filter_by: Optional[dict] = None
) -> list[Task]:
    """
    Return all top-level tasks (tasks that are not referenced as a subtask),
    with their subtasks eagerly loaded.
    
    Filter options (only one filter type per call):
    - {"priority": 5} - Exact priority
    - {"priority_range": [3, 7]} - Priority range (min, max)
    - {"status": "IN_PROGRESS"} - Exact status
    - {"created_after": date(2024, 1, 1)} - Created after date
    - {"created_before": date(2024, 12, 31)} - Created before date
    - {"due_after": date(2024, 10, 1)} - Due after date
    - {"due_before": date(2024, 10, 31)} - Due before date
    - {"start_after": date(2024, 10, 1)} - Start after date
    - {"start_before": date(2024, 10, 31)} - Start before date
    
    Sort options:
    - "priority_desc" (default): Priority high to low, then deadline closest to furthest
    - "priority_asc": Priority low to high, then deadline closest to furthest  
    - "start_date_asc": Start date oldest to latest, then by priority high to low
    - "start_date_desc": Start date latest to oldest, then by priority high to low
    - "deadline_asc": Deadline oldest to latest, then by priority high to low
    - "deadline_desc": Deadline latest to oldest, then by priority high to low
    - "status": By status, then by priority high to low
    """
    with SessionLocal() as session:
        not_a_subtask = ~exists(
            select(ParentAssignment.subtask_id).where(ParentAssignment.subtask_id == Task.id)
        )
        stmt = (
            select(Task)
            .where(not_a_subtask)
            .options(selectinload(Task.subtask_links).selectinload(ParentAssignment.subtask))
        )
        
        # Apply basic filters
        if active_only:
            stmt = stmt.where(Task.active.is_(True))
        if project_id is not None:
            stmt = stmt.where(Task.project_id == project_id)
            
        # Apply single filter if provided
        if filter_by:
            if "priority" in filter_by:
                stmt = stmt.where(Task.priority == filter_by["priority"])
            elif "priority_range" in filter_by:
                min_p, max_p = filter_by["priority_range"]
                stmt = stmt.where(Task.priority >= min_p, Task.priority <= max_p)
            elif "status" in filter_by:
                stmt = stmt.where(Task.status == filter_by["status"])
            elif "created_after" in filter_by:
                stmt = stmt.where(Task.created_at >= filter_by["created_after"])
            elif "created_before" in filter_by:
                stmt = stmt.where(Task.created_at <= filter_by["created_before"])
            elif "due_after" in filter_by:
                stmt = stmt.where(Task.deadline >= filter_by["due_after"])
            elif "due_before" in filter_by:
                stmt = stmt.where(Task.deadline <= filter_by["due_before"])
            elif "start_after" in filter_by:
                stmt = stmt.where(Task.start_date >= filter_by["start_after"])
            elif "start_before" in filter_by:
                stmt = stmt.where(Task.start_date <= filter_by["start_before"])
            else:
                raise ValueError(f"Invalid filter_by parameter: {filter_by}")
        
        # Apply sorting after filtering
        if sort_by == "priority_desc":
            stmt = stmt.order_by(
                Task.priority.desc(), 
                Task.deadline.is_(None), 
                Task.deadline.asc(), 
                Task.id.asc()
            )
        elif sort_by == "priority_asc":
            stmt = stmt.order_by(
                Task.priority.asc(), 
                Task.deadline.is_(None), 
                Task.deadline.asc(), 
                Task.id.asc()
            )
        elif sort_by == "start_date_asc":
            stmt = stmt.order_by(
                Task.start_date.is_(None), 
                Task.start_date.asc(), 
                Task.priority.desc(), 
                Task.id.asc()
            )
        elif sort_by == "start_date_desc":
            stmt = stmt.order_by(
                Task.start_date.desc(), 
                Task.start_date.is_(None), 
                Task.priority.desc(), 
                Task.id.asc()
            )
        elif sort_by == "deadline_asc":
            stmt = stmt.order_by(
                Task.deadline.is_(None), 
                Task.deadline.asc(), 
                Task.priority.desc(), 
                Task.id.asc()
            )
        elif sort_by == "deadline_desc":
            stmt = stmt.order_by(
                Task.deadline.desc(), 
                Task.deadline.is_(None), 
                Task.priority.desc(), 
                Task.id.asc()
            )
        elif sort_by == "status":
            stmt = stmt.order_by(
                Task.status.asc(), 
                Task.priority.desc(), 
                Task.id.asc()
            )
        else:
            raise ValueError(f"Invalid sort_by parameter: {sort_by}")
        
        return session.execute(stmt).scalars().all()

# Soft Delete
def delete_task(task_id: int, *, detach_links: bool = True) -> Task:
    """
    Soft-delete a task by setting active=False.
    By default, detach all links so archived tasks are not part of any hierarchy.

    Returns the updated Task.
    """
    with SessionLocal.begin() as session:
        task = session.get(Task, task_id)
        if not task:
            raise ValueError("Task not found")

        if task.active is False:
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

# ---- Subtask CRUD -------------------------------------------------------------------

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