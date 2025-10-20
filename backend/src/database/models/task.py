from sqlalchemy import (
    Column, Integer, String, Date, ForeignKey, CheckConstraint, Index, Boolean, text
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy

from backend.src.database.db_setup import Base
from backend.src.database.models.parent_assignment import ParentAssignment  
from backend.src.enums.task_status import TaskStatus
from backend.src.database.models.comment import Comment

class Task(Base):
    __tablename__ = "task"  

    id          = Column(Integer, primary_key=True)
    title       = Column(String(128), nullable=False)
    description = Column(String(256))
    start_date  = Column(Date)
    deadline    = Column(Date)
    status      = Column(String, nullable=False, default=TaskStatus.TO_DO.value)
    priority    = Column(Integer, nullable=False, default=5)
    recurring   = Column(Integer, nullable=False, default=0)
    tag         = Column(String(128))

    #Link FK to Project table later: ForeignKey("project.id", ondelete="SET NULL")
    project_id  = Column(Integer, nullable=False, index=True)
    active      = Column(Boolean, nullable=False, default=True)

    # --- Association-object relationships ---
    # One parent -> many link rows (each link points to a subtask)
    subtask_links = relationship(
        ParentAssignment,
        foreign_keys=[ParentAssignment.parent_id],
        back_populates="parent",
        passive_deletes=True,
    )

    # Each subtask has at most one parent link (unique on subtask_id)
    parent_link = relationship(
        ParentAssignment,
        foreign_keys=[ParentAssignment.subtask_id],
        back_populates="subtask",
        uselist=False,
        passive_deletes=True,
    )

    #comments = Column(String)
    comments = relationship(
    "Comment",
    back_populates="task",
    cascade="all, delete-orphan",
    passive_deletes=True
    )

    assigned_users = relationship(
        "TaskAssignment", back_populates="task", cascade="all, delete-orphan"
    )

    subtasks = association_proxy("subtask_links", "subtask")  
    parent   = association_proxy("parent_link",   "parent")   

    __table_args__ = (
        CheckConstraint("priority >= 1 AND priority <= 10", name="ck_priority_range"),
        Index("ix_task_project_active_deadline", "project_id", "active", "deadline"),
    )
