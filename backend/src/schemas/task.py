from __future__ import annotations
from datetime import date
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    start_date: Optional[date] = None
    deadline: Optional[date] = None
    notes: Optional[str] = None
    collaborators: Optional[str] = None   # comma-separated for now
    status: Optional[str] = "To-do"       # keep minimal: plain strings
    priority: Optional[str] = "Medium"
    parent_id: Optional[int] = None

class TaskUpdate(BaseModel):
    # Partial update — send only what you want to change
    title: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date] = None
    deadline: Optional[date] = None
    notes: Optional[str] = None
    collaborators: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    parent_id: Optional[int] = None

class TaskRead(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    start_date: Optional[date] = None
    deadline: Optional[date] = None
    notes: Optional[str] = None
    collaborators: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    parent_id: Optional[int] = None

    class Config:
        from_attributes = True  

class TaskWithSubTasks(BaseModel):

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    title: str
    description: Optional[str] = None
    start_date: Optional[date] = None
    deadline: Optional[date] = None
    notes: Optional[str] = None
    collaborators: Optional[str] = None
    status: str
    priority: str

    subTasks: List[TaskRead] = Field(
        default_factory=list,
        validation_alias="subtasks",
        serialization_alias="subTasks",
    )