from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from backend.src.schemas.user import UserRead

class CommentCreate(BaseModel):
   
    user_id: int
    comment: str

class CommentRead(BaseModel):
    comment_id: int
    task_id: int    
    user_id: int
    comment: str
    timestamp: datetime
    user: Optional[UserRead] = None

    class Config:
        orm_mode = True

class CommentUpdate(BaseModel):
    comment: Optional[str] = None

class CommentWithUser(BaseModel):
    comment_id: int
    task_id: int    
    user_id: int
    comment: str
    timestamp: datetime
    user: UserRead

    class Config:
        orm_mode = True

