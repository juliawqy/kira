from __future__ import annotations
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field



class DepartmentCreate(BaseModel):
    name: str
    manager_id: int 
    department_id: int 



class DepartmentRead(BaseModel):
    id: int
    name: str
    manager_id: int

    class Config:
        from_attributes = True




