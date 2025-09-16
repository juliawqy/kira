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
  


def list_parent_tasks():
    with SessionLocal() as session:
        stmt = (select(Task)
                .where(Task.parent_id.is_(None))
                .options(joinedload(Task.subtasks))
                .order_by(Task.deadline.is_(None), Task.deadline.asc()))
        return session.execute(stmt).unique().scalars().all()

     
def get_task_with_subtasks(task_id):
    with SessionLocal() as session:
        stmt = (select(Task)
                .options(joinedload(Task.subtasks))
                .where(Task.id == task_id))
        return session.execute(stmt).unique().scalar_one_or_none()
 

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


def unassign_task(task_id: int, members_to_remove: list[str]):
    with SessionLocal() as session:
        task = session.get(Task, task_id)
        if not task:
            raise ValueError("Task not found")

        existing = set(task.collaborators.split(",")) if task.collaborators else set()
        updated = existing - set(members_to_remove)

        task.collaborators = ",".join(updated) if updated else None

        session.commit()
        return task.collaborators

      
# Delete a subtask only (not a parent task)
def delete_subtask(subtask_id: int) -> bool:
    """
    Delete a subtask by id.
    Returns True if deleted, False if not found.
    """
    with SessionLocal() as session:
        sub = session.get(Task, subtask_id)
        if sub is None:
            return False
        # Safety: only allow deleting if it is a subtask (has a parent)
        if sub.parent_id is None:
            # It's a parent task; use delete_task() instead
            raise ValueError(f"Task {subtask_id} is not a subtask (no parent). Use delete_task().")
        session.delete(sub)
        session.commit()
        return True


# Delete a parent task (and detach its subtasks)
def delete_task(task_id: int) -> dict:
    """
    Delete a task by id.
    - If the task has subtasks, detach them first (parent_id -> None)
      so they return to the product backlog as independent tasks.
    Returns a summary dict: {"deleted": task_id, "subtasks_detached": N}
    """
    with SessionLocal() as session:
        task = session.get(Task, task_id)
        if task is None:
            raise ValueError(f"Task id {task_id} not found")

        # Detach subtasks (move back to backlog)
        # Note: we don't change status; AC only requires making them independent.
        detached = 0
        # Use relationship if available; otherwise query by parent_id
        if hasattr(task, "subtasks"):
            for st in list(task.subtasks):
                st.parent_id = None
                detached += 1
        else:
            # Fallback if relationship not configured
            from sqlalchemy import select
            subs = session.execute(
                select(Task).where(Task.parent_id == task_id)
            ).scalars().all()
            for st in subs:
                st.parent_id = None
                detached += 1

        session.flush()  # ensure children updates hit DB before deleting parent
        session.delete(task)
        session.commit()
        return {"deleted": task_id, "subtasks_detached": detached}

