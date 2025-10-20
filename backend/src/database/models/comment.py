from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from backend.src.database.db_setup import Base
from datetime import datetime

class Comment(Base):
    __tablename__ = "comment"

    comment_id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("task.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("user.user_id", ondelete="CASCADE"), nullable=False)
    comment = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    task = relationship("Task", back_populates="comments")
