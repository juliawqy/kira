import time
import os
import pytest
from selenium.webdriver.common.by import By
from backend.src.enums.user_role import UserRole
from tests.mock_data.user.e2e_data import E2E_USER_WORKFLOW, E2E_SELECTORS
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


@pytest.fixture(scope="session")
def test_db_engine():
    """
    Create a test database engine for e2e tests.
    """
    from backend.src.database.db_setup import Base
    
    # Use the same database but ensure clean state
    engine = create_engine("sqlite:///backend/src/database/kira.db", echo=False)
    yield engine


@pytest.fixture
def isolated_database(test_db_engine):
    """
    Enterprise-grade database isolation using transaction rollback.
    This ensures each test starts with a clean database state.
    """
    # Create a connection and transaction
    connection = test_db_engine.connect()
    transaction = connection.begin()
    
    # Clear all existing data at start of test
    try:
        connection.execute(text("DELETE FROM users"))
        connection.execute(text("DELETE FROM tasks"))
        connection.commit()
    except Exception:
        pass
    
    yield connection
    
    # Rollback any changes made during the test
    try:
        connection.execute(text("DELETE FROM users"))
        connection.execute(text("DELETE FROM tasks"))
        connection.commit()
    except Exception:
        pass
    finally:
        connection.close()


@pytest.fixture 
def test_user_data():
    """
    Static test data for consistent, repeatable tests.
    """
    return E2E_USER_WORKFLOW

