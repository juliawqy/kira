import threading
import socket
import time
import uuid
import pytest
import uvicorn

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# DB / app imports (adjusted to your project structure)
from backend.src.database.db_setup import Base
import backend.src.database.db_setup as db_setup
import backend.src.services.user as user_service
import backend.src.services.task as task_service
from backend.src.main import app


@pytest.fixture(scope="module")
def driver():
    options = Options()
    # options.add_argument("--headless=new")  # uncomment for CI
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    yield driver
    try:
        driver.quit()
    except Exception:
        pass


@pytest.fixture
def app_server(tmp_path):
    """
    Start a uvicorn server for each test with its own SQLite DB.
    Yields the base API URL (e.g. http://127.0.0.1:PORT/kira/app/api/v1).
    Ensures the engine and server are fully torn down on fixture finalization.
    """
    # unique DB file per test to guarantee isolation even if previous test crashed
    db_file = tmp_path / f"e2e_{uuid.uuid4().hex}.db"
    engine = create_engine(
        f"sqlite:///{db_file}",
        connect_args={"check_same_thread": False},
        future=True,
    )

    # Ensure foreign keys are enabled for SQLite
    @event.listens_for(engine, "connect")
    def _fk_on(dbapi_connection, connection_record):  # pragma: no cover
        cur = dbapi_connection.cursor()
        cur.execute("PRAGMA foreign_keys=ON")
        cur.close()

    # Create fresh schema for this test
    Base.metadata.create_all(bind=engine)

    # Create a session factory bound to this engine
    TestingSessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
        future=True,
    )

    # Patch the central db_setup so code importing db_setup.* sees the test engine/session
    try:
        db_setup.engine = engine
        db_setup.SessionLocal = TestingSessionLocal
    except Exception:
        # safe fallback if attributes differ in your project
        pass

    # ALSO patch service modules that may have captured SessionLocal at import-time
    # (this mirrors what worked in your task tests)
    try:
        user_service.SessionLocal = TestingSessionLocal
    except Exception:
        pass
    try:
        task_service.SessionLocal = TestingSessionLocal
    except Exception:
        pass

    # find a free port
    port = None
    for candidate in range(8010, 8031):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", candidate))
                port = candidate
                break
            except OSError:
                continue
    if port is None:
        raise RuntimeError("No free port found for app_server")

    # Start uvicorn server in background thread
    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    # wait briefly for server to up
    time.sleep(1.0)

    # Yield API base (frontend can append route paths)
    api_base = f"http://127.0.0.1:{port}/kira/app/api/v1"
    try:
        yield api_base
    finally:
        # Shutdown server
        try:
            server.should_exit = True
        except Exception:
            pass
        # give uvicorn a moment and join
        thread.join(timeout=3.0)

        # Drop schema and dispose engine to release file handle
        try:
            Base.metadata.drop_all(bind=engine)
        except Exception:
            pass
        try:
            engine.dispose()
        except Exception:
            pass

@pytest.fixture(autouse=True)
def reset_database():
    # Drop all tables and recreate before each test
    Base.metadata.drop_all(bind=db_setup.engine)
    Base.metadata.create_all(bind=db_setup.engine)
    yield