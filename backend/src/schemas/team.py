from pydantic import BaseModel
from typing import Optional



class TeamCreate(BaseModel):
    team_name: str
    department_id: int
    team_number: int


class TeamRead(BaseModel):
    team_id: int
    team_name: str
    manager_id: int
    department_id: int
    team_number: int 

    class Config:
        orm_mode = True
