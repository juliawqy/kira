from __future__ import annotations

import os
import tempfile
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.src.database.db_setup import Base
from backend.src.database.models.task import Task
from backend.src.enums.task_status import TaskStatus


@pytest.fixture(scope="session")
def test_engine_backend_integration():
    """Create a temporary SQLite DB engine for backend integration tests (scoped to this package)."""
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)

    engine = create_engine(f"sqlite:///{db_path}", echo=False)
    Base.metadata.create_all(bind=engine)

    try:
        yield engine
    finally:
        # Ensure all pooled connections are closed before deleting the file (Windows lock safety)
        try:
            engine.dispose()
        except Exception:
            pass
        if os.path.exists(db_path):
            try:
                os.remove(db_path)
            except PermissionError:
                # Best-effort cleanup; leave file if still locked
                pass


@pytest.fixture
def db_session(test_engine_backend_integration):
    """Provide a transaction-scoped session for each test."""
    connection = test_engine_backend_integration.connect()
    transaction = connection.begin()

    Session = sessionmaker(bind=connection)
    session = Session()

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def task_factory(db_session):
    """Factory to create Task rows for integration tests."""
    def _create_task(**kwargs):
        default_data = {
            "title": "Test Task",
            "description": "Test Description",
            "status": TaskStatus.TO_DO.value,
            "priority": 5,
            "project_id": kwargs.pop("project_id", 1),
            "active": True,
        }
        default_data.update(kwargs)

        task = Task(**default_data)
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)
        return task

    return _create_task


@pytest.fixture(scope="session", autouse=True)
def override_service_sessionlocal(test_engine_backend_integration):
    """Ensure services.task uses this package's test engine."""
    from backend.src.services import task as task_service

    old_sessionlocal = task_service.SessionLocal
    TestingSessionLocal = sessionmaker(
        bind=test_engine_backend_integration,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )
    task_service.SessionLocal = TestingSessionLocal
    try:
        yield
    finally:
        # Restore original SessionLocal so other suites don't hold onto this engine
        task_service.SessionLocal = old_sessionlocal


@pytest.fixture(autouse=True)
def bind_service_to_test_connection(db_session):
    """Bind services.task.SessionLocal to the SAME connection used by db_session for each test."""
    from backend.src.services import task as task_service
    from sqlalchemy.orm import sessionmaker

    old_sessionlocal = task_service.SessionLocal
    TestingSessionLocal = sessionmaker(
        bind=db_session.get_bind(),
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )
    task_service.SessionLocal = TestingSessionLocal
    try:
        yield
    finally:
        task_service.SessionLocal = old_sessionlocal
