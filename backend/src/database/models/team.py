from sqlalchemy import Column, Integer, String
from backend.src.database.db_setup import Base

class Team(Base):
    __tablename__ = "teams"

    team_id = Column(Integer, primary_key=True, index=True)
    team_name = Column(String, nullable=False)
    manager_id = Column(Integer, nullable=False)
