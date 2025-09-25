from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint, CheckConstraint, Index
from sqlalchemy.orm import relationship
from database.db_setup import Base

class ParentAssignment(Base):
    __tablename__ = "parent_assignment" 

    # Composite PK
    parent_id  = Column(Integer, ForeignKey("task.id", ondelete="CASCADE"), primary_key=True)
    subtask_id = Column(Integer, ForeignKey("task.id", ondelete="CASCADE"), primary_key=True)

    # Relationships to Task (string target avoids circular import)
    parent  = relationship("Task", foreign_keys=[parent_id], back_populates="subtask_links")
    subtask = relationship("Task", foreign_keys=[subtask_id], back_populates="parent_link")

    __table_args__ = (
        # Each subtask can belong to at most one parent
        UniqueConstraint("subtask_id", name="uq_parent_assignment_subtask"),
        # Prevent self-linking
        CheckConstraint("parent_id <> subtask_id", name="ck_parent_assignment_not_self"),
        Index("ix_parent_assignment_parent_sub", "parent_id", "subtask_id"),
    )

    # NOTE: could've just implemented a simple association table for this 
    # but decided to implement a mapped class in case we need to add in additional columns in the future

