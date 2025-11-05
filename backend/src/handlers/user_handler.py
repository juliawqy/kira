from __future__ import annotations

import logging
from typing import Iterable, Optional


from backend.src.services import user as user_service
from backend.src.services import department as department_service
from backend.src.enums.task_status import TaskStatus, ALLOWED_STATUSES
from backend.src.enums.task_filter import TaskFilter, ALLOWED_FILTERS
from backend.src.enums.task_sort import TaskSort, ALLOWED_SORTS
from backend.src.enums.user_role import UserRole, ALLOWED_ROLES
from backend.src.database.db_setup import SessionLocal
from backend.src.database.models.user import User



logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)



# -------- User CRUD Handlers -------------------------------------------------------


def create_user(
    name: str,
    email: str,
    role: str,
    password: str,
    department_id: Optional[int] = None,
    admin: bool = False,
    created_by_admin: bool = True, 
):
    
    try:
        role_enum = UserRole(role)
    
    except ValueError as ve:
        raise ValueError(
            f"Invalid role '{role}'. Valid roles are: {[r.value for r in UserRole]}"
        )
    
    if not created_by_admin:
        raise PermissionError("Only admin users can create accounts")

    if not department_id == None:
        dept = department_service.get_department_by_id(department_id)
        if dept == None:
            raise ValueError("Department not found")

    if not user_service.get_user(email) == None:
        raise ValueError("User with this email already exists")
    
    new_user = user_service.create_user(
        name=name,
            email=str(email),
            role=role_enum,
            password=password,
            department_id=department_id,
            admin=admin,
    )

    return new_user


def get_user(identifier: str | int) -> Optional[User]:

    if identifier.isdigit() or isinstance(identifier, int):
        user = user_service.get_user(int(identifier))
    else:
        user = user_service.get_user(identifier)
    if not user:
        raise ValueError("User not found")
    return user
    

def list_users():
    return user_service.list_users()


def update_user(
user_id: int,
    *,
    name: Optional[str] = None,
    email: Optional[str] = None,
    role: Optional[str] = None,
    department_id: Optional[int] = None,
    admin: Optional[bool] = None,
) -> Optional[User]:
    
    if role is not None and role not in ALLOWED_ROLES:
        raise ValueError(f"Invalid role: {role}")
    
    user = user_service.get_user(user_id)
    if not user:
        raise ValueError("User not found")
    
    if email and email != user.email:
        email_user = user_service.get_user(email)
        if not email_user == None:
            raise ValueError("Email already in use")

    if department_id is not None:
        dept = department_service.get_department_by_id(department_id)
        if dept == None:
            raise ValueError("Department not found")
        
    if role is not None:
        role = UserRole(role)
        if role not in ALLOWED_ROLES:
            raise ValueError(f"Invalid role: {role}")
    
    updated_user = user_service.update_user(
        user_id=user_id or None,
        name=name or None,
        email=email or None,
        role=role or None,
        department_id=department_id or None,
        admin=admin or None,
    )
    return updated_user


def delete_user(user_id: int, is_admin: bool) -> bool:
    user = user_service.get_user(user_id)
    if not user:
        raise ValueError("User not found")

    ok = user_service.delete_user(user_id)
    return ok


def change_password(user_id: int, current_password: str, new_password: str) -> bool:
    user = user_service.get_user(user_id)
    if not user:
        raise ValueError("User not found")

    return user_service.change_password(user_id, current_password, new_password)