from __future__ import annotations

import re
from typing import Optional, List

from sqlalchemy import select
from passlib.context import CryptContext

from backend.src.database.db_setup import SessionLocal
from backend.src.database.models.user import User
from backend.src.database.models.department import Department
from backend.src.enums.user_role import UserRole, ALLOWED_ROLES

# ---- Password Hashing -----------------------------------------------------

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
PASSWORD_REGEX = re.compile(r".*[!@#$%^&*(),.?\":{}|<>].*")


def _hash_password(password: str) -> str:
    if not isinstance(password, str):
        raise TypeError("password must be a string")
    return pwd_context.hash(password)


def _verify_password(plain: str, hashed: str) -> bool:
    if not isinstance(plain, str) or not isinstance(hashed, str):
        return False
    return pwd_context.verify(plain, hashed)


def _validate_password(password: str) -> None:
    if len(password) < 8 or not PASSWORD_REGEX.match(password):
        raise ValueError(
            "Password must be at least 8 characters and contain 1 special character"
        )


# ---- Services -------------------------------------------------------------

def create_user(
    name: str,
    email: str,
    role: UserRole,
    password: str,
    department_id: Optional[int] = None,
    admin: bool = False,
    created_by_admin: bool = True,  # <-- NEW param
) -> User:
    """Create a new user with enforced UserRole."""
    if not created_by_admin:
        raise PermissionError("Only admin users can create accounts")

    _validate_password(password)
    if not isinstance(role, UserRole):
        raise ValueError(f"role must be a valid UserRole enum, got {role}")

    with SessionLocal.begin() as session:
        existing = session.execute(select(User).where(User.email == email)).scalar_one_or_none()
        if existing:
            raise ValueError("User with this email already exists")
        
        if not name:
            raise TypeError("name is required and cannot be None or empty")
        
        if not email:
            raise TypeError("email is required and cannot be None or empty")
        
        if not isinstance(admin, bool):
            raise TypeError("admin must be a boolean value")

        user = User(
            name=name,
            email=email,
            role=role.value,
            admin=admin,
            hashed_pw=_hash_password(password),
            department_id=department_id,
        )
        session.add(user)
        session.flush()
        session.refresh(user)
        return user


def get_user(identifier: str | int) -> Optional[User]:
    """Fetch a user by id, email, or name."""
    with SessionLocal() as session:
        if isinstance(identifier, int):
            return session.get(User, identifier)
        stmt = select(User).where(
            (User.email == identifier) | (User.name == identifier)
        )
        return session.execute(stmt).scalar_one_or_none()


def list_users() -> list[User]:
    """List all users ordered by user_id."""
    with SessionLocal() as session:
        stmt = select(User).order_by(User.user_id.asc())
        return session.execute(stmt).scalars().all()


def update_user(
    user_id: int,
    *,
    name: Optional[str] = None,
    email: Optional[str] = None,
    role: Optional[UserRole] = None,
    department_id: Optional[int] = None,
    admin: Optional[bool] = None,
) -> Optional[User]:
    """Update a user's details."""
    if role is not None and role not in ALLOWED_ROLES:
        raise ValueError(f"Invalid role: {role}")

    with SessionLocal.begin() as session:
        user = session.get(User, user_id)
        if not user:
            return None

        if email and email != user.email:
            if session.execute(select(User).where(User.email == email)).scalar_one_or_none():
                raise ValueError("Email already in use")
            user.email = email
        if name is not None:
            user.name = name
        if role is not None:
            user.role = role.value
        if department_id is not None:
            dept = session.get(Department, department_id)
            user.department_id = department_id
        if admin is not None:
            user.admin = admin

        session.add(user)
        session.flush()
        session.refresh(user)
        return user


def delete_user(user_id: int, is_admin: bool) -> bool:
    """Hard delete: remove a user permanently."""
    if not is_admin:
        raise PermissionError("Only admin users can delete accounts")

    with SessionLocal.begin() as session:
        user = session.get(User, user_id)
        if not user:
            return False
        session.delete(user)
        return True


def change_password(user_id: int, current_password: str, new_password: str) -> bool:
    """Change a user's password."""
    _validate_password(new_password)
    with SessionLocal.begin() as session:
        user = session.get(User, user_id)
        if not user:
            raise ValueError("User not found")
        if not _verify_password(current_password, user.hashed_pw):
            raise ValueError("Current password is incorrect")

        user.hashed_pw = _hash_password(new_password)
        session.add(user)
        return True

def get_users_by_department(department_id: int) -> List[User]:
    """Return all users assigned to a department."""
    with SessionLocal() as session:
        stmt = (
            select(User)
            .where(User.department_id == department_id)
            .order_by(User.user_id.asc())
        )
        return list(session.execute(stmt).scalars().all())


def assign_user_to_department(user_id: int, department_id: Optional[int]) -> User:
    """Assign (or unassign with None) a user to a department."""
    with SessionLocal.begin() as session:
        user = session.get(User, user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")

        if department_id is not None:
            dept = session.get(Department, department_id)
            if not dept:
                raise ValueError(f"Department {department_id} not found")

        user.department_id = department_id
        session.add(user)
        session.flush()
        session.refresh(user)
        return user