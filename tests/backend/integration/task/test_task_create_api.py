# tests/backend/integration/task/test_task_create_api.py
from __future__ import annotations

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from fastapi.testclient import TestClient

from backend.src.enums.task_status import TaskStatus
from tests.mock_data.task.integration_data import (
    TASK_CREATE_MINIMAL,
    TASK_CREATE_FULL,
    TASK_CREATE_PRIORITY_TOO_LOW,
    TASK_CREATE_PRIORITY_TOO_HIGH,
    TASK_CREATE_INVALID_STATUS,
    TASK_CREATE_MISSING_TITLE,
    TASK_CREATE_MISSING_PROJECT_ID,
    TASK_CREATE_EMPTY_TITLE,
    TASK_CREATE_PARENT,
    TASK_CREATE_CHILD_TEMPLATE,
    TASK_CREATE_NONEXISTENT_PARENT,
    TASK_CREATE_INACTIVE_PARENT_CHILD,
    TASK_CREATE_VALID_DATES,
    TASK_CREATE_INVALID_DATE,
    TASK_CREATE_PRIORITY_MIN,
    TASK_CREATE_PRIORITY_MAX,
    TASK_CREATE_STATUS_TODO,
    TASK_CREATE_STATUS_IN_PROGRESS,
    TASK_CREATE_STATUS_COMPLETED,
    TASK_CREATE_STATUS_BLOCKED,
    TASK_CREATE_NULL_FIELDS,
    TASK_CREATE_LONG_TEXT,
    TASK_CREATE_SPECIAL_CHARS,
    TASK_CREATE_PROJECT_1,
    TASK_CREATE_PROJECT_2,
    TASK_CREATE_PROJECT_3,
    TASK_CREATE_RESPONSE_TEST,
    EXPECTED_RESPONSE_FIELDS,
    EXPECTED_TASK_MINIMAL_RESPONSE,
    EXPECTED_TASK_FULL_RESPONSE,
    EXPECTED_PARENT_TASK_RESPONSE,
    EXPECTED_CHILD_TASK_RESPONSE,
    EXPECTED_EMPTY_TITLE_RESPONSE,
    EXPECTED_VALID_DATES_RESPONSE,
    EXPECTED_TASK_TODO_RESPONSE,
    EXPECTED_TASK_IN_PROGRESS_RESPONSE,
    EXPECTED_TASK_COMPLETED_RESPONSE,
    EXPECTED_TASK_BLOCKED_RESPONSE
)

@pytest.fixture
def test_db_session(test_engine):
    """
    Create a database session using the same SessionLocal as the API.
    This ensures both API and tests see the same data.
    """
    from sqlalchemy.orm import sessionmaker
    TestingSessionLocal = sessionmaker(
        bind=test_engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
        future=True,
    )
    
    with TestingSessionLocal() as session:
        yield session

@pytest.fixture
def verify_database_state(test_db_session):
    """
    Fixture to verify database state before and after tests.
    """
    def _verify_state():
        result = test_db_session.execute(text("SELECT COUNT(*) FROM task"))
        count = result.scalar()
        return count
    
    initial_count = _verify_state()
    yield _verify_state
    final_count = _verify_state()
    
    if final_count != initial_count:
        print(f"Database state changed: {initial_count} -> {final_count} tasks")

