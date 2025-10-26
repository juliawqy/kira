from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, delete, text
from sqlalchemy.orm import sessionmaker

from backend.src.main import app
from backend.src.database.db_setup import Base

import backend.src.services.task as svc
import backend.src.services.task_assignment as task_assignment_svc
import backend.src.services.project as project_svc

from backend.src.database.models.task import Task
from backend.src.database.models.parent_assignment import ParentAssignment
from backend.src.database.models.project import Project
from backend.src.database.models.task_assignment import TaskAssignment
from backend.src.database.models.user import User


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
        # Teardown: disable FK checks before dropping tables to avoid circular dependency issues
        try:
            with engine.connect() as conn:
                conn.execute(text("PRAGMA foreign_keys=OFF"))
                Base.metadata.drop_all(bind=conn)
                conn.execute(text("PRAGMA foreign_keys=ON"))
        finally:
            engine.dispose()


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
    project_svc.SessionLocal = TestingSessionLocal
    task_assignment_svc.SessionLocal = TestingSessionLocal

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

    TestingSession = sessionmaker(bind=test_engine, future=True)
    with TestingSession.begin() as s:
        s.execute(delete(TaskAssignment))
        s.execute(delete(ParentAssignment))
        s.execute(delete(Task))
        s.execute(delete(Project))
        s.execute(delete(User))
    yield
