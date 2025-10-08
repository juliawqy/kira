# backend/src/schemas/task.py
from __future__ import annotations
from datetime import date
<<<<<<< HEAD
from typing import Optional, List, Literal
=======
from typing import Optional, List, Literal, Annotated
>>>>>>> 90732818ea271ec617266c163ded6d656b42ad1f
from pydantic import BaseModel, ConfigDict, Field
from backend.src.enums.task_status import TaskStatus, ALLOWED_STATUSES

<<<<<<< HEAD
# Keep these exactly in sync with your DB CHECK constraints
Status = Literal["To-do", "In-progress", "Completed", "Blocked"]
Priority = Literal["Low", "Medium", "High"]

# ---------- Read models ----------

=======
# ---------- Read models ----------

>>>>>>> 90732818ea271ec617266c163ded6d656b42ad1f
class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: Optional[str] = None
    start_date: Optional[date] = None
    deadline: Optional[date] = None
<<<<<<< HEAD
    status: Status
    priority: Priority
=======
    status: Literal["To-do", "In-progress", "Completed", "Blocked"]
    priority: int
>>>>>>> 90732818ea271ec617266c163ded6d656b42ad1f
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
<<<<<<< HEAD
    status: Status = "To-do"
    priority: Priority = "Medium"
    project_id: Optional[int] = None
=======
    status: Literal["To-do", "In-progress", "Completed", "Blocked"] = TaskStatus.TO_DO.value
    priority: Annotated[int, Field(ge=1, le=10, description="1 = least important, 10 = most important")] = 5
    project_id: int
>>>>>>> 90732818ea271ec617266c163ded6d656b42ad1f
    active: bool = True
    parent_id: Optional[int] = None      

class TaskUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date] = None
    deadline: Optional[date] = None
<<<<<<< HEAD
    priority: Optional[Priority] = None
=======
    priority: Optional[Annotated[int, Field(ge=1, le=10)]] = None
>>>>>>> 90732818ea271ec617266c163ded6d656b42ad1f
    project_id: Optional[int] = None
    active: Optional[bool] = None
