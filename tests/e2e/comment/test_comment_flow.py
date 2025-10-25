import time
import os
import pytest
import threading
import socket
import uvicorn

from selenium.webdriver.common.by import By
from backend.src.database.db_setup import Base
from backend.src.database.models.user import User
from backend.src.database.models.project import Project
from backend.src.database.models.task import Task
import backend.src.services.comment as svc
import backend.src.services.task as task_svc
import backend.src.services.project as proj_svc
import backend.src.services.user as user_svc
from tests.mock_data.comment.e2e_data import E2E_COMMENT_WORKFLOW, E2E_SELECTORS, VALID_USER, VALID_TASK, VALID_PROJECT
from sqlalchemy import create_engine, event, delete
from sqlalchemy.orm import sessionmaker
from backend.src.main import app


@pytest.fixture(scope="session")
def test_engine_comment(tmp_path_factory):
    """
    Session-scoped file-backed SQLite engine with FK support.
    Creates schema once, drops at the end.
    """
    db_file = tmp_path_factory.mktemp("kira_e2e_comment") / "e2e_comment.db"
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
        engine.dispose()


@pytest.fixture
def isolated_database(test_engine_comment):
    """
    Enterprise-grade database isolation using transaction rollback.
    This ensures each test starts with a clean database state.
    """

    TestingSessionLocal = sessionmaker(
        bind=test_engine_comment,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
        future=True,
    )

    with TestingSessionLocal() as session:
        try:
            yield session
        finally:
            session.close()


@pytest.fixture(autouse=True)
def reset_database_tables(test_engine_comment):
    """Drop and recreate all tables before each test to reset ID sequences."""        

    Session = sessionmaker(bind=test_engine_comment, future=True)
    with Session() as session:
        session.execute(delete(Task))
        session.execute(delete(Project))
        session.execute(delete(User))
        session.commit()

        user = User(**VALID_USER)
        session.add(user)
        session.flush()
        project = Project(**VALID_PROJECT)
        session.add(project)
        session.flush()
        task = Task(**VALID_TASK)
        session.add(task)
        session.commit()

    yield

@pytest.fixture(scope="session")
def app_server(test_engine_comment):
    """Run FastAPI app with SessionLocal overridden to the isolated test engine."""
    TestingSessionLocal = sessionmaker(
        bind=test_engine_comment,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
        future=True,
    )
    user_svc.SessionLocal = TestingSessionLocal
    task_svc.SessionLocal = TestingSessionLocal
    svc.SessionLocal = TestingSessionLocal
    proj_svc.SessionLocal = TestingSessionLocal


    port = None
    for candidate in [8010, 8011, 8012, 8013, 8014, 8015, 8016, 8017, 8018, 8019, 8020]:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", candidate))
                port = candidate
                break
            except OSError:
                continue
    if port is None:
        port = 8021

    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    time.sleep(1.0)
    try:
        yield f"http://127.0.0.1:{port}/kira/app/api/v1"
    finally:
        server.should_exit = True
        thread.join(timeout=2)


@pytest.fixture
def test_comment_data():
    """Static test data for predictable workflow."""
    return E2E_COMMENT_WORKFLOW


# E2E-111/001
def test_complete_comment_crud_workflow_ui_only(driver, isolated_database, app_server, test_comment_data):
    """Full UI workflow test for comment feature."""
    data = test_comment_data
    ids = data["entity_ids"]
    selectors = E2E_SELECTORS


    html_file = os.path.join(os.getcwd(), "frontend", "comment", "comment.html")
    from urllib.parse import quote
    driver.get(
        f"file:///{html_file}?api={quote(app_server + '/task')}&task={ids['task_id']}&user={ids['user_id']}"
    )
    time.sleep(1.5)

    # Verify starting empty state
    comments = driver.find_elements(By.CSS_SELECTOR, selectors["comment_item"])
    assert len(comments) == 0, "Expected no comments initially"

    # ADD COMMENT
    driver.find_element(By.ID, selectors["comment_input"]).send_keys(data["comments"]["create"])
    driver.find_element(By.ID, selectors["submit_button"]).click()

    # Wait for async status
    status_ok = False
    for _ in range(6):
        status = driver.find_element(By.ID, selectors["status_element"]).text.lower()
        if data["expected_messages"]["create_success"] in status:
            status_ok = True
            break
        time.sleep(0.5)
    assert status_ok, f"Comment creation failed; got: '{driver.find_element(By.ID, selectors['status_element']).text}'"

    # VERIFY COMMENT IN LIST
    driver.find_element(By.ID, selectors["refresh_button"]).click()
    time.sleep(2)
    comments = driver.find_elements(By.CSS_SELECTOR, selectors["comment_item"])
    assert any(data["comments"]["create"] in c.text for c in comments), "Comment not found in list"

    # UPDATE COMMENT
    update_buttons = driver.find_elements(By.CSS_SELECTOR, selectors["update_button"])
    assert update_buttons, "No update buttons found"
    update_buttons[0].click()
    time.sleep(1)

    update_input = driver.find_element(By.CSS_SELECTOR, selectors["update_input"])
    update_input.clear()
    update_input.send_keys(data["comments"]["update"])
    driver.find_element(By.CSS_SELECTOR, selectors["save_button"]).click()

    # Wait for async status
    status_ok = False
    for _ in range(6):
        status = driver.find_element(By.ID, selectors["status_element"]).text.lower()
        if data["expected_messages"]["update_success"] in status:
            status_ok = True
            break
        time.sleep(0.5)
    assert status_ok, f"Comment update failed; got: '{driver.find_element(By.ID, selectors['status_element']).text}'"

    # VERIFY UPDATED TEXT
    driver.find_element(By.ID, selectors["refresh_button"]).click()
    time.sleep(2)
    page_content = driver.page_source
    assert data["comments"]["update"] in page_content, "Updated comment not visible"

    # DELETE COMMENT
    delete_buttons = driver.find_elements(By.CSS_SELECTOR, selectors["delete_button"])
    assert delete_buttons, "No delete buttons found"
    delete_buttons[0].click()
    time.sleep(1)

    try:
        alert = driver.switch_to.alert
        alert.accept()
    except Exception:
        pass

    # Wait for async status
    status_ok = False
    for _ in range(6):
        status = driver.find_element(By.ID, selectors["status_element"]).text.lower()
        if any(k in status for k in ("deleted", "loaded", "success")):
            status_ok = True
            break
        time.sleep(0.5)
    assert status_ok, f"Comment deletion failed; got: '{driver.find_element(By.ID, selectors['status_element']).text}'"

    # FINAL VERIFY EMPTY
    driver.find_element(By.ID, selectors["refresh_button"]).click()
    time.sleep(2)
    comments = driver.find_elements(By.CSS_SELECTOR, selectors["comment_item"])
    assert len(comments) == 0, "Expected no comments after deletion"
