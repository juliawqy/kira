from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database.db_setup import Base

class Team(Base):
    __tablename__ = "teams"

    team_id = Column(Integer, primary_key=True, index=True)
    team_name = Column(String, unique=True, nullable=False)
    manager_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
