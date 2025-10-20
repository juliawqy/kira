from __future__ import annotations
from pydantic import BaseModel, ConfigDict

class DepartmentCreate(BaseModel):
    department_name: str
    manager_id: int

class DepartmentRead(BaseModel):
    department_id: int
    department_name: str
    manager_id: int
    model_config = ConfigDict(from_attributes=True)  
