from sqlalchemy import Column, Integer, String, PrimaryKeyConstraint, ForeignKey
from sqlalchemy.orm import relationship
from backend.src.database.db_setup import Base

class TeamAssignment(Base):
    __tablename__ = "team_assignments"

    team_id = Column(Integer, ForeignKey("team.team_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("user.user_id"), nullable=False)

    user = relationship("User", back_populates="assigned_teams", passive_deletes=True)
    team = relationship("Team", back_populates="team_members", passive_deletes=True)

    __table_args__ = (
        PrimaryKeyConstraint("team_id", "user_id", name="uq_team_user"),
    )

    