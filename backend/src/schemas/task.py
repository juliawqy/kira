# backend/src/schemas/task.py
from __future__ import annotations
from datetime import date
from typing import Optional, List, Literal
from pydantic import BaseModel, ConfigDict, Field, conint

# Keep these exactly in sync with your DB CHECK constraints
Status = Literal["To-do", "In-progress", "Completed", "Blocked"]

# ---------- Read models ----------

class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: Optional[str] = None
    start_date: Optional[date] = None
    deadline: Optional[date] = None
    status: Status
    priority_bucket: int
    project_id: Optional[int] = None
    active: bool

class TaskWithSubTasks(TaskRead):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    subTasks: List[TaskRead] = Field(
        default_factory=list,
        validation_alias="subtasks",      
        serialization_alias="subTasks", 
    )

# ---------- Write models ----------

class TaskCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: str
    description: Optional[str] = None
    start_date: Optional[date] = None
    deadline: Optional[date] = None
    status: Status = "To-do"
    priority_bucket: conint(ge=1, le=10) = Field(..., description="1 = least important, 10 = most important")
    project_id: Optional[int] = None
    active: bool = True
    parent_id: Optional[int] = None      

class TaskUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date] = None
    deadline: Optional[date] = None
    priority_bucket: Optional[conint(ge=1, le=10)] = None
    project_id: Optional[int] = None
    active: Optional[bool] = None
