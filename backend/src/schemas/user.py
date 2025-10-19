from __future__ import annotations
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field, EmailStr


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    role: str
    password: str = Field(..., min_length=8)
    department_id: Optional[int] = None
    admin: Optional[bool] = False
    created_by_admin: bool = True

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    department_id: Optional[int] = None
    admin: Optional[bool] = None

class UserRead(BaseModel):
    user_id: int
    name: str
    email: EmailStr
    role: str
    department_id: Optional[int] = None
    admin: bool        

    class Config:
        from_attributes = True

class UserPasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)
