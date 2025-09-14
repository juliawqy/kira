from sqlalchemy import select
from sqlalchemy.orm import joinedload
from typing import Optional
from db.db_setup import SessionLocal
from models.task import Task
from datetime import date

ALLOWED_STATUSES = {"To-do", "In progress", "Completed", "Blocked"}

def add_task(title, description, start_date, deadline,
             priority="Medium", status="To-do", collaborators=None,
             notes=None, parent_id=None):
    with SessionLocal() as session:
        # commit parent first if parent_id is None
        task = Task(
            title=title,
            description=description,
            start_date=start_date,
            deadline=deadline,
            priority=priority,
            status=status,
            collaborators=collaborators,
            notes=notes,
            parent_id=parent_id  # just store the parent_id, not object
        )
        session.add(task)
        session.commit()
        return task.id

    
#KIRA-22 Update Task Progress Status
def update_task_status(task_id: int, new_status: str) -> str:
    """
    Generic status updater with validation.
    Works for both tasks and subtasks by id.
    """
    if new_status not in ALLOWED_STATUSES:
        raise ValueError(f"Invalid status '{new_status}'. Allowed: {sorted(ALLOWED_STATUSES)}")
    with SessionLocal() as session:
        task = session.get(Task, task_id)
        if not task:
            raise ValueError(f"Task id {task_id} not found")
        task.status = new_status
        session.commit()
        return task.status
    
# Convenience helpers to match Acceptance Criteria semantics

def start_task(task_id: int) -> str:
    """Given a staff member has started on a task, change status to 'In progress'."""
    return update_task_status(task_id, "In progress")

def complete_task(task_id: int) -> str:
    """Given a staff member has completed a task, change status to 'Completed'."""
    return update_task_status(task_id, "Completed")

def mark_blocked(task_id: int) -> str:
    """A task pending approval has a 'Blocked' status."""
    return update_task_status(task_id, "Blocked")
  


# KIRA-2: task-viewing (view all parents tasks)
def list_parent_tasks():
    with SessionLocal() as session:
        stmt = (select(Task)
                .where(Task.parent_id.is_(None))
                .options(joinedload(Task.subtasks))
                .order_by(Task.deadline.is_(None), Task.deadline.asc()))
        return session.execute(stmt).unique().scalars().all()

# KIRA-2: task-viewing (view subtask by parent taks)      
def get_task_with_subtasks(task_id):
    with SessionLocal() as session:
        stmt = (select(Task)
                .options(joinedload(Task.subtasks))
                .where(Task.id == task_id))
        return session.execute(stmt).unique().scalar_one_or_none()
 
# KIRA-3: task-update
def update_task(task_id: int,
                title: Optional[str] = None,
                description: Optional[str] = None,
                start_date: Optional[date] = None,
                deadline: Optional[date] = None,
                priority: Optional[str] = None,
                status: Optional[str] = None,
                collaborators: Optional[str] = None,
                notes: Optional[str] = None,
                parent_id: Optional[int] = None):
    with SessionLocal() as session:
        task = session.get(Task, task_id)
        if task is None:
            return None

        if title is not None: task.title = title
        if description is not None: task.description = description
        if start_date is not None: task.start_date = start_date
        if deadline is not None: task.deadline = deadline
        if priority is not None: task.priority = priority
        if status is not None: task.status = status
        if collaborators is not None: task.collaborators = collaborators
        if notes is not None: task.notes = notes
        if parent_id is not None: task.parent_id = parent_id

        session.add(task)
        session.commit()
        return task.id

def assign_task(task_id, new_members: list[str]):
    with SessionLocal() as session:
        task = session.get(Task, task_id)
        if not task:
            raise ValueError("Task not found")

        existing = set(task.collaborators.split(",")) if task.collaborators else set()
        updated = existing.union(new_members)
        task.collaborators = ",".join(updated)

        session.commit()
