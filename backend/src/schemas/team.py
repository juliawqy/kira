from pydantic import BaseModel
from typing import Optional



class TeamCreate(BaseModel):
    team_name: str
    department_id: Optional[int] = None
    team_number: Optional[int] = None


class TeamRead(BaseModel):
    team_id: int
    team_name: str
    manager_id: int
    department_id: Optional[int] = None
    team_number: Optional[int] = None

    class Config:
        orm_mode = True
