from __future__ import annotations
from typing import List

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from backend.src.schemas.user import UserCreate, UserUpdate, UserRead, UserPasswordChange
from backend.src.enums.user_role import UserRole
import backend.src.handlers.user_handler as user_handler
import backend.src.handlers.department_handler as department_handler

router = APIRouter(prefix="/user", tags=["user"])


# ---- Create ---------------------------------------------------------------

@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED, name="create_user",)
def create_user(payload: UserCreate):
    """
    Create a new user.
    """
    try:

        u = user_handler.create_user(
            name=payload.name,
            email=str(payload.email),
            role=payload.role,
            password=payload.password,
            department_id=payload.department_id,
            admin=payload.admin,
            created_by_admin=payload.created_by_admin
        )
        return UserRead.model_validate(u, from_attributes=True)
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


# ---- Read -----------------------------------------------------------------


@router.get("/{identifier}", response_model=UserRead, name="get_user")
def get_user(identifier: str):
    """
    Get a user by id, email, or name.
    """
    try:
        u = user_handler.get_user(identifier)

    except ValueError:
        raise HTTPException(status_code=404, detail="User not found")

    return UserRead.model_validate(u, from_attributes=True)


@router.get("/", response_model=List[UserRead],name="list_users")
def list_users():
    """
    List all users.
    """
    users = user_handler.list_users()
    return [UserRead.model_validate(u, from_attributes=True) for u in users]


@router.get("department/{department_id}", response_model=List[UserRead],name="list_users_in_department")
def list_users_in_department(department_id: int):
    """
    List all users in a specific department.
    """
    users = department_handler.view_users_in_department(department_id)
    return [UserRead.model_validate(u, from_attributes=True) for u in users]


# ---- Update ---------------------------------------------------------------


@router.patch("/{user_id}", response_model=UserRead, name="update_user")
def update_user(user_id: int, payload: UserUpdate):
    """
    Update a user's details (name, email, role, department_id, admin).
    """
    try:
        update_data = payload.model_dump(exclude_unset=True)
        updated = user_handler.update_user(user_id, **update_data)

        return UserRead.model_validate(updated, from_attributes=True)

    except ValueError as e:
        if "user" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e)) 
        raise HTTPException(status_code=400, detail=str(e))


# ---- Delete ---------------------------------------------------------------


@router.delete("/{user_id}",response_model=bool,name="delete_user")
def delete_user(user_id: int):
    """
    Hard delete a user.
    """
    try:
        deleted_user = user_handler.delete_user(user_id, True)
        return deleted_user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ---- Password -------------------------------------------------------------


@router.post("/{user_id}/password", response_model=bool,name="change_password")
def change_password(user_id: int, payload: UserPasswordChange):
    """
    Change a user's password (requires current_password).
    """
    try:
        return user_handler.change_password(
            user_id,
            payload.current_password,
            payload.new_password,
        )
    except ValueError as e:
        msg = str(e)
        if msg.lower().startswith("current password is incorrect"):
            raise HTTPException(status_code=403, detail=msg)
        raise HTTPException(status_code=400, detail=msg)
