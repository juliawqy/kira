from sqlalchemy import Column, Integer, String, UniqueConstraint, ForeignKey
from backend.src.database.db_setup import Base


class Team(Base):
    __tablename__ = "teams"

    team_id = Column(Integer, primary_key=True, index=True)
    team_name = Column(String, nullable=False)
    manager_id = Column(Integer, nullable=False)
    department_id = Column(Integer, nullable=False)
    team_number = Column(Integer, nullable=False)


class TeamAssignment(Base):
    __tablename__ = "team_assignments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    team_id = Column(Integer, ForeignKey("teams.team_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)

    __table_args__ = (
        UniqueConstraint("team_id", "user_id", name="uq_team_user"),
    )