# INT-001/001
def test_create_task_minimal(client, task_base_path, test_db_session, verify_database_state):
    """Create task with minimal required fields"""
    initial_count = verify_database_state()
    
    response = client.post(f"{task_base_path}/", json=TASK_CREATE_MINIMAL)
    assert response.status_code == 201
    
    data = response.json()
    task_id = data["id"]
    
    assert data["title"] == EXPECTED_TASK_MINIMAL_RESPONSE["title"]
    assert data["project_id"] == EXPECTED_TASK_MINIMAL_RESPONSE["project_id"]
    assert data["status"] == EXPECTED_TASK_MINIMAL_RESPONSE["status"]
    assert data["priority"] == EXPECTED_TASK_MINIMAL_RESPONSE["priority"]
    assert data["active"] == EXPECTED_TASK_MINIMAL_RESPONSE["active"]
    assert data["description"] == EXPECTED_TASK_MINIMAL_RESPONSE["description"]
    assert data["start_date"] == EXPECTED_TASK_MINIMAL_RESPONSE["start_date"]
    assert data["deadline"] == EXPECTED_TASK_MINIMAL_RESPONSE["deadline"]
    assert "id" in data
    
    for field in EXPECTED_RESPONSE_FIELDS:
        assert field in data

    db_result = test_db_session.execute(
        text("SELECT title, project_id, status, priority, active, description FROM task WHERE id = :id"), 
        {"id": task_id}
    ).fetchone()
    assert db_result is not None
    assert db_result[0] == EXPECTED_TASK_MINIMAL_RESPONSE["title"]
    assert db_result[1] == EXPECTED_TASK_MINIMAL_RESPONSE["project_id"] 
    assert db_result[2] == EXPECTED_TASK_MINIMAL_RESPONSE["status"]
    assert db_result[3] == EXPECTED_TASK_MINIMAL_RESPONSE["priority"]
    assert db_result[4] == 1
    assert db_result[5] == EXPECTED_TASK_MINIMAL_RESPONSE["description"]

    final_count = verify_database_state()
    assert final_count == initial_count + 1

# INT-001/002
def test_create_task_full_details(client, task_base_path, test_db_session, verify_database_state):
    """Create task with all fields populated - Full stack test"""
    initial_count = verify_database_state()
    
    response = client.post(f"{task_base_path}/", json=TASK_CREATE_FULL)
    assert response.status_code == 201
    
    data = response.json()
    task_id = data["id"]
    
    assert data["title"] == EXPECTED_TASK_FULL_RESPONSE["title"]
    assert data["description"] == EXPECTED_TASK_FULL_RESPONSE["description"]
    assert data["project_id"] == EXPECTED_TASK_FULL_RESPONSE["project_id"]
    assert data["priority"] == EXPECTED_TASK_FULL_RESPONSE["priority"]
    assert data["status"] == EXPECTED_TASK_FULL_RESPONSE["status"]
    assert data["active"] == EXPECTED_TASK_FULL_RESPONSE["active"]
    assert data["start_date"] == EXPECTED_TASK_FULL_RESPONSE["start_date"]
    assert data["deadline"] == EXPECTED_TASK_FULL_RESPONSE["deadline"]

    db_result = test_db_session.execute(
        text("SELECT title, description, priority, status, project_id, active FROM task WHERE id = :id"), 
        {"id": task_id}
    ).fetchone()
    assert db_result is not None
    assert db_result[0] == EXPECTED_TASK_FULL_RESPONSE["title"]
    assert db_result[1] == EXPECTED_TASK_FULL_RESPONSE["description"]
    assert db_result[2] == EXPECTED_TASK_FULL_RESPONSE["priority"]
    assert db_result[3] == EXPECTED_TASK_FULL_RESPONSE["status"]
    assert db_result[4] == EXPECTED_TASK_FULL_RESPONSE["project_id"]
    assert db_result[5] == 1

    final_count = verify_database_state()
    assert final_count == initial_count + 1

# INT-001/003
def test_create_task_priority_validation_low(client, task_base_path):
    """Create task with priority below minimum"""
    response = client.post(f"{task_base_path}/", json=TASK_CREATE_PRIORITY_TOO_LOW)
    assert response.status_code == 422

# INT-001/004
def test_create_task_priority_validation_high(client, task_base_path):
    """Create task with priority above maximum"""
    response = client.post(f"{task_base_path}/", json=TASK_CREATE_PRIORITY_TOO_HIGH)
    assert response.status_code == 422

# INT-001/005
def test_create_task_invalid_status(client, task_base_path):
    """Create task with invalid status value"""
    response = client.post(f"{task_base_path}/", json=TASK_CREATE_INVALID_STATUS)
    assert response.status_code == 422

# INT-001/006
def test_create_task_missing_title(client, task_base_path):
    """Create task without required title field"""
    response = client.post(f"{task_base_path}/", json=TASK_CREATE_MISSING_TITLE)
    assert response.status_code == 422

# INT-001/007
def test_create_task_missing_project_id(client, task_base_path):
    """Create task without required project_id field"""
    response = client.post(f"{task_base_path}/", json=TASK_CREATE_MISSING_PROJECT_ID)
    assert response.status_code == 422

