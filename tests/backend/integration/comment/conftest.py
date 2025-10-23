from __future__ import annotations

import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, delete
from sqlalchemy.orm import sessionmaker

from backend.src.database.db_setup import Base
from backend.src.database.models.comment import Comment
from backend.src.database.models.task import Task
from backend.src.database.models.user import User
from backend.src.api.v1.router import router as v1_router
from backend.src.main import app
from backend.src.database.models.project import Project

@pytest.fixture(scope="session")
def test_engine(tmp_path_factory):
    db_file = tmp_path_factory.mktemp("kira_integration_comment") / "comment_itest.db"
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
        try:
            engine.dispose()
        finally:
            if os.path.exists(db_file):
                try:
                    os.remove(db_file)
                except PermissionError:
                    pass


@pytest.fixture(scope="session")
def client(test_engine):
    TestingSessionLocal = sessionmaker(
        bind=test_engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
        future=True,
    )
    # Point the comment service to the test DB
    import backend.src.services.comment as comment_service
    comment_service.SessionLocal = TestingSessionLocal

    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="session")
def task_base_path() -> str:
    """Discover base path for task routes (e.g., '/kira/app/api/v1/task')."""

    for route in app.routes:
        try:
            if getattr(route, "name", None) == "add_comment" and "POST" in route.methods:
                return route.path.split("/{task_id}")[0].rstrip("/")
        except Exception:
            continue
    return "/kira/app/api/v1/task"  


@pytest.fixture(autouse=True)
def clean_db(test_engine):
    """Clean tables BEFORE each test: comments first (FK), then tasks and users."""
    TestingSession = sessionmaker(bind=test_engine, future=True)
    with TestingSession.begin() as s:
        s.execute(delete(Comment))
        s.execute(delete(Task))
        s.execute(delete(Project))
        s.execute(delete(User))
    yield