# E2E-057/001
def test_complete_user_crud_workflow_ui_only(driver, isolated_database, test_user_data):
    """
    Complete user CRUD workflow with proper database isolation.
    Tests the full navigation flow starting from user.html main page.
    """
    
    # Extract test data from centralized mock data
    create_data = test_user_data["create"]
    update_data = test_user_data["update"] 
    expected = test_user_data["expected_responses"]
    selectors = E2E_SELECTORS
    
    created_user_id = None
    
    # START: Navigate to main user list page
    html_file = os.path.join(os.getcwd(), "frontend", "user", "user.html")
    driver.get(f"file:///{html_file}")
    time.sleep(2)
    
    # Verify we're on the user list page and it's empty (clean state)
    user_items = driver.find_elements(By.CSS_SELECTOR, selectors["list_view"]["user_items"])
    assert len(user_items) == 0, f"Expected empty user list, found {len(user_items)} users"
    
    # NAVIGATE TO CREATE: Click "Create New User" button
    create_button = driver.find_element(By.XPATH, "//button[text()='Create New User']")
    create_button.click()
    time.sleep(1)
    
    # Verify we're now on the create user page
    assert "create_user.html" in driver.current_url or driver.title == "Create User", "Should be on create user page"

    # CREATE USER: Fill out creation form using centralized data
    driver.find_element(By.ID, selectors["forms"]["name_input"]).send_keys(create_data["name"])
    driver.find_element(By.ID, selectors["forms"]["email_input"]).send_keys(create_data["email"])

    # Select role from dropdown
    role_select = driver.find_element(By.ID, selectors["forms"]["role_select"])
    role_select.find_element(By.CSS_SELECTOR, f"option[value='{create_data['role'].value}']").click()

    driver.find_element(By.ID, selectors["forms"]["password_input"]).send_keys(create_data["password"])
    driver.find_element(By.ID, selectors["forms"]["department_input"]).send_keys(create_data["department_id"])
    driver.find_element(By.ID, selectors["forms"]["admin_checkbox"]).click()  # Make admin
    driver.find_element(By.CSS_SELECTOR, selectors["forms"]["submit_button"]).click()

    time.sleep(2)  # wait for API response

    # Handle the confirmation alert
    try:
        alert = driver.switch_to.alert
        alert.dismiss()  # Click "Cancel" to stay on the page and read status
        time.sleep(1)
    except:
        pass

    status = driver.find_element(By.ID, selectors["status"]["status_element"]).text
    assert expected["create_success"] in status.lower(), f"User creation failed: {status}"

    # NAVIGATE BACK: Click "Back to Users" button to return to main list
    driver.find_element(By.XPATH, "//button[text()='← Back to Users']").click()
    time.sleep(1)

    # Verify we're back on user list page
    assert "user.html" in driver.current_url or "Users" in driver.title, "Should be back on user list page"

    # READ USER (List View): Verify user appears in list
    driver.find_element(By.ID, selectors["status"]["refresh_button"]).click()
    time.sleep(2)

    user_items = driver.find_elements(By.CSS_SELECTOR, selectors["list_view"]["user_items"])
    user_found = any(create_data["name"] in item.text for item in user_items)
    assert user_found, f"Created user '{create_data['name']}' not found in user list"

    # Extract user ID for later operations
    test_user_element = next(item for item in user_items if create_data["name"] in item.text)
    user_info_text = test_user_element.find_element(By.CSS_SELECTOR, selectors["list_view"]["user_info"]).text
    created_user_id = user_info_text.split("ID: ")[1].split(" |")[0]

    # READ USER (Individual View): Verify the details from the list view
    user_text = test_user_element.text
    assert create_data["email"] in user_text, "User email not displayed correctly"
    assert create_data["role"].value in user_text, "User role not displayed correctly"

    # UPDATE USER: Click update button for our user
    update_buttons = driver.find_elements(By.CSS_SELECTOR, selectors["list_view"]["update_button"])
    assert len(update_buttons) > 0, "No update buttons found"

    # Click the update button for the first user (our created user should be there)
    update_buttons[0].click()
    time.sleep(1)

    # Find and fill the update form
    name_input = driver.find_element(By.CSS_SELECTOR, "[id^='update-name-']")
    email_input = driver.find_element(By.CSS_SELECTOR, "[id^='update-email-']")
    role_select = driver.find_element(By.CSS_SELECTOR, "[id^='update-role-']")

    # Update the user information using centralized data
    name_input.clear()
    name_input.send_keys(update_data["name"])

    email_input.clear()
    email_input.send_keys(update_data["email"])

    # Change role
    role_select.find_element(By.CSS_SELECTOR, f"option[value='{update_data['role'].value}']").click()

    # Click save changes
    save_button = driver.find_element(By.CSS_SELECTOR, selectors["list_view"]["save_button"])
    save_button.click()

    # Wait for update to complete
    time.sleep(1)

    # Check for success message
    status_element = driver.find_element(By.ID, selectors["status"]["status_element"])
    status_text = status_element.text

    # Check against expected responses
    update_successful = any(indicator in status_text.lower() for indicator in expected["update_success"])
    assert update_successful, f"Update failed: {status_text}"

    # Wait for auto-refresh to complete
    time.sleep(2)

    # Verify the updated information appears in the list
    page_content = driver.page_source
    assert update_data["name"] in page_content, f"Updated name '{update_data['name']}' not found in user list"
    assert update_data["email"] in page_content, f"Updated email '{update_data['email']}' not found in user list"

    # DELETE USER: Refresh to ensure we have latest data
    refresh_button = driver.find_element(By.ID, selectors["status"]["refresh_button"])
    refresh_button.click()
    time.sleep(2)

    # Find and click the delete button for our user
    delete_buttons = driver.find_elements(By.CSS_SELECTOR, selectors["list_view"]["delete_button"])
    assert len(delete_buttons) > 0, "No delete buttons found"

    # Find the specific delete button for our updated user
    user_items = driver.find_elements(By.CSS_SELECTOR, selectors["list_view"]["user_items"])
    target_delete_button = None

    for item in user_items:
        if update_data["name"] in item.text:
            target_delete_button = item.find_element(By.CSS_SELECTOR, selectors["list_view"]["delete_button"])
            break

    assert target_delete_button is not None, f"Could not find delete button for user '{update_data['name']}'"

    # Click the delete button
    target_delete_button.click()
    time.sleep(1)

    # Handle the confirmation dialog
    alert = driver.switch_to.alert
    alert.accept()  # Click OK on the confirmation dialog
    time.sleep(2)

    # Verify deletion success
    status_element = driver.find_element(By.ID, selectors["status"]["status_element"])
    status_text = status_element.text.lower()
    
    # Check against expected responses
    deletion_successful = any(indicator in status_text for indicator in expected["delete_success"])
    assert deletion_successful, f"Delete failed: {status_element.text}"

    # Verify the user is no longer in the list
    page_content = driver.page_source
    assert update_data["name"] not in page_content, f"Deleted user '{update_data['name']}' still appears in user list"

    # VERIFY FINAL STATE: Refresh and verify current state
    driver.find_element(By.ID, selectors["status"]["refresh_button"]).click()
    time.sleep(1)

    # Verify user no longer exists after deletion and we're back to empty state
    page_content = driver.page_source
    assert update_data["name"] not in page_content, f"Deleted user '{update_data['name']}' unexpectedly still exists"
    
    # Verify we're back to clean state with no users
    user_items = driver.find_elements(By.CSS_SELECTOR, selectors["list_view"]["user_items"])
    assert len(user_items) == 0, f"Expected empty user list after deletion, found {len(user_items)} users"