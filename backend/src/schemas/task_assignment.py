from re import I
from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Optional, List

from backend.src.schemas.user import UserRead


class UnassignUsersPayload(BaseModel):
    user_ids: List[int]

class AssignUsersPayload(BaseModel):
    user_ids: List[int]
    
    @field_validator('user_ids')
    def validate_user_ids(cls, v):
        if not v or len(v) < 1:
            raise ValueError('user_ids must contain at least one user ID')
        return v
