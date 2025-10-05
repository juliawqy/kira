from __future__ import annotations

import re
from typing import Optional

from sqlalchemy import select
from passlib.context import CryptContext

from backend.src.database.db_setup import SessionLocal
from backend.src.database.models.user import User
from backend.src.enums.user_role import UserRole

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
) -> User:
    """Create a new user with enforced UserRole."""
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

        user = User(
            name=name,
            email=email,
            role=role.value,  # store string representation
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
    if role is not None and not isinstance(role, UserRole):
        raise ValueError(f"role must be a valid UserRole enum, received: {role}, which is invalid")

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
            user.department_id = department_id
        if admin is not None:
            user.admin = admin

        session.add(user)
        session.flush()
        session.refresh(user)
        return user


def delete_user(user_id: int) -> bool:
    """Hard delete: remove a user permanently."""
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
