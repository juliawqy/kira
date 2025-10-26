# tests/backend/integration/user/conftest.py
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, delete, text
from sqlalchemy.orm import sessionmaker

import backend.src.services.user as svc
from backend.src.database.db_setup import Base
from backend.src.database.models.user import User
# from backend.src.database.models.team import Team  # when needed for FK
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
    
    # Also override comment service SessionLocal
    import backend.src.services.comment as comment_svc
    comment_svc.SessionLocal = TestingSessionLocal

    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="session")
def user_base_path() -> str:
    """
    Discover the concrete base path for user routes (e.g., '/user' or '/api/v1/user').
    We look for the POST route named 'create_user'.
    """
    for route in app.routes:
        try:
            if getattr(route, "name", None) == "create_user" and "POST" in route.methods:
                return route.path.rstrip("/")
        except Exception:
            continue
    return "/user"  # fallback


@pytest.fixture
def test_db_session(test_engine):
    """
    Create a database session using the same SessionLocal as the API.
    """
    TestingSessionLocal = sessionmaker(
        bind=test_engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
        future=True,
    )

    with TestingSessionLocal() as session:
        yield session


@pytest.fixture(autouse=True)
def clean_db(test_engine):
    """Clean tables BEFORE each test: handle FK-safe cleanup for user-comment integration."""
    TestingSession = sessionmaker(bind=test_engine, future=True)
    with TestingSession.begin() as s:
        # Temporarily disable foreign key constraints for cleanup
        s.execute(text("PRAGMA foreign_keys=OFF"))
        
        # Clean all tables that might interfere with user tests
        s.execute(text("DELETE FROM comment"))
        s.execute(text("DELETE FROM task"))
        s.execute(text("DELETE FROM project"))
        s.execute(text("DELETE FROM user"))
        
        # Re-enable foreign key constraints
        s.execute(text("PRAGMA foreign_keys=ON"))
    yield
