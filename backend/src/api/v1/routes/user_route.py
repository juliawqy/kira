from __future__ import annotations
from typing import List

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from backend.src.schemas.user import UserCreate, UserUpdate, UserRead, UserPasswordChange
from backend.src.enums.user_role import UserRole
import backend.src.services.user as user_service  

router = APIRouter(prefix="/user", tags=["user"])


# ---- Create ---------------------------------------------------------------

@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED, name="create_user",)
def create_user(payload: UserCreate):
    """
    Create a new user.
    """
    try:
        # Convert string role to UserRole enum
        try:
            role_enum = UserRole(payload.role)
        except ValueError as ve:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid role '{payload.role}'. Valid roles are: {[r.value for r in UserRole]}"
            )
            
        u = user_service.create_user(
            name=payload.name,
            email=str(payload.email),
            role=role_enum,
            password=payload.password,
            department_id=payload.department_id,
            admin=bool(payload.admin),
        )
        return UserRead.model_validate(u, from_attributes=True)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ---- Read -----------------------------------------------------------------

@router.get("/{identifier}", response_model=UserRead, name="get_user")
def get_user(identifier: str):
    """
    Get a user by id, email, or name.
    """
    if identifier.isdigit():
        u = user_service.get_user(int(identifier))
    else:
        u = user_service.get_user(identifier)

    if not u:
        raise HTTPException(status_code=404, detail="User not found")

    return UserRead.model_validate(u, from_attributes=True)


@router.get("/", response_model=List[UserRead],name="list_users")
def list_users():
    """
    List all users.
    """
    users = user_service.list_users()
    return [UserRead.model_validate(u, from_attributes=True) for u in users]


# ---- Update ---------------------------------------------------------------

@router.patch("/{user_id}", response_model=UserRead, name="update_user")
def update_user(user_id: int, payload: UserUpdate):
    """
    Update a user's details (name, email, role, department_id, admin).
    """
    try:
        # Convert payload to dict and handle role conversion
        update_data = payload.model_dump(exclude_unset=True)
        
        # Convert string role to UserRole enum if role is provided
        if 'role' in update_data and update_data['role'] is not None:
            try:
                update_data['role'] = UserRole(update_data['role'])
            except ValueError as ve:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid role '{update_data['role']}'. Valid roles are: {[r.value for r in UserRole]}"
                )
        
        updated = user_service.update_user(
            user_id,
            **update_data,
        )
        if not updated:
            raise HTTPException(status_code=404, detail="User not found")
        return UserRead.model_validate(updated, from_attributes=True)
    except ValueError as e:
        # e.g., email already in use
        raise HTTPException(status_code=400, detail=str(e))


# ---- Delete ---------------------------------------------------------------

@router.delete("/{user_id}",response_model=bool,name="delete_user")
def delete_user(user_id: int):
    """
    Hard delete a user.
    """
    ok = user_service.delete_user(user_id)
    if not ok:
        raise HTTPException(status_code=404, detail="User not found")
    return ok


# ---- Password -------------------------------------------------------------

@router.post("/{user_id}/password", response_model=bool,name="change_password")
def change_password(user_id: int, payload: UserPasswordChange):
    """
    Change a user's password (requires current_password).
    """
    try:
        return user_service.change_password(
            user_id,
            payload.current_password,
            payload.new_password,
        )
    except ValueError as e:
        # "User not found" or "Current password is incorrect"
        msg = str(e)
        if msg.lower().startswith("current password is incorrect"):
            raise HTTPException(status_code=403, detail=msg)
        raise HTTPException(status_code=400, detail=msg)
