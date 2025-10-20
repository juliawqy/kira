import time
import os
import pytest
from selenium.webdriver.common.by import By
from backend.src.database.db_setup import Base
from backend.src.database.models.user import User
from backend.src.database.models.project import Project
from backend.src.database.models.task import Task
from tests.mock_data.comment.e2e_data import E2E_COMMENT_WORKFLOW, E2E_SELECTORS


@pytest.fixture
def test_comment_data():
    """Static test data for predictable workflow."""
    return E2E_COMMENT_WORKFLOW

# E2E-111/001
def test_complete_comment_crud_workflow_ui_only(driver, app_server, test_comment_data, reset_database):
    """Full UI workflow test for comment feature."""
    data = test_comment_data
    ids = data["entity_ids"]
    selectors = E2E_SELECTORS

    # Seed required entities into the isolated DB bound to app_server
    import backend.src.database.db_setup as db_setup
    with db_setup.SessionLocal() as session:
        user_cfg = data["user"]
        project_cfg = data["project"]
        task_cfg = data["task"]

        session.add(
            User(
                user_id=ids["user_id"],
                email=user_cfg["email"],
                name=user_cfg["name"],
                role=user_cfg["role"],
                admin=user_cfg["admin"],
                hashed_pw=user_cfg["hashed_pw"],
            )
        )
        session.add(
            Project(
                project_id=ids["project_id"],
                project_name=project_cfg["project_name"],
                project_manager=ids["user_id"],
                active=project_cfg["active"],
            )
        )
        session.add(
            Task(
                id=ids["task_id"],
                title=task_cfg["title"],
                description=task_cfg["description"],
                status=task_cfg["status"],
                priority=task_cfg["priority"],
                project_id=ids["project_id"],
                active=task_cfg["active"],
                recurring=task_cfg["recurring"],
            )
        )
        session.commit()

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
