from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from backend.src.database.db_setup import Base

class Department(Base):
    __tablename__ = "department"

    department_id = Column(Integer, primary_key=True, autoincrement=True)
    department_name = Column(String, nullable=False, index=True)
    manager_id = Column(Integer, nullable=False)

    teams = relationship("Team", back_populates="department")
    users = relationship("User", back_populates="department")

