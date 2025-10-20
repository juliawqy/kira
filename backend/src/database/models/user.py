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
    department_id = Column(Integer, nullable=True)  # no ForeignKey for now

    # department_id = Column(Integer, ForeignKey("departments.department_id"), nullable=True)
    # department = relationship("Department", back_populates="users", lazy="joined")

    assigned_tasks = relationship(
        "TaskAssignment", back_populates="user", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("email", name="uq_user_email"),
    )
