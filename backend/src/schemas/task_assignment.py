from re import I
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List

from backend.src.schemas.user import UserRead


class TaskAssignmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    task_id: int
    user_id: int

class TaskAssignmentCreate(TaskAssignmentRead):
    pass

