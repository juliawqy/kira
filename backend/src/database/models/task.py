from sqlalchemy import (
    Column, Integer, String, Date, ForeignKey, CheckConstraint, Index, Boolean, text
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy

from backend.src.database.db_setup import Base
from backend.src.database.models.parent_assignment import ParentAssignment  

STATUS_VALUES   = ("To-do", "In-progress", "Completed", "Blocked")  
PRIORITY_VALUES = ("Low", "Medium", "High")

class Task(Base):
    __tablename__ = "task"  

    id          = Column(Integer, primary_key=True)
    title       = Column(String(128), nullable=False)
    description = Column(String(256))
    start_date  = Column(Date)
    deadline    = Column(Date)

    status      = Column(String(20), nullable=False, default="To-do")
    priority    = Column(String(10), nullable=False, default="Medium")

    #Link FK to Project table later: ForeignKey("project.id", ondelete="SET NULL")
    project_id  = Column(Integer, nullable=True, index=True)
    active      = Column(Boolean, nullable=False, server_default=text("1"))  # SQLite 'true' equivalent

    # --- Association-object relationships ---
    # One parent -> many link rows (each link points to a subtask)
    subtask_links = relationship(
        ParentAssignment,
        foreign_keys=[ParentAssignment.parent_id],
        back_populates="parent",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    # Each subtask has at most one parent link (unique on subtask_id)
    parent_link = relationship(
        ParentAssignment,
        foreign_keys=[ParentAssignment.subtask_id],
        back_populates="subtask",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    # --- Friendly proxies (so your app can keep using task.subtasks / task.parent) 
    subtasks = association_proxy("subtask_links", "subtask")  # list-like: append Task objects
    parent   = association_proxy("parent_link",   "parent")   # single Task or None

    __table_args__ = (
        CheckConstraint(f"status IN {STATUS_VALUES}",     name="ck_task_status"),
        CheckConstraint(f"priority IN {PRIORITY_VALUES}", name="ck_task_priority"),
        Index("ix_task_project_active_deadline", "project_id", "active", "deadline"),
    )
