from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class CommentCreate(BaseModel):
   
    user_id: int
    comment: str

class CommentRead(BaseModel):
    comment_id: int
    task_id: int    
    user_id: int
    comment: str
    timestamp: datetime

    class Config:
        orm_mode = True

class CommentUpdate(BaseModel):
    comment: Optional[str] = None

