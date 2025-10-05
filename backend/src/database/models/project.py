from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, UniqueConstraint, PrimaryKeyConstraint
from backend.src.database.db_setup import Base

class Project(Base):
    __tablename__ = "projects"

    project_id = Column(Integer, primary_key=True, index=True)
    project_name = Column(String, nullable=False)
    project_manager = Column(Integer, nullable=False)
    active = Column(Boolean, nullable=False, default=True)


class ProjectAssignment(Base):
    __tablename__ = "project_assignments"

    project_id = Column(Integer, ForeignKey("projects.project_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint("project_id", "user_id", name="pk_project_user"),
    )