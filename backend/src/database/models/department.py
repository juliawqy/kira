from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    CheckConstraint,
    Index,
)
from sqlalchemy.orm import relationship
from backend.src.database.db_setup import Base


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)

    manager_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    # Relationships
    manager = relationship(
        "User",
        back_populates="managed_departments",
        foreign_keys=[manager_id]
    )
    users = relationship(
        "User",
        back_populates="department",
        foreign_keys="User.department_id"
    )

    __table_args__ = (
        CheckConstraint("name <> ''", name="ck_departments_name_nonempty"),
    )


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), nullable=False, unique=True)
    email = Column(String(255), nullable=False, unique=True)
    role = Column(String(50), nullable=False, default="member")  # e.g. admin, manager, member
    is_active = Column(Boolean, default=True)

    department_id = Column(
        Integer,
        ForeignKey("departments.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    # Relationships
    department = relationship(
        "Department",
        back_populates="users",
        foreign_keys=[department_id]
    )
    managed_departments = relationship(
        "Department",
        back_populates="manager",
        foreign_keys="Department.manager_id"
    )

    __table_args__ = (
        CheckConstraint("role in ('admin','manager','member')", name="ck_users_role"),
    )
