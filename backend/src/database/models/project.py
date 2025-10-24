from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, UniqueConstraint, PrimaryKeyConstraint
from backend.src.database.db_setup import Base
from sqlalchemy.orm import relationship


class Project(Base):
    __tablename__ = "project"

    project_id = Column(Integer, primary_key=True, index=True)
    project_name = Column(String, nullable=False)
    project_manager = (Column(Integer, ForeignKey("user.user_id"), nullable=True))
    active = Column(Boolean, nullable=False, default=True)

    tasks = relationship(
        "Task", back_populates="project", cascade="all, delete-orphan"
    )

    project_manager_user = relationship("User", back_populates="managed_projects")


class ProjectAssignment(Base):
    __tablename__ = "project_assignment"

    project_id = Column(Integer, ForeignKey("project.project_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("user.user_id"), nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint("project_id", "user_id", name="pk_project_user"),
    )