# backend/src/services/task.py
from __future__ import annotations

from datetime import date, timedelta
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
    **kwargs
) -> Task:
    """
    Update details of a task.

    Return the updated task.

    Use delete_task for setting active=False.
    Use set_task_status for status transitions.
    
    Raises ValueError if 'active' or 'status' fields are included in the update.
    """
    # Check for disallowed fields
    disallowed_fields = {'active', 'status'} & set(kwargs.keys())
    if disallowed_fields:
        raise ValueError(f"Cannot update fields {disallowed_fields}. Use delete_task() for 'active' or set_task_status() for 'status'.")
    
    with SessionLocal.begin() as session:
        task = session.get(Task, task_id)
        if not task:
            raise ValueError("Task not found")

        if title is not None:       task.title = title
        if description is not None: task.description = description
        if start_date is not None:  task.start_date = start_date
        if deadline is not None:    task.deadline = deadline
        if priority is not None:
            _validate_bucket(priority)
            task.priority = priority
        if project_id is not None:  task.project_id = project_id

        session.add(task)
        session.flush()
        return task

def set_task_status(task_id: int, new_status: str) -> Task:
    """
    update the status of a task.

    If marking a recurring task as "Completed",
    automatically create the next occurrence with the same details and new deadline = old_deadline + recurring 

    Returns the updated Task.

    Raise ValueError if deadline is not set for a recurring Task.
    """
    if new_status not in ALLOWED_STATUSES:
        raise ValueError(f"Invalid status '{new_status}'")
    with SessionLocal.begin() as session:
        task = session.get(Task, task_id)
        if not task:
            raise ValueError("Task not found")

        recurring = int(getattr(task, "recurring", 0) or 0)

        if new_status == TaskStatus.COMPLETED.value and recurring > 0:
            if task.deadline:
                next_deadline = task.deadline + timedelta(days=task.recurring)
            else:
                raise ValueError("Cannot create next occurrence of recurring task without a deadline")

            new_task = Task(
                title = task.title,
                description = task.description,
                start_date = task.deadline,
                deadline = next_deadline,
                status = TaskStatus.TO_DO.value,
                priority = task.priority,
                recurring = task.recurring,
                project_id = task.project_id,
                active = True,
            )

            session.add(new_task)
            session.flush()
        
        task.status = new_status
        session.add(task)
        session.flush()
        
        return task

