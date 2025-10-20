import time
import os
import pytest
from selenium.webdriver.common.by import By
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


@pytest.fixture(scope="session")
def test_db_engine():
    """Connect to same SQLite database used by backend."""
    from backend.src.database.db_setup import Base
    engine = create_engine("sqlite:///backend/src/database/kira.db", echo=False)
    yield engine


@pytest.fixture
def isolated_database(test_db_engine):
    """Ensure clean comment/task state for each E2E test + insert task/user rows."""
    connection = test_db_engine.connect()
    transaction = connection.begin()

    try:
        connection.execute(text("DELETE FROM comment"))
        connection.execute(text("DELETE FROM task"))
        connection.execute(text("DELETE FROM user"))
        connection.execute(text("DELETE FROM project"))

        connection.execute(text("""
            INSERT INTO user (user_id, email, name, role, admin, hashed_pw, department_id)
            VALUES (2, 'testuser@example.com', 'Test User', 'STAFF', 0, 'hashed_pw_dummy', NULL)
        """))

        connection.execute(text("""
            INSERT INTO project (project_id, project_name, project_manager, active)
            VALUES (1, 'UI Test Project', 2, 1)
        """))

        connection.execute(text("""
            INSERT INTO task (id, title, description, status, priority, project_id, active, recurring)
            VALUES (1, 'Test Task', 'Task used for comment testing', 'To-do', 5, 1, 1, 0)
        """))


        connection.commit()
    except Exception as e:
        print("Setup failed:", e)
        connection.rollback()

    yield connection

    # Clean up after test
    try:
        connection.execute(text("DELETE FROM comment"))
        connection.execute(text("DELETE FROM task"))
        connection.execute(text("DELETE FROM user"))
        connection.execute(text("DELETE FROM project"))
        connection.commit()
    except Exception as e:
        print("Teardown failed:", e)
        connection.rollback()
    finally:
        connection.close()



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


def test_complete_comment_crud_workflow_ui_only(driver, isolated_database, test_comment_data):
    """Full UI workflow test for comment feature."""
    data = test_comment_data
    html_file = os.path.join(os.getcwd(), "frontend", "comment", "comment.html")
    driver.get(f"file:///{html_file}")
    time.sleep(2)

    # Verify starting empty state
    comments = driver.find_elements(By.CSS_SELECTOR, ".comment-item")
    assert len(comments) == 0, "Expected no comments initially"

    # ADD COMMENT
    driver.find_element(By.ID, "commentInput").send_keys(data["create_comment"])
    driver.find_element(By.ID, "submitComment").click()
    time.sleep(1)

    status = driver.find_element(By.ID, "status").text.lower()
    assert data["expected_messages"]["create_success"] in status.lower(), "Comment creation failed"


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
    time.sleep(1)

    status = driver.find_element(By.ID, "status").text.lower()
    assert data["expected_messages"]["update_success"] in status, "Comment update failed"

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

    alert = driver.switch_to.alert
    alert.accept()
    time.sleep(1)

    status = driver.find_element(By.ID, "status").text.lower()
    assert "comment" in status and ("deleted" in status or "loaded" in status), "Comment deletion failed"


    # FINAL VERIFY EMPTY
    driver.find_element(By.ID, "refresh").click()
    time.sleep(2)
    comments = driver.find_elements(By.CSS_SELECTOR, ".comment-item")
    assert len(comments) == 0, "Expected no comments after deletion"