# INT-001/008
def test_create_task_empty_title(client, task_base_path, test_db_session, verify_database_state):
    """Create task with empty title"""
    initial_count = verify_database_state()
    
    response = client.post(f"{task_base_path}/", json=TASK_CREATE_EMPTY_TITLE)
    assert response.status_code == 201
    
    data = response.json()
    task_id = data["id"]
    
    assert data["title"] == EXPECTED_EMPTY_TITLE_RESPONSE["title"]
    assert data["project_id"] == EXPECTED_EMPTY_TITLE_RESPONSE["project_id"]
    assert data["status"] == EXPECTED_EMPTY_TITLE_RESPONSE["status"]
    assert data["priority"] == EXPECTED_EMPTY_TITLE_RESPONSE["priority"]
    assert data["active"] == EXPECTED_EMPTY_TITLE_RESPONSE["active"]
    
    db_result = test_db_session.execute(
        text("SELECT title, project_id, status FROM task WHERE id = :id"), 
        {"id": task_id}
    ).fetchone()
    assert db_result is not None
    assert db_result[0] == EXPECTED_EMPTY_TITLE_RESPONSE["title"]
    assert db_result[1] == EXPECTED_EMPTY_TITLE_RESPONSE["project_id"]
    assert db_result[2] == EXPECTED_EMPTY_TITLE_RESPONSE["status"]
    
    final_count = verify_database_state()
    assert final_count == initial_count + 1

# INT-001/009
def test_create_task_with_parent(client, task_base_path, test_db_session, verify_database_state):
    """Create parent and child task relationship - Full stack test"""
    initial_count = verify_database_state()
    
    # Create parent task
    parent_response = client.post(f"{task_base_path}/", json=TASK_CREATE_PARENT)
    assert parent_response.status_code == 201
    parent_data = parent_response.json()
    parent_id = parent_data["id"]
    
    assert parent_data["title"] == EXPECTED_PARENT_TASK_RESPONSE["title"]
    assert parent_data["project_id"] == EXPECTED_PARENT_TASK_RESPONSE["project_id"]
    assert parent_data["status"] == EXPECTED_PARENT_TASK_RESPONSE["status"]
    assert parent_data["active"] == EXPECTED_PARENT_TASK_RESPONSE["active"]
    
    parent_db = test_db_session.execute(
        text("SELECT title, project_id, status, active FROM task WHERE id = :id"), 
        {"id": parent_id}
    ).fetchone()
    assert parent_db is not None
    assert parent_db[0] == EXPECTED_PARENT_TASK_RESPONSE["title"]
    assert parent_db[1] == EXPECTED_PARENT_TASK_RESPONSE["project_id"]
    assert parent_db[2] == EXPECTED_PARENT_TASK_RESPONSE["status"]
    assert parent_db[3] == 1
    
    child_payload = TASK_CREATE_CHILD_TEMPLATE.copy()
    child_payload["parent_id"] = parent_id
    child_response = client.post(f"{task_base_path}/", json=child_payload)
    assert child_response.status_code == 201
    
    child_data = child_response.json()
    child_id = child_data["id"]
    
    assert child_data["title"] == EXPECTED_CHILD_TASK_RESPONSE["title"]
    assert child_data["project_id"] == EXPECTED_CHILD_TASK_RESPONSE["project_id"]
    assert child_data["status"] == EXPECTED_CHILD_TASK_RESPONSE["status"]
    assert child_data["active"] == EXPECTED_CHILD_TASK_RESPONSE["active"]
    
    child_db = test_db_session.execute(
        text("SELECT title, project_id, status, active FROM task WHERE id = :id"), 
        {"id": child_id}
    ).fetchone()
    assert child_db is not None
    assert child_db[0] == EXPECTED_CHILD_TASK_RESPONSE["title"]
    assert child_db[1] == EXPECTED_CHILD_TASK_RESPONSE["project_id"]
    assert child_db[2] == EXPECTED_CHILD_TASK_RESPONSE["status"]
    assert child_db[3] == 1
    
    parent_assignment = test_db_session.execute(
        text("SELECT parent_id, subtask_id FROM parent_assignment WHERE parent_id = :parent_id AND subtask_id = :child_id"),
        {"parent_id": parent_id, "child_id": child_id}
    ).fetchone()
    assert parent_assignment is not None
    assert parent_assignment[0] == parent_id
    assert parent_assignment[1] == child_id
    
    final_count = verify_database_state()
    assert final_count == initial_count + 2