def list_tasks(
    *, 
    active_only: bool = True, 
    project_id: Optional[int] = None,
    sort_by: str = "priority_desc",
    filter_by: Optional[dict] = None
) -> list[Task]:
    """
    Return all top-level tasks (tasks that are not referenced as a subtask),
    with their subtasks eagerly loaded.
    
    Filter options:
    - {"priority_range": [3, 7]} - Priority range (min, max)
    - {"status": "IN_PROGRESS"} - Exact status 
    - {"deadline_range": [date(2024, 10, 1), date(2024, 10, 31)]} - Due date range
    - {"start_date_range": [date(2024, 10, 1), date(2024, 10, 31)]} - Start date range
    
    Note: Date ranges (deadline_range, start_date_range) can be combined together.
    Other filters (priority_range, status) are mutually exclusive with all others.
    
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
            
        # Apply filters if provided
        if filter_by:
            # Validate filter combinations
            date_filters = set(filter_by.keys()) & {"deadline_range", "start_date_range"}
            non_date_filters = set(filter_by.keys()) & {"priority_range", "status"}
            
            # Date filters can be combined with each other, but not with non-date filters
            if len(non_date_filters) > 1:
                raise ValueError(f"Only one non-date filter allowed. Found: {list(non_date_filters)}")
            if len(non_date_filters) >= 1 and len(date_filters) >= 1:
                raise ValueError(f"Date filters cannot be combined with other filter types. Found date filters: {list(date_filters)}, other filters: {list(non_date_filters)}")
            
            # Apply filters
            if "priority_range" in filter_by:
                min_p, max_p = filter_by["priority_range"]
                stmt = stmt.where(Task.priority >= min_p, Task.priority <= max_p)
            
            if "status" in filter_by:
                stmt = stmt.where(Task.status == filter_by["status"])
                
            if "deadline_range" in filter_by:
                start_date, end_date = filter_by["deadline_range"]
                stmt = stmt.where(Task.deadline >= start_date, Task.deadline <= end_date)
                
            if "start_date_range" in filter_by:
                start_date, end_date = filter_by["start_date_range"]
                stmt = stmt.where(Task.start_date >= start_date, Task.start_date <= end_date)
        
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
                Task.status.desc(), # reverse alphabetical order gives to-do first and blocked last
                Task.priority.desc(), 
                Task.id.asc()
            )
        else:
            raise ValueError(f"Invalid sort_by parameter: {sort_by}")
        
        return session.execute(stmt).scalars().all()

def list_tasks_by_project(project_id: int, *, active_only: bool = True) -> list[Task]:
    """
    Only returns tasks that are not subtasks of other tasks (top-level hierarchy).
    """
    with SessionLocal() as session:
        # Only return parent tasks (not subtasks) for this project
        not_a_subtask = ~exists(
            select(ParentAssignment.subtask_id).where(ParentAssignment.subtask_id == Task.id)
        )
        stmt = (
            select(Task)
            .where(not_a_subtask)
            .where(Task.project_id == project_id)
            .options(selectinload(Task.subtask_links).selectinload(ParentAssignment.subtask))
        )
        
        if active_only:
            stmt = stmt.where(Task.active.is_(True))
        
        tasks = session.execute(stmt).scalars().all()
        return tasks

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
    
    Filter options:
    - {"priority_range": [3, 7]} - Priority range (min, max)
    - {"status": "IN_PROGRESS"} - Exact status 
    - {"deadline_range": [date(2024, 10, 1), date(2024, 10, 31)]} - Due date range
    - {"start_date_range": [date(2024, 10, 1), date(2024, 10, 31)]} - Start date range
    
    Note: Date ranges (deadline_range, start_date_range) can be combined together.
    Other filters (priority_range, status) are mutually exclusive with all others.
    
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
        )
        
        # Apply basic filters
        if active_only:
            stmt = stmt.where(Task.active.is_(True))
        if project_id is not None:
            stmt = stmt.where(Task.project_id == project_id)
            
        # Apply filters if provided
        if filter_by:
            # Validate filter combinations
            date_filters = set(filter_by.keys()) & {"deadline_range", "start_date_range"}
            non_date_filters = set(filter_by.keys()) & {"priority_range", "status"}
            
            # Date filters can be combined with each other, but not with non-date filters
            if len(non_date_filters) > 1:
                raise ValueError(f"Only one non-date filter allowed. Found: {list(non_date_filters)}")
            if len(non_date_filters) >= 1 and len(date_filters) >= 1:
                raise ValueError(f"Date filters cannot be combined with other filter types. Found date filters: {list(date_filters)}, other filters: {list(non_date_filters)}")
            
            # Apply filters
            if "priority_range" in filter_by:
                min_p, max_p = filter_by["priority_range"]
                stmt = stmt.where(Task.priority >= min_p, Task.priority <= max_p)
            
            if "status" in filter_by:
                stmt = stmt.where(Task.status == filter_by["status"])
                
            if "deadline_range" in filter_by:
                start_date, end_date = filter_by["deadline_range"]
                stmt = stmt.where(Task.deadline >= start_date, Task.deadline <= end_date)
                
            if "start_date_range" in filter_by:
                start_date, end_date = filter_by["start_date_range"]
                stmt = stmt.where(Task.start_date >= start_date, Task.start_date <= end_date)
        
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
                Task.status.desc(), # reverse alphabetical order gives to-do first and blocked last
                Task.priority.desc(), 
                Task.id.asc()
            )
        else:
            raise ValueError(f"Invalid sort_by parameter: {sort_by}")
        
        return session.execute(stmt).scalars().all()

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
    Return a task with its active subtasks
    """
    if not isinstance(task_id, int):
        raise TypeError(f"task_id must be an integer, got {type(task_id).__name__}")
    
    with SessionLocal() as session:
        stmt = (
            select(Task)
            .where(Task.id == task_id)
            .options(
                # load link rows and their active subtask Task objects
                selectinload(Task.subtask_links).selectinload(ParentAssignment.subtask.and_(Task.active.is_(True)))
            )
        )
        return session.execute(stmt).scalar_one_or_none()