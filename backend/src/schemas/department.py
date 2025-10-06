from __future__ import annotations
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field



class DepartmentCreate(BaseModel):
    name: str
    manager_id: Optional[int] = None


class DepartmentUpdate(BaseModel):
    # Partial update: only send fields you want to change
    name: Optional[str] = None
    manager_id: Optional[int] = None



class DepartmentRead(BaseModel):
    id: int
    name: str
    manager_id: Optional[int] = None

    class Config:
        from_attributes = True


class UserRead(BaseModel):
    id: int
    username: str
    email: str
    role: Optional[str] = None
    is_active: Optional[bool] = True
    department_id: Optional[int] = None

    class Config:
        from_attributes = True


class DepartmentWithUsers(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    name: str
    manager_id: Optional[int] = None

    # nested list of users
    users: List[UserRead] = Field(
        default_factory=list,
        serialization_alias="users"
    )