# INT-001/010
def test_create_task_with_nonexistent_parent(client, task_base_path):
    """Create task with non-existent parent ID"""
    response = client.post(f"{task_base_path}/", json=TASK_CREATE_NONEXISTENT_PARENT)
    assert response.status_code == 404

# INT-001/011
def test_create_task_with_inactive_parent(client, task_base_path, test_db_session, verify_database_state):
    """Create child task with inactive parent - Full stack test"""
    initial_count = verify_database_state()
    
    # Create parent task
    parent_response = client.post(f"{task_base_path}/", json=TASK_CREATE_PARENT)
    assert parent_response.status_code == 201
    parent_id = parent_response.json()["id"]
    
    delete_response = client.post(f"{task_base_path}/{parent_id}/delete")
    assert delete_response.status_code == 200
    
    parent_db = test_db_session.execute(
        text("SELECT active FROM task WHERE id = :id"), {"id": parent_id}
    ).fetchone()
    assert parent_db is not None
    assert parent_db[0] == 0
    
    child_payload = TASK_CREATE_INACTIVE_PARENT_CHILD.copy()
    child_payload["parent_id"] = parent_id
    response = client.post(f"{task_base_path}/", json=child_payload)
    assert response.status_code == 400
    
    child_count = test_db_session.execute(
        text("SELECT COUNT(*) FROM task WHERE title = :title"),
        {"title": child_payload["title"]}
    ).scalar()
    assert child_count == 0
    
    final_count = verify_database_state()
    assert final_count == initial_count + 1

# INT-001/012
def test_create_task_valid_dates(client, task_base_path, test_db_session, verify_database_state):
    """Create task with valid date formats"""
    initial_count = verify_database_state()
    
    response = client.post(f"{task_base_path}/", json=TASK_CREATE_VALID_DATES)
    assert response.status_code == 201
    
    data = response.json()
    task_id = data["id"]
    
    assert data["title"] == EXPECTED_VALID_DATES_RESPONSE["title"]
    assert data["project_id"] == EXPECTED_VALID_DATES_RESPONSE["project_id"]
    assert data["start_date"] == EXPECTED_VALID_DATES_RESPONSE["start_date"]
    assert data["deadline"] == EXPECTED_VALID_DATES_RESPONSE["deadline"]
    assert data["status"] == EXPECTED_VALID_DATES_RESPONSE["status"]
    assert data["priority"] == EXPECTED_VALID_DATES_RESPONSE["priority"]
    assert data["active"] == EXPECTED_VALID_DATES_RESPONSE["active"]
    
    db_result = test_db_session.execute(
        text("SELECT title, project_id, start_date, deadline FROM task WHERE id = :id"), 
        {"id": task_id}
    ).fetchone()
    assert db_result is not None
    assert db_result[0] == EXPECTED_VALID_DATES_RESPONSE["title"]
    assert db_result[1] == EXPECTED_VALID_DATES_RESPONSE["project_id"]
    assert db_result[2] == EXPECTED_VALID_DATES_RESPONSE["start_date"]
    assert db_result[3] == EXPECTED_VALID_DATES_RESPONSE["deadline"]
    
    final_count = verify_database_state()
    assert final_count == initial_count + 1

# INT-001/013
def test_create_task_invalid_date(client, task_base_path):
    """Create task with invalid date format"""
    response = client.post(f"{task_base_path}/", json=TASK_CREATE_INVALID_DATE)
    assert response.status_code == 422

# INT-001/014
def test_create_task_priority_boundaries(client, task_base_path):
    """Test priority boundary values"""
    min_response = client.post(f"{task_base_path}/", json=TASK_CREATE_PRIORITY_MIN)
    assert min_response.status_code == 201
    assert min_response.json()["priority"] == TASK_CREATE_PRIORITY_MIN["priority"]
    
    max_response = client.post(f"{task_base_path}/", json=TASK_CREATE_PRIORITY_MAX)
    assert max_response.status_code == 201
    assert max_response.json()["priority"] == TASK_CREATE_PRIORITY_MAX["priority"]

