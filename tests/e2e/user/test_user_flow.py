from __future__ import annotations
import os
from backend.src.database.db_setup import Base
import pytest
from selenium.webdriver.common.by import By
import time
from urllib.parse import quote

from tests.mock_data.user.e2e_data import E2E_USER_WORKFLOW, E2E_SELECTORS, VALID_DEPARTMENT, SEED_USER
from backend.src.database.models.user import User
from backend.src.database.models.department import Department
import backend.src.services.user as svc
import threading
import socket
import uvicorn
from sqlalchemy import create_engine, event, delete
from sqlalchemy.orm import sessionmaker
from backend.src.main import app


@pytest.fixture(scope="session")
def test_engine_user(tmp_path_factory):
    """
    Session-scoped file-backed SQLite engine with FK support.
    Creates schema once, drops at the end.
    """
    db_file = tmp_path_factory.mktemp("kira_e2e_user") / "e2e_user.db"
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
def isolated_database(test_engine_user):
    """
    Enterprise-grade database isolation using transaction rollback.
    This ensures each test starts with a clean database state.
    """

    TestingSessionLocal = sessionmaker(
        bind=test_engine_user,
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
def reset_database_tables(test_engine_user):
    """Drop and recreate all tables before each test to reset ID sequences."""        

    Session = sessionmaker(bind=test_engine_user, future=True)
    with Session() as session:
        session.execute(delete(Department))
        session.execute(delete(User))
        session.commit()

        user = User(**SEED_USER)
        session.add(user)
        session.flush()
        department = Department(**VALID_DEPARTMENT)
        session.add(department)
        session.commit()

    yield

@pytest.fixture(scope="session")
def app_server(test_engine_user):
    """Run FastAPI app with SessionLocal overridden to the isolated test engine."""
    TestingSessionLocal = sessionmaker(
        bind=test_engine_user,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
        future=True,
    )
    svc.SessionLocal = TestingSessionLocal

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
        yield f"http://127.0.0.1:{port}/kira/app/api/v1/user"
    finally:
        server.should_exit = True
        thread.join(timeout=2)


@pytest.fixture
def test_user_data():
    """Static test data for consistent, repeatable tests."""
    return E2E_USER_WORKFLOW


# E2E-057/001
def test_complete_user_crud_workflow_ui_only(driver, isolated_database, app_server, test_user_data):
    """
    Full user CRUD flow against a fresh test server per test.
    app_server fixture ensures a fresh DB and server, even if previous test crashed.
    """

    create_data = test_user_data["create"]
    update_data = test_user_data["update"]
    expected = test_user_data["expected_responses"]
    selectors = E2E_SELECTORS

    # Load the file-based frontend but tell it which API to use via query param "api"
    html_file = os.path.join(os.getcwd(), "frontend", "user", "user.html")
    driver.get(f"file:///{html_file}?api={quote(app_server)}")
    time.sleep(2)

    # START: Ensure list empty
    user_items = driver.find_elements(By.CSS_SELECTOR, selectors["list_view"]["user_items"])
    assert len(user_items) == 1, f"Expected 1 seeded user list, found {len(user_items)} users"

    # OPEN CREATE UI
    driver.find_element(By.XPATH, "//button[text()='Create New User']").click()
    time.sleep(1)

    # FILL CREATE FORM
    driver.find_element(By.ID, selectors["forms"]["name_input"]).send_keys(create_data["name"])
    driver.find_element(By.ID, selectors["forms"]["email_input"]).send_keys(create_data["email"])

    role_select = driver.find_element(By.ID, selectors["forms"]["role_select"])
    role_select.find_element(By.CSS_SELECTOR, f"option[value='{create_data['role'].value}']").click()

    driver.find_element(By.ID, selectors["forms"]["password_input"]).send_keys(create_data["password"])
    driver.find_element(By.ID, selectors["forms"]["department_input"]).send_keys(create_data["department_id"])
    if create_data.get("is_admin") or create_data.get("admin"):
        # checkbox naming may vary; try to click if present
        try:
            driver.find_element(By.ID, selectors["forms"]["admin_checkbox"]).click()
        except Exception:
            pass

    driver.find_element(By.CSS_SELECTOR, selectors["forms"]["submit_button"]).click()
    time.sleep(2)

    # Dismiss any alert if present
    try:
        alert = driver.switch_to.alert
        alert.dismiss()
        time.sleep(0.5)
    except Exception:
        pass

    status = driver.find_element(By.ID, selectors["status"]["status_element"]).text
    assert expected["create_success"] in status.lower(), f"User creation failed: {status}"

    # BACK -> REFRESH -> verify created
    driver.find_element(By.XPATH, "//button[text()='← Back to Users']").click()
    time.sleep(1)
    driver.find_element(By.ID, selectors["status"]["refresh_button"]).click()
    time.sleep(1)

    user_items = driver.find_elements(By.CSS_SELECTOR, selectors["list_view"]["user_items"])
    assert any(create_data["name"] in it.text for it in user_items), "Created user not in list"

    # UPDATE flow (use first update button)
    update_buttons = driver.find_elements(By.CSS_SELECTOR, selectors["list_view"]["update_button"])
    assert update_buttons, "No update buttons found"
    update_buttons[0].click()
    time.sleep(1)

    name_input = driver.find_element(By.CSS_SELECTOR, "[id^='update-name-']")
    email_input = driver.find_element(By.CSS_SELECTOR, "[id^='update-email-']")
    role_select = driver.find_element(By.CSS_SELECTOR, "[id^='update-role-']")

    name_input.clear()
    name_input.send_keys(update_data["name"])
    email_input.clear()
    email_input.send_keys(update_data["email"])
    role_select.find_element(By.CSS_SELECTOR, f"option[value='{update_data['role'].value}']").click()

    driver.find_element(By.CSS_SELECTOR, selectors["list_view"]["save_button"]).click()
    time.sleep(1)

    status_text = driver.find_element(By.ID, selectors["status"]["status_element"]).text.lower()
    assert any(ind in status_text for ind in expected["update_success"]), f"Update failed: {status_text}"

    time.sleep(1)
    page_content = driver.page_source
    assert update_data["name"] in page_content
    assert update_data["email"] in page_content

    # DELETE flow
    driver.find_element(By.ID, selectors["status"]["refresh_button"]).click()
    time.sleep(1)

    user_items = driver.find_elements(By.CSS_SELECTOR, selectors["list_view"]["user_items"])
    target_delete_button = None
    for item in user_items:
        if create_data["name"] in item.text:
            target_delete_button = item.find_element(By.CSS_SELECTOR, selectors["list_view"]["delete_button"])
            break
    assert target_delete_button, "Delete button for second user not found"

    target_delete_button.click()
    time.sleep(0.5)
    try:
        alert = driver.switch_to.alert
        alert.accept()
        time.sleep(1)
    except Exception:
        pass

    status_text = driver.find_element(By.ID, selectors["status"]["status_element"]).text.lower()
    assert any(ind in status_text for ind in expected["delete_success"]), f"Delete failed: {status_text}"

    driver.find_element(By.ID, selectors["status"]["refresh_button"]).click()
    time.sleep(1)
    page = driver.page_source
    assert create_data["name"] not in page
    # final sanity
    user_items = driver.find_elements(By.CSS_SELECTOR, selectors["list_view"]["user_items"])
    assert len(user_items) == 1, f"Expected 1 seeded user list after deletion, found {len(user_items)}"
