from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from backend.src.database.db_setup import Base

class Department(Base):
    __tablename__ = "department"

    department_id = Column(Integer, primary_key=True, autoincrement=True)
    department_name = Column(String, nullable=False, index=True)
    manager_id = Column(Integer, ForeignKey("user.user_id", ondelete="SET NULL"), nullable=False, index=True)
    teams = relationship("Team", back_populates="department")
    users = relationship("User", back_populates="department", foreign_keys="User.department_id")
    manager = relationship("User", foreign_keys=[manager_id], lazy="joined")

