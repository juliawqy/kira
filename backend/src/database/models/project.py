from sqlalchemy import Column, Integer, String, Boolean
from backend.src.database.db_setup import Base

class Project(Base):
    __tablename__ = "projects"

    project_id = Column(Integer, primary_key=True, index=True)
    project_name = Column(String, nullable=False)
    project_manager = Column(Integer, nullable=False)
    active = Column(Boolean, nullable=False, default=True)
