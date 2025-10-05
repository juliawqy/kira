"""
Global test configuration and fixtures.
"""
import os
import tempfile
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# --- Your app & DB setup ---
from backend.src.main import app
from backend.src.database.db_setup import Base

# --- ORM models you already use in factories ---
from backend.src.database.models.user import User
from backend.src.database.models.task import Task


# ---------- Test DB engine (session scope) ----------
@pytest.fixture(scope="session")
def test_db_path():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    try:
        yield path
    finally:
        if os.path.exists(path):
            os.remove(path)

@pytest.fixture(scope="session")
def test_engine(test_db_path):
    """
    Create a test database engine for the entire test session.
    Use check_same_thread=False so FastAPI/TestClient can use the same file DB across threads.
    """
    engine = create_engine(
        f"sqlite:///{test_db_path}",
        echo=False,
        future=True,
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    try:
        yield engine
    finally:
        Base.metadata.drop_all(bind=engine)


# ---------- Per-test session & transaction ----------
@pytest.fixture
def db_session(test_engine):
    """
    Create a database session for each test with automatic rollback.
    """
    connection = test_engine.connect()
    transaction = connection.begin()
    SessionLocal = sessionmaker(bind=connection, autoflush=False, autocommit=False, future=True)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


# ---------- FastAPI client for API testing ----------
@pytest.fixture
def client():
    """
    TestClient for API testing.
    Since your app doesn't use dependency injection for DB sessions,
    this provides a simple test client for API endpoint testing.
    """
    with TestClient(app) as c:
        yield c


# ---------- Factories (aligned to your User model columns) ----------
@pytest.fixture
def user_factory(db_session):
    """
    Factory for creating test users directly via ORM (bypasses API).
    Matches model fields: user_id, email, name, role (str), admin (bool), hashed_pw (str), department_id (int|None).
    """
    def _create_user(**kwargs):
        from backend.src.enums.user_role import UserRole

        role_val = kwargs.pop("role", UserRole.STAFF)
        # role column is a string; accept Enum or str
        role_str = role_val.value if hasattr(role_val, "value") else str(role_val)

        default = {
            "name": "Test User",
            "email": "test@example.com",
            "role": role_str,
            "admin": False,
            "hashed_pw": "hashed_password",   # matches model column
            "department_id": 1,
        }
        default.update(kwargs)

        # Ensure final role is a string
        if hasattr(default["role"], "value"):
            default["role"] = default["role"].value

        user = User(**default)
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    return _create_user


@pytest.fixture
def task_factory(db_session):
    """
    Factory for creating test tasks directly via ORM.
    """
    def _create_task(**kwargs):
        from backend.src.enums.task_status import TaskStatus
        from backend.src.enums.task_priority import TaskPriority

        default = {
            "title": "Test Task",
            "description": "Test Description",
            "status": TaskStatus.TODO,
            "priority": TaskPriority.MEDIUM,
            "assigned_user_id": None,
        }
        default.update(kwargs)

        task = Task(**default)
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)
        return task

    return _create_task
