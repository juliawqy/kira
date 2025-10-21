from pydantic import BaseModel, Field
from typing import Optional, List


class TeamCreate(BaseModel):
    team_name: str
    department_id: int
    team_number: str


class TeamAssignmentRead(BaseModel):
    id: int
    team_id: int
    user_id: int

    class Config:
        orm_mode = True


class TeamRead(BaseModel):
    team_id: int
    team_name: str
    manager_id: int
    department_id: int
    team_number: str 

    class Config:
        orm_mode = True


class TeamAssignmentCreate(BaseModel):
    team_id: int
    user_id: int
