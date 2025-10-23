from sqlalchemy import Column, Integer, String, UniqueConstraint, ForeignKey
from sqlalchemy.orm import relationship
from backend.src.database.db_setup import Base


class Team(Base):
    __tablename__ = "team"

    team_id = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)
    team_name = Column(String, nullable=False)
    manager_id = Column(Integer, nullable=False)
    department_id = Column(Integer, ForeignKey("department.department_id", ondelete="CASCADE"), nullable=False)
    team_number = Column(String, nullable=False)

    department = relationship("Department", back_populates="teams")

    team_members = relationship(
        "TeamAssignment", back_populates="team", cascade="all, delete-orphan"
    )