# INT-001/015
def test_create_task_status_todo(client, task_base_path, test_db_session, verify_database_state):
    """Create task with TO_DO status"""
    initial_count = verify_database_state()
    
    response = client.post(f"{task_base_path}/", json=TASK_CREATE_STATUS_TODO)
    assert response.status_code == 201
    
    data = response.json()
    task_id = data["id"]
    
    assert data["title"] == EXPECTED_TASK_TODO_RESPONSE["title"]
    assert data["status"] == EXPECTED_TASK_TODO_RESPONSE["status"]
    assert data["project_id"] == EXPECTED_TASK_TODO_RESPONSE["project_id"]
    assert data["priority"] == EXPECTED_TASK_TODO_RESPONSE["priority"]
    assert data["active"] == EXPECTED_TASK_TODO_RESPONSE["active"]
    
    db_result = test_db_session.execute(
        text("SELECT title, status, project_id FROM task WHERE id = :id"), 
        {"id": task_id}
    ).fetchone()
    assert db_result is not None
    assert db_result[0] == EXPECTED_TASK_TODO_RESPONSE["title"]
    assert db_result[1] == EXPECTED_TASK_TODO_RESPONSE["status"]
    assert db_result[2] == EXPECTED_TASK_TODO_RESPONSE["project_id"]
    
    final_count = verify_database_state()
    assert final_count == initial_count + 1

# INT-001/016
def test_create_task_status_in_progress(client, task_base_path, test_db_session, verify_database_state):
    """Create task with IN_PROGRESS status"""
    initial_count = verify_database_state()
    
    response = client.post(f"{task_base_path}/", json=TASK_CREATE_STATUS_IN_PROGRESS)
    assert response.status_code == 201
    
    data = response.json()
    task_id = data["id"]
    
    assert data["title"] == EXPECTED_TASK_IN_PROGRESS_RESPONSE["title"]
    assert data["status"] == EXPECTED_TASK_IN_PROGRESS_RESPONSE["status"]
    assert data["project_id"] == EXPECTED_TASK_IN_PROGRESS_RESPONSE["project_id"]
    assert data["priority"] == EXPECTED_TASK_IN_PROGRESS_RESPONSE["priority"]
    assert data["active"] == EXPECTED_TASK_IN_PROGRESS_RESPONSE["active"]
    
    db_result = test_db_session.execute(
        text("SELECT title, status, project_id FROM task WHERE id = :id"), 
        {"id": task_id}
    ).fetchone()
    assert db_result is not None
    assert db_result[0] == EXPECTED_TASK_IN_PROGRESS_RESPONSE["title"]
    assert db_result[1] == EXPECTED_TASK_IN_PROGRESS_RESPONSE["status"]
    assert db_result[2] == EXPECTED_TASK_IN_PROGRESS_RESPONSE["project_id"]
    
    final_count = verify_database_state()
    assert final_count == initial_count + 1

# INT-001/017
def test_create_task_status_completed(client, task_base_path, test_db_session, verify_database_state):
    """Create task with COMPLETED status"""
    initial_count = verify_database_state()
    
    response = client.post(f"{task_base_path}/", json=TASK_CREATE_STATUS_COMPLETED)
    assert response.status_code == 201
    
    data = response.json()
    task_id = data["id"]
    
    assert data["title"] == EXPECTED_TASK_COMPLETED_RESPONSE["title"]
    assert data["status"] == EXPECTED_TASK_COMPLETED_RESPONSE["status"]
    assert data["project_id"] == EXPECTED_TASK_COMPLETED_RESPONSE["project_id"]
    assert data["priority"] == EXPECTED_TASK_COMPLETED_RESPONSE["priority"]
    assert data["active"] == EXPECTED_TASK_COMPLETED_RESPONSE["active"]
    
    db_result = test_db_session.execute(
        text("SELECT title, status, project_id FROM task WHERE id = :id"), 
        {"id": task_id}
    ).fetchone()
    assert db_result is not None
    assert db_result[0] == EXPECTED_TASK_COMPLETED_RESPONSE["title"]
    assert db_result[1] == EXPECTED_TASK_COMPLETED_RESPONSE["status"]
    assert db_result[2] == EXPECTED_TASK_COMPLETED_RESPONSE["project_id"]
    
    final_count = verify_database_state()
    assert final_count == initial_count + 1

