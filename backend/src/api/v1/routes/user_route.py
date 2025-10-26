from __future__ import annotations
from typing import List

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from backend.src.schemas.user import UserCreate, UserUpdate, UserRead, UserPasswordChange
from backend.src.schemas.comment import CommentRead
from backend.src.enums.user_role import UserRole
import backend.src.services.user as user_service
import backend.src.services.comment as comment_service
import backend.src.handlers.department_handler as department_handler

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
        if not payload.created_by_admin:
            raise HTTPException(
                status_code=403,
                detail="Only admin users can create accounts"
            )

        u = user_service.create_user(
            name=payload.name,
            email=str(payload.email),
            role=role_enum,
            password=payload.password,
            department_id=payload.department_id,
            admin=payload.admin,
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

        if "role" in update_data and update_data["role"] is not None:
            try:
                update_data["role"] = UserRole(update_data["role"])
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid role '{update_data['role']}'. Valid roles are: {[r.value for r in UserRole]}"
                )

        updated = user_service.update_user(user_id, **update_data)
        if not updated:
            raise HTTPException(status_code=404, detail="User not found")

        return UserRead.model_validate(updated, from_attributes=True)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ---- Delete ---------------------------------------------------------------

@router.delete("/{user_id}",response_model=bool,name="delete_user")
def delete_user(user_id: int):
    """
    Hard delete a user.
    """
    ok = user_service.delete_user(user_id, True)
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


# ---- Comments ---------------------------------------------------------------

@router.get("/{user_id}/comments", response_model=List[CommentRead], name="get_user_comments")
def get_user_comments(user_id: int):
    """
    Get all comments made by a specific user.
    """
    try:
        # Verify user exists
        user = user_service.get_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail=f"User {user_id} not found")
        
        comments = comment_service.list_comments_by_user(user_id)
        return comments
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{user_id}/comments/count", response_model=int, name="get_user_comment_count")
def get_user_comment_count(user_id: int):
    """
    Get the total number of comments made by a user.
    """
    try:
        # Verify user exists
        user = user_service.get_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail=f"User {user_id} not found")
        
        count = comment_service.get_user_comment_count(user_id)
        return count
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
