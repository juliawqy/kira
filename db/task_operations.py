from sqlalchemy import select
from sqlalchemy.orm import joinedload
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