# INT-001/018
def test_create_task_status_blocked(client, task_base_path, test_db_session, verify_database_state):
    """Create task with BLOCKED status"""
    initial_count = verify_database_state()
    
    response = client.post(f"{task_base_path}/", json=TASK_CREATE_STATUS_BLOCKED)
    assert response.status_code == 201
    
    data = response.json()
    task_id = data["id"]
    
    assert data["title"] == EXPECTED_TASK_BLOCKED_RESPONSE["title"]
    assert data["status"] == EXPECTED_TASK_BLOCKED_RESPONSE["status"]
    assert data["project_id"] == EXPECTED_TASK_BLOCKED_RESPONSE["project_id"]
    assert data["priority"] == EXPECTED_TASK_BLOCKED_RESPONSE["priority"]
    assert data["active"] == EXPECTED_TASK_BLOCKED_RESPONSE["active"]
    
    db_result = test_db_session.execute(
        text("SELECT title, status, project_id FROM task WHERE id = :id"), 
        {"id": task_id}
    ).fetchone()
    assert db_result is not None
    assert db_result[0] == EXPECTED_TASK_BLOCKED_RESPONSE["title"]
    assert db_result[1] == EXPECTED_TASK_BLOCKED_RESPONSE["status"]
    assert db_result[2] == EXPECTED_TASK_BLOCKED_RESPONSE["project_id"]
    
    final_count = verify_database_state()
    assert final_count == initial_count + 1

# INT-001/019
def test_create_task_null_optional_fields(client, task_base_path):
    """Create task with explicitly null optional fields"""
    response = client.post(f"{task_base_path}/", json=TASK_CREATE_NULL_FIELDS)
    assert response.status_code == 201
    
    data = response.json()
    assert data["description"] is None
    assert data["start_date"] is None
    assert data["deadline"] is None

# INT-001/020
def test_create_task_long_text_fields(client, task_base_path):
    """Create task with long text content"""
    response = client.post(f"{task_base_path}/", json=TASK_CREATE_LONG_TEXT)
    assert response.status_code == 201
    
    data = response.json()
    assert data["title"] == TASK_CREATE_LONG_TEXT["title"]
    assert data["description"] == TASK_CREATE_LONG_TEXT["description"]

# INT-001/021
def test_create_task_special_characters(client, task_base_path):
    """Create task with special characters in text fields"""
    response = client.post(f"{task_base_path}/", json=TASK_CREATE_SPECIAL_CHARS)
    assert response.status_code == 201
    
    data = response.json()
    assert data["title"] == TASK_CREATE_SPECIAL_CHARS["title"]
    assert data["description"] == TASK_CREATE_SPECIAL_CHARS["description"]

# INT-001/022
def test_create_task_multiple_projects(client, task_base_path):
    """Create tasks for different projects"""
    response1 = client.post(f"{task_base_path}/", json=TASK_CREATE_PROJECT_1)
    assert response1.status_code == 201
    assert response1.json()["project_id"] == TASK_CREATE_PROJECT_1["project_id"]
    
    response2 = client.post(f"{task_base_path}/", json=TASK_CREATE_PROJECT_2)
    assert response2.status_code == 201
    assert response2.json()["project_id"] == TASK_CREATE_PROJECT_2["project_id"]
    
    response3 = client.post(f"{task_base_path}/", json=TASK_CREATE_PROJECT_3)
    assert response3.status_code == 201
    assert response3.json()["project_id"] == TASK_CREATE_PROJECT_3["project_id"]

# INT-001/023
def test_create_task_response_structure(client, task_base_path):
    """Verify task creation response structure"""
    response = client.post(f"{task_base_path}/", json=TASK_CREATE_RESPONSE_TEST)
    assert response.status_code == 201
    
    data = response.json()
    for field in EXPECTED_RESPONSE_FIELDS:
        assert field in data
    
    assert isinstance(data["id"], int)
    assert data["id"] > 0
    assert isinstance(data["active"], bool)
    assert data["active"] is True

