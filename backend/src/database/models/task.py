from sqlalchemy import (
    Column, Integer, String, Date, ForeignKey, CheckConstraint, Index
)
from sqlalchemy.orm import relationship
from database.db_setup import Base

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(String)
    start_date = Column(Date)
    deadline = Column(Date)
    notes = Column(String)
    collaborators = Column(String)

    status = Column(String(20), nullable=False, default="To-do")
    priority = Column(String(20), nullable=False, default="Medium")

    # Keep children; set parent_id -> NULL when parent is deleted
    parent_id = Column(
        Integer,
        ForeignKey("tasks.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    parent = relationship(
        "Task",
        remote_side=lambda: Task.id,
        back_populates="subtasks",
        foreign_keys=lambda: [Task.parent_id],
    )
    subtasks = relationship(
        "Task",
        back_populates="parent",
        foreign_keys=lambda: [Task.parent_id],
        # NO delete-orphan/cascade delete; let DB handle ON DELETE SET NULL
        passive_deletes=True,
    )

    comments = Column(String)

    __table_args__ = (
        CheckConstraint("status in ('To-do','In-progress','Completed')", name="ck_tasks_status"),
        CheckConstraint("priority in ('Low','Medium','High')", name="ck_tasks_priority"),
    )
