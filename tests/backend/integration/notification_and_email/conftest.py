from __future__ import annotations

import pytest
from sqlalchemy.orm import sessionmaker


@pytest.fixture(scope="session", autouse=True)
def override_service_sessionlocal(test_engine_backend_integration):
    """
    Ensure backend.src.services.task uses the same test database engine
    as the integration tests in this package.
    """
    from backend.src.services import task as task_service

    TestingSessionLocal = sessionmaker(
        bind=test_engine_backend_integration,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )
    task_service.SessionLocal = TestingSessionLocal
    yield


@pytest.fixture(autouse=True)
def bind_service_to_test_connection(db_session):
    """
    Bind services.task.SessionLocal to the SAME connection used by db_session
    so updates within the test transaction are visible to service calls.
    """
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