# INT-001/024
def test_create_task_all_status_combinations(client, task_base_path):
    """Create tasks with all valid status combinations"""
    status_payloads = [
        TASK_CREATE_STATUS_TODO,
        TASK_CREATE_STATUS_IN_PROGRESS,
        TASK_CREATE_STATUS_COMPLETED,
        TASK_CREATE_STATUS_BLOCKED
    ]
    
    for status_data in status_payloads:
        response = client.post(f"{task_base_path}/", json=status_data)
        assert response.status_code == 201
        assert response.json()["status"] == status_data["status"]

# INT-001/025
def test_create_task_database_isolation(client, task_base_path, test_db_session, verify_database_state):
    """Verify database isolation between test runs - Full stack test"""
    initial_count = verify_database_state()
    assert initial_count == 0
    
    response1 = client.post(f"{task_base_path}/", json=TASK_CREATE_MINIMAL)
    assert response1.status_code == 201
    task1_id = response1.json()["id"]
    
    response2 = client.post(f"{task_base_path}/", json=TASK_CREATE_FULL)
    assert response2.status_code == 201
    task2_id = response2.json()["id"]
    
    task1_db = test_db_session.execute(
        text("SELECT title FROM task WHERE id = :id"), {"id": task1_id}
    ).fetchone()
    task2_db = test_db_session.execute(
        text("SELECT title FROM task WHERE id = :id"), {"id": task2_id}
    ).fetchone()
    
    assert task1_db is not None
    assert task2_db is not None
    assert task1_db[0] == TASK_CREATE_MINIMAL["title"]
    assert task2_db[0] == TASK_CREATE_FULL["title"]
    
    final_count = verify_database_state()
    assert final_count == 2
    
    get_response1 = client.get(f"{task_base_path}/{task1_id}")
    get_response2 = client.get(f"{task_base_path}/{task2_id}")
    assert get_response1.status_code == 200
    assert get_response2.status_code == 200
    assert get_response1.json()["title"] == TASK_CREATE_MINIMAL["title"]
    assert get_response2.json()["title"] == TASK_CREATE_FULL["title"]

# INT-001/026
def test_create_task_service_layer_integration(client, task_base_path, test_db_session, verify_database_state):
    """Test service layer integration and error handling - Full stack test"""
    initial_count = verify_database_state()
    
    response = client.post(f"{task_base_path}/", json=TASK_CREATE_MINIMAL)
    assert response.status_code == 201
    task_id = response.json()["id"]
    
    db_task = test_db_session.execute(
        text("SELECT title, active FROM task WHERE id = :id"), {"id": task_id}
    ).fetchone()
    assert db_task is not None
    assert db_task[0] == TASK_CREATE_MINIMAL["title"]
    assert db_task[1] == 1
    
    invalid_response = client.post(f"{task_base_path}/", json=TASK_CREATE_PRIORITY_TOO_LOW)
    assert invalid_response.status_code == 422
    
    invalid_count = test_db_session.execute(
        text("SELECT COUNT(*) FROM task WHERE title = :title"),
        {"title": TASK_CREATE_PRIORITY_TOO_LOW.get("title", "Invalid Task")}
    ).scalar()
    assert invalid_count == 0
    
    final_count = verify_database_state()
    assert final_count == initial_count + 1

# INT-001/027
def test_create_task_transaction_integrity(client, task_base_path, test_db_session, verify_database_state):
    """Test database transaction integrity - Full stack test"""
    initial_count = verify_database_state()
    
    parent_response = client.post(f"{task_base_path}/", json=TASK_CREATE_PARENT)
    assert parent_response.status_code == 201
    parent_id = parent_response.json()["id"]
    
    child_payload = TASK_CREATE_CHILD_TEMPLATE.copy()
    child_payload["parent_id"] = parent_id
    child_response = client.post(f"{task_base_path}/", json=child_payload)
    assert child_response.status_code == 201
    child_id = child_response.json()["id"]
    
    task_exists = test_db_session.execute(
        text("SELECT COUNT(*) FROM task WHERE id = :id"), {"id": child_id}
    ).scalar()
    relationship_exists = test_db_session.execute(
        text("SELECT COUNT(*) FROM parent_assignment WHERE parent_id = :parent_id AND subtask_id = :child_id"),
        {"parent_id": parent_id, "child_id": child_id}
    ).scalar()
    
    assert task_exists == 1
    assert relationship_exists == 1
    
    final_count = verify_database_state()
    assert final_count == initial_count + 2
