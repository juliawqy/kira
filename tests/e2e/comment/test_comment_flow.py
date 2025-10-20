import time
import os
import pytest
from selenium.webdriver.common.by import By
from sqlalchemy.orm import Session
from backend.src.database.db_setup import Base
from backend.src.database.models.user import User
from backend.src.database.models.project import Project
from backend.src.database.models.task import Task


@pytest.fixture
def test_comment_data():
    """Static test data for predictable workflow."""
    return {
        "task_id": 1,
        "user_id": 2,
        "create_comment": "Initial test comment",
        "update_comment": "Updated comment text",
        "expected_messages": {
            "create_success": "comment added successfully",
            "update_success": "comment updated successfully",
            "delete_success": "comment deleted successfully"
        },
    }


def test_complete_comment_crud_workflow_ui_only(driver, app_server, test_comment_data, reset_database):
    """Full UI workflow test for comment feature."""
    data = test_comment_data

    # Seed required entities into the isolated DB bound to app_server
    # We use the globally patched SessionLocal via reset_database fixture
    import backend.src.database.db_setup as db_setup
    with db_setup.SessionLocal() as session:
        # Create user, project, task
        session.add(User(user_id=data["user_id"], email="testuser@example.com", name="Test User", role="STAFF", admin=False, hashed_pw="x"))
        session.add(Project(project_id=1, project_name="UI Test Project", project_manager=data["user_id"], active=True))
        session.add(Task(id=data["task_id"], title="Test Task", description="Task used for comment testing", status="To-do", priority=5, project_id=1, active=True, recurring=False))
        session.commit()

    html_file = os.path.join(os.getcwd(), "frontend", "comment", "comment.html")
    from urllib.parse import quote
    # Pass API base and IDs via query string
    driver.get(f"file:///{html_file}?api={quote(app_server + '/task')}&task={data['task_id']}&user={data['user_id']}")
    time.sleep(1.5)

    # Verify starting empty state
    comments = driver.find_elements(By.CSS_SELECTOR, ".comment-item")
    assert len(comments) == 0, "Expected no comments initially"

    # ADD COMMENT
    driver.find_element(By.ID, "commentInput").send_keys(data["create_comment"])
    driver.find_element(By.ID, "submitComment").click()
    # Wait for async status
    status_ok = False
    for _ in range(6):
        status = driver.find_element(By.ID, "status").text.lower()
        if data["expected_messages"]["create_success"] in status:
            status_ok = True
            break
        time.sleep(0.5)
    assert status_ok, f"Comment creation failed; got: '{driver.find_element(By.ID, 'status').text}'"


    # VERIFY COMMENT IN LIST
    driver.find_element(By.ID, "refresh").click()
    time.sleep(2)
    comments = driver.find_elements(By.CSS_SELECTOR, ".comment-item")
    assert any(data["create_comment"] in c.text for c in comments), "Comment not found in list"

    # UPDATE COMMENT
    update_buttons = driver.find_elements(By.CSS_SELECTOR, ".btn-update")
    assert update_buttons, "No update buttons found"
    update_buttons[0].click()
    time.sleep(1)

    update_input = driver.find_element(By.CSS_SELECTOR, ".update-input")
    update_input.clear()
    update_input.send_keys(data["update_comment"])

    driver.find_element(By.CSS_SELECTOR, ".btn-save").click()
    # Wait for async status
    status_ok = False
    for _ in range(6):
        status = driver.find_element(By.ID, "status").text.lower()
        if data["expected_messages"]["update_success"] in status:
            status_ok = True
            break
        time.sleep(0.5)
    assert status_ok, f"Comment update failed; got: '{driver.find_element(By.ID, 'status').text}'"

    # VERIFY UPDATED TEXT
    driver.find_element(By.ID, "refresh").click()
    time.sleep(2)
    page_content = driver.page_source
    assert data["update_comment"] in page_content, "Updated comment not visible"

    # DELETE COMMENT
    delete_buttons = driver.find_elements(By.CSS_SELECTOR, ".btn-delete")
    assert delete_buttons, "No delete buttons found"
    delete_buttons[0].click()
    time.sleep(1)

    # Confirm delete if alert appears
    try:
        alert = driver.switch_to.alert
        alert.accept()
    except Exception:
        pass
    # Wait for async status
    status_ok = False
    for _ in range(6):
        status = driver.find_element(By.ID, "status").text.lower()
        if "comment" in status and ("deleted" in status or "loaded" in status or "success" in status):
            status_ok = True
            break
        time.sleep(0.5)
    assert status_ok, f"Comment deletion failed; got: '{driver.find_element(By.ID, 'status').text}'"


    # FINAL VERIFY EMPTY
    driver.find_element(By.ID, "refresh").click()
    time.sleep(2)
    comments = driver.find_elements(By.CSS_SELECTOR, ".comment-item")
    assert len(comments) == 0, "Expected no comments after deletion"

