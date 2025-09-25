from pydantic import BaseModel

class TeamCreate(BaseModel):
	team_name: str

class TeamRead(BaseModel):
    team_id: int
    team_name: str
    manager_id: int
    user_id: int
    name: str
    email: str

    class Config:
        orm_mode = True
