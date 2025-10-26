from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from backend.src.database.db_setup import Base
from backend.src.enums.user_role import UserRole

class User(Base):
    __tablename__ = "user"

    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(256), unique=True, nullable=False, index=True)
    name = Column(String(64), nullable=False)
    role = Column(String, nullable=False, default=UserRole.STAFF.value)
    admin = Column(Boolean, default=False, nullable=False)
    hashed_pw = Column(String(256), nullable=False)
    department_id = Column(
        Integer,
        ForeignKey("department.department_id", ondelete="SET NULL"),
        nullable=True
    )
    managed_departments = relationship("Department", back_populates="manager", foreign_keys="Department.manager_id")
    department = relationship("Department", back_populates="users", foreign_keys=[department_id])

    assigned_tasks = relationship(
        "TaskAssignment", back_populates="user", cascade="all, delete-orphan"
    )
    assigned_teams = relationship(
        "TeamAssignment", back_populates="user", cascade="all, delete-orphan"
    )

    managed_teams = relationship("Team", back_populates="manager", foreign_keys="Team.manager_id")

    managed_projects = relationship("Project", back_populates="project_manager_user")

    __table_args__ = (
        UniqueConstraint("email", name="uq_user_email"),
    )

