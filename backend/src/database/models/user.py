from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from backend.src.database.db_setup import Base 


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)
    admin = Column(Boolean, default=False)
    hashed_pw = Column(String(255), nullable=False)
    department_id = Column(Integer, nullable=True)  # no ForeignKey for now

    # department_id = Column(Integer, ForeignKey("departments.department_id"), nullable=True)
    # department = relationship("Department", back_populates="users", lazy="joined")

    __table_args__ = (
        UniqueConstraint("email", name="uq_user_email"),
    )
