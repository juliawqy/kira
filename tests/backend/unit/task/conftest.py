# tests/backend/unit/conftest.py
from __future__ import annotations

import pytest
from sqlalchemy import create_engine, event, delete
from sqlalchemy.orm import sessionmaker

# Import the service layer (keeps one consistent import path: backend.src.*)
import backend.src.services.task as svc

# Import Base and models so Base.metadata knows all tables
from backend.src.database.db_setup import Base
from backend.src.database.models.task import Task
from backend.src.database.models.parent_assignment import ParentAssignment


@pytest.fixture(scope="session")
def test_engine(tmp_path_factory):
    """
    Session-scoped file-backed SQLite engine:
    - shared across connections/threads
    - PRAGMA foreign_keys=ON so FKs/ON DELETE work like prod
    - schema created once, dropped after session
    """
    db_file = tmp_path_factory.mktemp("kira_unit") / "unit.db"
    engine = create_engine(
        f"sqlite:///{db_file}",
        connect_args={"check_same_thread": False},
        future=True,
    )

    @event.listens_for(engine, "connect")
    def _fk_on(dbapi_connection, connection_record):  # pragma: no cover
        cur = dbapi_connection.cursor()
        cur.execute("PRAGMA foreign_keys=ON")
        cur.close()

    # Models are registered via imports above; build schema once
    Base.metadata.create_all(bind=engine)
    try:
        yield engine
    finally:
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="session", autouse=True)
def override_sessionlocal(test_engine):
    """
    Point the app's SessionLocal at the test engine.
    expire_on_commit=False prevents DetachedInstanceError on returned ORM objects.
    """
    TestingSessionLocal = sessionmaker(
        bind=test_engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,  # <-- key for tests reading returned objects
        future=True,
    )
    svc.SessionLocal = TestingSessionLocal
    yield


@pytest.fixture(autouse=True)
def clean_db(test_engine):
    """
    Clean tables BEFORE each test for isolation (links first due to FK, then tasks).
    """
    TestingSession = sessionmaker(bind=test_engine, future=True)
    with TestingSession.begin() as s:
        s.execute(delete(ParentAssignment))
        s.execute(delete(Task))
    yield
