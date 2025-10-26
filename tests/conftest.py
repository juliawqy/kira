"""
Global test configuration and fixtures.
"""
import pytest
import tempfile
import os
import time
import multiprocessing
import requests

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker

from backend.src.database.db_setup import Base
from backend.src.database.models.user import User
from backend.src.database.models.task import Task
from backend.src.main import app
import uvicorn

def _run_server():
    uvicorn.run(
        "backend.src.main:app",
        host="127.0.0.1",
        port=8001,
        log_level="info",
    )


@pytest.fixture(scope="session")
def live_server(test_db_path):
    """
    Run FastAPI app in a subprocess, sharing the same DB file path.
    """
    proc = multiprocessing.Process(target=_run_server, daemon=True)
    proc.start()

    # wait until server is up
    for _ in range(20):
        try:
            requests.get("http://127.0.0.1:8001/docs")
            break
        except Exception:
            time.sleep(0.5)

    yield "http://127.0.0.1:8001"

    proc.terminate()
    proc.join()


@pytest.fixture(scope="session")
def test_db_path():
    """Create a temp DB file path shared between test + live server processes."""
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)
    yield db_path
    # Cleanup after all processes are done
    if os.path.exists(db_path):
        os.remove(db_path)


@pytest.fixture(scope="session")
def test_engine(test_db_path):
    """
    Each process creates its own engine bound to the same temp file.
    """
    engine = create_engine(
        f"sqlite:///{test_db_path}",
        connect_args={"check_same_thread": False},
        echo=False,
        future=True,
    )

    # Enforce foreign key constraints for normal test operation
    @event.listens_for(engine, "connect")
    def _fk_pragma(dbapi_connection, connection_record):  # pragma: no cover
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(bind=engine)
    yield engine

    # Teardown: disable FK checks on the same connection used for drop_all,
    # so dropping parent tables won't fail due to FK checks on this connection.
    # Using a connection and passing it to drop_all ensures the PRAGMA is in effect
    # for the drop operation.
    try:
        with engine.connect() as conn:
            # Ensure the PRAGMA is executed on this connection
            conn.execute(text("PRAGMA foreign_keys=OFF"))
            # Pass the connection to drop_all so it runs on the same connection
            Base.metadata.drop_all(bind=conn)
            conn.execute(text("PRAGMA foreign_keys=ON"))
    finally:
        engine.dispose()


@pytest.fixture
def db_session(test_engine):
    """
    Session fixture bound to the test engine.
    """
    connection = test_engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection, autoflush=False, autocommit=False)
    session = Session()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def user_factory(db_session):
    """
    Factory for creating test users.
    """
    def _create_user(**kwargs):
        from backend.src.enums.user_role import UserRole
        default_data = {
            "name": "Test User",
            "email": "test@example.com",
            "role": UserRole.STAFF,
            "password_hash": "hashed_password",
            "department_id": None,
            "admin": False,
            "created_by_admin": True
        }
        default_data.update(kwargs)

        user = User(**default_data)
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    return _create_user


@pytest.fixture
def task_factory(db_session):
    """
    Factory for creating test tasks.
    """
    def _create_task(**kwargs):
        from backend.src.enums.task_status import TaskStatus
        default_data = {
            "title": "Test Task",
            "description": "Test Description",
            "status": TaskStatus.TODO,
            "priority": 5,
            "assigned_user_id": None,
        }
        default_data.update(kwargs)

        task = Task(**default_data)
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)
        return task

    return _create_task