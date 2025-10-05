from pydantic import BaseModel
from typing import Optional

class ProjectCreate(BaseModel):
    project_name: str  

class ProjectRead(BaseModel):
    project_id: int
    project_name: str
    project_manager: int
    active: bool = True

    class Config:
        orm_mode = True

class ProjectAssignmentCreate(BaseModel):
    project_id: int
    user_id: int