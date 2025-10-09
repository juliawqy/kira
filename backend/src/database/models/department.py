from sqlalchemy import (
    Column,
    Integer,
    String
)
from sqlalchemy import Column, Integer, String
from backend.src.database.db_setup import Base



class Department(Base):
    __tablename__ = "department"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    main = Column(String, nullable=True)
    manager_id = Column(Integer, nullable=False)


