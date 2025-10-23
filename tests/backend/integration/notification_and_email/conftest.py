from __future__ import annotations

import os
import tempfile
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path
import importlib.util

from backend.src.database.db_setup import Base
from backend.src.database.models.task import Task
from backend.src.enums.task_status import TaskStatus


def _load_mock_module(file_name: str):
    mock_dir = Path(__file__).parents[3] / 'mock_data' / 'notification&email'
    file_path = mock_dir / file_name
    spec = importlib.util.spec_from_file_location(f"mock_{file_name.replace('.', '_')}", str(file_path))
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader, f"Failed to load mock module: {file_path}"
    spec.loader.exec_module(module) 
    return module


_integration_mock = _load_mock_module('integration_notification_email_data.py')


@pytest.fixture(scope="session")
def test_engine_backend_integration():
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)

    engine = create_engine(f"sqlite:///{db_path}", echo=False)
    Base.metadata.create_all(bind=engine)

    try:
        yield engine
    finally:
        try:
            engine.dispose()
        except Exception:
            pass
        if os.path.exists(db_path):
            try:
                os.remove(db_path)
            except PermissionError:
                pass


@pytest.fixture
def db_session(test_engine_backend_integration):
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
    def _create_task(**kwargs):
        default_data = dict(getattr(_integration_mock, 'DEFAULT_TASK_DATA', {}))
        default_data.setdefault("status", TaskStatus.TO_DO.value)
        default_data["project_id"] = kwargs.pop("project_id", 1)
        default_data.update(kwargs)

        task = Task(**default_data)
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)
        return task

    return _create_task


@pytest.fixture(scope="session", autouse=True)
def override_service_sessionlocal(test_engine_backend_integration):
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
        task_service.SessionLocal = old_sessionlocal


@pytest.fixture(autouse=True)
def bind_service_to_test_connection(db_session):
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
