from db.db_setup import SessionLocal
from models.task import Task
from datetime import date

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
    
def assign_task(task_id, new_members: list[str]):
    with SessionLocal() as session:
        task = session.get(Task, task_id)
        if not task:
            raise ValueError("Task not found")

        existing = set(task.collaborators.split(",")) if task.collaborators else set()
        updated = existing.union(new_members)
        task.collaborators = ",".join(updated)

        session.commit()


