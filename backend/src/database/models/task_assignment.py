from sqlalchemy import Column, Integer, ForeignKey, PrimaryKeyConstraint, Index
from sqlalchemy.orm import relationship
from backend.src.database.db_setup import Base

class TaskAssignment(Base):
    __tablename__ = "task_assignment" 

    task_id = Column(Integer, ForeignKey("task.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("user.user_id", ondelete="CASCADE"), nullable=False)

    task = relationship("Task", back_populates="assigned_users", passive_deletes=True)
    user = relationship("User", back_populates="assigned_tasks", passive_deletes=True)

    __table_args__ = (
        PrimaryKeyConstraint("task_id", "user_id", name="pk_task_assignment"),
        Index("ix_task_assignment_task_user", "task_id", "user_id"),
    )