from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from db.db_setup import Base

class Task(Base):
    __tablename__ = 'tasks'
    
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String)
    start_date = Column(Date)
    deadline = Column(Date)
    notes = Column(String)
    collaborators = Column(String)  # comma-separated for now
    status = Column(String, default="To-do")  # to-do, in-progress, done
    priority = Column(String, default="Medium")     # Low, Medium, High
    
    # Link to parent task
    parent_id = Column(Integer, ForeignKey('tasks.id'), nullable=True)
    subtasks = relationship(
        "Task", 
        back_populates="parent", 
        lazy="joined"
    )
    parent = relationship(
        "Task",
        remote_side=[id],
        back_populates="subtasks"
    )
    
    comments = Column(String) 
