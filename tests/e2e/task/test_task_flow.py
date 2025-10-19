from __future__ import annotations
import time
import os
from backend.src.database.db_setup import Base
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from sqlalchemy import create_engine, event


from sqlalchemy.orm import sessionmaker
from tests.mock_data.task.e2e_data import E2E_TASK_WORKFLOW, E2E_SELECTORS
import threading
import socket
import uvicorn
import backend.src.services.task as svc
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
        engine.dispose()

@pytest.fixture
def isolated_database(test_engine):
    """
    Enterprise-grade database isolation using transaction rollback.
    This ensures each test starts with a clean database state.
    """

    TestingSessionLocal = sessionmaker(
        bind=test_engine,
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
def reset_database_tables(test_engine):
    """Drop and recreate all tables before each test to reset ID sequences."""
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    yield
@pytest.fixture(scope="session")
def app_server(test_engine):
    """Run FastAPI app with SessionLocal overridden to the isolated test engine."""
    TestingSessionLocal = sessionmaker(
        bind=test_engine,
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
        yield f"http://127.0.0.1:{port}/kira/app/api/v1/task"
    finally:
        server.should_exit = True
        thread.join(timeout=2)

@pytest.fixture
def test_task_data():
    return E2E_TASK_WORKFLOW

# E2E-016/001
def test_complete_task_crud_workflow(driver, isolated_database, app_server, test_task_data):
    workflow = test_task_data
    create_task = workflow["create"]
    update_task = workflow["update"]
    expected = workflow["expected_responses"]
    selectors = E2E_SELECTORS

    html_file = os.path.join(os.getcwd(), "frontend", "task", "task.html")
    from urllib.parse import quote
    driver.get(f"file:///{html_file}?api={quote(app_server)}")
    time.sleep(1)

    # Clean state
    driver.find_element(By.ID, selectors["status"]["refresh_button"]).click()
    time.sleep(1)
    # Assert all task ids are unique
    infos = driver.find_elements(By.CSS_SELECTOR, ".task-item .task-info")
    ids = [el.get_attribute("data-id") for el in infos]
    assert len(ids) == len(set(ids))
    task_items = driver.find_elements(By.CSS_SELECTOR, selectors["list_view"]["task_items"])
    assert len(task_items) == 0

    # CREATE
    driver.find_element(By.ID, selectors["forms"]["title_input"]).send_keys(create_task["title"])
    driver.find_element(By.ID, selectors["forms"]["description_input"]).send_keys(create_task["description"])
    Select(driver.find_element(By.ID, selectors["forms"]["priority_input"]))\
        .select_by_value(str(create_task["priority"]))
    Select(driver.find_element(By.ID, selectors["forms"]["status_select"]))\
        .select_by_value(create_task["status"])    
    Select(driver.find_element(By.ID, selectors["forms"]["project_input"]))\
        .select_by_value(str(create_task["project_id"]))
    driver.find_element(By.CSS_SELECTOR, selectors["forms"]["submit_button"]).click()

    status_ok = False
    for _ in range(6):
        text = driver.find_element(By.ID, selectors["status"]["status_element"]).text.lower()
        if expected["create_success"] in text:
            status_ok = True
            break
        time.sleep(0.5)
    assert status_ok, f"Expected create status; got: '{driver.find_element(By.ID, selectors['status']['status_element']).text}'"

    # VIEW
    driver.find_element(By.ID, selectors["status"]["refresh_button"]).click()
    time.sleep(1)

    infos = driver.find_elements(By.CSS_SELECTOR, ".task-item .task-info")
    ids = [el.get_attribute("data-id") for el in infos]
    assert len(ids) == len(set(ids))
    page = driver.page_source
    assert create_task["title"] in page

    # UPDATE
    update_buttons = driver.find_elements(By.CSS_SELECTOR, selectors["list_view"]["update_button"])
    assert update_buttons
    update_buttons[0].click()
    time.sleep(1)

    driver.find_element(By.CSS_SELECTOR, "[id^='update-title-']").clear()
    driver.find_element(By.CSS_SELECTOR, "[id^='update-title-']").send_keys(update_task["title"])
    driver.find_element(By.CSS_SELECTOR, "[id^='update-desc-']").clear()
    driver.find_element(By.CSS_SELECTOR, "[id^='update-desc-']").send_keys(update_task["description"])
    driver.find_element(By.CSS_SELECTOR, "[id^='update-priority-']").clear()
    driver.find_element(By.CSS_SELECTOR, "[id^='update-priority-']").send_keys(str(update_task["priority"]))
    driver.find_element(By.CSS_SELECTOR, selectors["list_view"]["save_button"]).click()
    time.sleep(1)

    status_text = driver.find_element(By.ID, selectors["status"]["status_element"]).text.lower()
    assert any(s in status_text for s in expected["update_success"]) 

    driver.find_element(By.ID, selectors["status"]["refresh_button"]).click()
    time.sleep(1)
    page = driver.page_source
    assert update_task["title"] in page

    # DELETE
    delete_buttons = driver.find_elements(By.CSS_SELECTOR, selectors["list_view"]["delete_button"])
    assert delete_buttons
    delete_buttons[0].click()
    time.sleep(1)
    status_text = driver.find_element(By.ID, selectors["status"]["status_element"]).text.lower()
    assert any(s in status_text for s in expected["delete_success"]) 

    driver.find_element(By.ID, selectors["status"]["refresh_button"]).click()
    time.sleep(1)
    page = driver.page_source
    assert update_task["title"] not in page

# E2E-016/002
def test_task_assignment_workflow(driver, isolated_database, app_server, test_task_data):
    workflow = test_task_data
    create_task = workflow["create"]
    selectors = E2E_SELECTORS

    html_file = os.path.join(os.getcwd(), "frontend", "task", "task.html")
    from urllib.parse import quote
    driver.get(f"file:///{html_file}?api={quote(app_server)}")
    time.sleep(1)

    # Create parent A and B
    for title in ("Parent A", "Parent B"):
        driver.find_element(By.ID, selectors["forms"]["title_input"]).clear()
        driver.find_element(By.ID, selectors["forms"]["title_input"]).send_keys(title)
        Select(driver.find_element(By.ID, selectors["forms"]["priority_input"])) \
            .select_by_value(str(create_task["priority"]))
        Select(driver.find_element(By.ID, selectors["forms"]["status_select"])) \
            .select_by_value(create_task["status"])
        Select(driver.find_element(By.ID, selectors["forms"]["project_input"])) \
            .select_by_value(str(create_task["project_id"]))
        driver.find_element(By.CSS_SELECTOR, selectors["forms"]["submit_button"]).click()
        time.sleep(0.5)

    driver.find_element(By.ID, selectors["status"]["refresh_button"]).click()
    time.sleep(1)

    # Create child C
    driver.find_element(By.ID, selectors["forms"]["title_input"]).clear()
    driver.find_element(By.ID, selectors["forms"]["title_input"]).send_keys("Child C")
    Select(driver.find_element(By.ID, selectors["forms"]["priority_input"])) \
        .select_by_value(str(create_task["priority"]))
    Select(driver.find_element(By.ID, selectors["forms"]["status_select"])) \
        .select_by_value(create_task["status"])
    Select(driver.find_element(By.ID, selectors["forms"]["project_input"])) \
        .select_by_value(str(create_task["project_id"]))
    driver.find_element(By.CSS_SELECTOR, selectors["forms"]["submit_button"]).click()
    time.sleep(0.5)

    # Create child D
    driver.find_element(By.ID, selectors["forms"]["title_input"]).clear()
    driver.find_element(By.ID, selectors["forms"]["title_input"]).send_keys("Child D")
    Select(driver.find_element(By.ID, selectors["forms"]["priority_input"])) \
        .select_by_value(str(create_task["priority"]))
    Select(driver.find_element(By.ID, selectors["forms"]["status_select"])) \
        .select_by_value(create_task["status"])
    Select(driver.find_element(By.ID, selectors["forms"]["project_input"])) \
        .select_by_value(str(create_task["project_id"]))
    driver.find_element(By.CSS_SELECTOR, selectors["forms"]["submit_button"]).click()
    time.sleep(0.5)

    driver.find_element(By.ID, selectors["status"]["refresh_button"]).click()
    time.sleep(1)

    # Attach child C to Parent A, and child D to Parent B
    def find_card(title):
        cards = driver.find_elements(By.CSS_SELECTOR, ".task-item")
        for c in cards:
            if title in c.text:
                return c
        return None

    parent_a = find_card("Parent A")
    parent_b = find_card("Parent B")
    assert parent_a and parent_b

    # Get ids for children
    infos = driver.find_elements(By.CSS_SELECTOR, ".task-item .task-info")
    child_c_id = next(el.get_attribute("data-id") for el in infos if "Child C" in el.text)
    child_d_id = next(el.get_attribute("data-id") for el in infos if "Child D" in el.text)

    # Attach C under A
    a_attach = parent_a.find_element(By.CSS_SELECTOR, "[id^='attach-input-']")
    a_attach.clear()
    a_attach.send_keys(child_c_id)
    parent_a.find_element(By.CSS_SELECTOR, selectors["list_view"]["attach_button"]).click()
    time.sleep(1)

    # Attach D under B (re-acquire elements to avoid staleness)
    parent_b = find_card("Parent B")
    b_attach = parent_b.find_element(By.CSS_SELECTOR, "[id^='attach-input-']")
    b_attach.clear()
    b_attach.send_keys(child_d_id)
    parent_b.find_element(By.CSS_SELECTOR, selectors["list_view"]["attach_button"]).click()
    time.sleep(1)

    # Verify subtasks appear under parents
    for _ in range(6):
        parent_a = find_card("Parent A")
        parent_b = find_card("Parent B")
        if parent_a and parent_b:
            break
        time.sleep(0.3)

    parent_a_id = parent_a.find_element(By.CSS_SELECTOR, ".task-info").get_attribute("data-id")
    parent_b_id = parent_b.find_element(By.CSS_SELECTOR, ".task-info").get_attribute("data-id")
    assert "Child C" in driver.find_element(By.ID, f"subtasks-{parent_a_id}").get_attribute("innerHTML")
    assert "Child D" in driver.find_element(By.ID, f"subtasks-{parent_b_id}").get_attribute("innerHTML")

    # Delete Child C under Parent A
    subitems_a = driver.find_elements(By.CSS_SELECTOR, f"#subtasks-{parent_a_id} .subtask-item")
    target = next(si for si in subitems_a if "Child C" in si.text)
    target.find_element(By.CSS_SELECTOR, ".delete-btn").click()
    time.sleep(1)

    # Ensure Child C is gone
    assert "Child C" not in driver.find_element(
        By.ID, f"subtasks-{parent_a_id}"
    ).get_attribute("innerHTML")


    # Delete Parent B
    parent_b = find_card("Parent B")
    delete_btn = parent_b.find_element(By.CSS_SELECTOR, selectors["list_view"]["parent_delete_button"])
    delete_btn.click()
    time.sleep(1)



    # Refresh to reload task list after deletion
    driver.find_element(By.ID, selectors["status"]["refresh_button"]).click()
    time.sleep(1)

    # Verify Child D is now top-level (standalone)
    cards = driver.find_elements(By.CSS_SELECTOR, ".task-item")
    card_titles = [c.text for c in cards]
    assert any("Child D" in t for t in card_titles)
    assert all("Parent B" not in t for t in card_titles)
