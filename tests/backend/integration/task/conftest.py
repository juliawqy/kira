# tests/backend/integration/task/conftest.py
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, delete
from sqlalchemy.orm import sessionmaker

# Import service first so models register once under backend.src.*
import backend.src.services.task as svc
from backend.src.database.db_setup import Base
from backend.src.database.models.task import Task
from backend.src.database.models.parent_assignment import ParentAssignment
from backend.src.main import app


@pytest.fixture(scope="session")
def test_engine(tmp_path_factory):
    """
    Session-scoped file-backed SQLite engine with FK support.
    Creates schema once, drops at the end.
    """
    db_file = tmp_path_factory.mktemp("kira_integration") / "itest.db"
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

    Base.metadata.create_all(bind=engine)
    try:
        yield engine
    finally:
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="session")
def client(test_engine):
    """
    FastAPI TestClient wired to the test DB via SessionLocal override.
    expire_on_commit=False to avoid DetachedInstanceError across requests.
    """
    TestingSessionLocal = sessionmaker(
        bind=test_engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
        future=True,
    )
    # Point the service layer to the test DB
    svc.SessionLocal = TestingSessionLocal

    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="session")
def task_base_path() -> str:
    """
    Discover the concrete base path for task routes (e.g., '/task' or '/api/v1/task').
    We look for the POST route named 'create_task'.
    """
    for route in app.routes:
        try:
            if getattr(route, "name", None) == "create_task" and "POST" in route.methods:
                return route.path.rstrip("/")
        except Exception:
            continue
    return "/task"  # fallback


@pytest.fixture(autouse=True)
def clean_db(test_engine):
    """Clean tables BEFORE each test: links first (FK), then tasks."""
    TestingSession = sessionmaker(bind=test_engine, future=True)
    with TestingSession.begin() as s:
        s.execute(delete(ParentAssignment))
        s.execute(delete(Task))
    yield
