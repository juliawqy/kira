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