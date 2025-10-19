# tests/backend/integration/task/test_task_assignment_api.py
from __future__ import annotations

import pytest
from sqlalchemy import text

from tests.mock_data.task.integration_data import (
    TASK_CREATE_PAYLOAD,
    TASK_2_PAYLOAD,
    TASK_3_PAYLOAD,
    INVALID_TASK_ID_NONEXISTENT,
)
from tests.mock_data.user.integration_data import (
    VALID_USER_ADMIN_TASK_ASSIGNMENT,
    VALID_USER_EMPLOYEE_TASK_ASSIGNMENT,
    INVALID_USER_ID,
)

def serialize_payload(payload: dict) -> dict:
    """Convert date/datetime objects in payload to ISO strings for JSON serialization."""
    from datetime import date, datetime
    
    def convert(value):
        if isinstance(value, (date, datetime)):
            return value.isoformat()
        if isinstance(value, dict):
            return {k: convert(v) for k, v in value.items()}
        if isinstance(value, list):
            return [convert(v) for v in value]
        return value

    return {k: convert(v) for k, v in payload.items()}


@pytest.fixture
def test_db_session(test_engine):
    """
    Create a database session using the same SessionLocal as the API.
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
        return result.scalar()

    initial_count = _verify_state()
    yield _verify_state
    final_count = _verify_state()
    # Note: We don't assert equality here since some tests may create/delete tasks


@pytest.fixture
def create_test_task(client, task_base_path):
    """Create a test task and return its data."""
    response = client.post(f"{task_base_path}/", json=serialize_payload(TASK_CREATE_PAYLOAD))
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def create_test_users(test_db_session):
    """Create test users in the database and return their IDs."""
    # Insert test users directly into the database
    test_db_session.execute(
            text("""
            INSERT INTO user (user_id, name, email, role, department_id, admin, hashed_pw)
            VALUES 
            (1, :name1, :email1, :role1, :dept1, :admin1, :hash1),
            (2, :name2, :email2, :role2, :dept2, :admin2, :hash2)
            """),
        {
            "name1": VALID_USER_ADMIN_TASK_ASSIGNMENT["name"],
            "email1": VALID_USER_ADMIN_TASK_ASSIGNMENT["email"],
            "role1": VALID_USER_ADMIN_TASK_ASSIGNMENT["role"],
            "dept1": VALID_USER_ADMIN_TASK_ASSIGNMENT["department_id"],
            "admin1": VALID_USER_ADMIN_TASK_ASSIGNMENT["admin"],
            "hash1": "hashed_password_1",
            "name2": VALID_USER_EMPLOYEE_TASK_ASSIGNMENT["name"],
            "email2": VALID_USER_EMPLOYEE_TASK_ASSIGNMENT["email"],
            "role2": VALID_USER_EMPLOYEE_TASK_ASSIGNMENT["role"],
            "dept2": VALID_USER_EMPLOYEE_TASK_ASSIGNMENT["department_id"],
            "admin2": VALID_USER_EMPLOYEE_TASK_ASSIGNMENT["admin"],
            "hash2": "hashed_password_2",
        }
    )
    test_db_session.commit()
    return [VALID_USER_ADMIN_TASK_ASSIGNMENT["user_id"], VALID_USER_EMPLOYEE_TASK_ASSIGNMENT["user_id"]]


# ================================ assign_users API Tests ================================

# INT-026/001
def test_assign_users_api_success(client, task_base_path, create_test_task, create_test_users):
    """Assign multiple users to a task via API successfully."""
    task = create_test_task
    user_ids = create_test_users
    
    payload = {"user_ids": user_ids}
    response = client.post(f"{task_base_path}/{task['id']}/assignees", json=payload)
    
    assert response.status_code == 200
    result = response.json()
    assert result["created"] == 2
    assert "created" in result

# INT-026/002
def test_assign_users_api_single_user_success(client, task_base_path, create_test_task, create_test_users):
    """Assign single user to a task via API successfully."""
    task = create_test_task
    user_ids = create_test_users
    
    payload = {"user_ids": [user_ids[0]]}
    response = client.post(f"{task_base_path}/{task['id']}/assignees", json=payload)
    
    assert response.status_code == 200
    result = response.json()
    assert result["created"] == 1

# INT-026/003
def test_assign_users_api_idempotent_behavior(client, task_base_path, create_test_task, create_test_users):
    """Assign same users multiple times returns 0 for second assignment (idempotent)."""
    task = create_test_task
    user_ids = create_test_users
    
    payload = {"user_ids": user_ids}
    
    # First assignment
    response1 = client.post(f"{task_base_path}/{task['id']}/assignees", json=payload)
    assert response1.status_code == 200
    assert response1.json()["created"] == 2
    
    # Second assignment (should be idempotent)
    response2 = client.post(f"{task_base_path}/{task['id']}/assignees", json=payload)
    assert response2.status_code == 200
    assert response2.json()["created"] == 0

# INT-026/004
def test_assign_users_api_task_not_found(client, task_base_path, create_test_users):
    """Assign users to nonexistent task returns 404."""
    user_ids = create_test_users
    
    payload = {"user_ids": user_ids}
    response = client.post(f"{task_base_path}/{INVALID_TASK_ID_NONEXISTENT}/assignees", json=payload)
    
    assert response.status_code == 404
    assert "Task not found" in response.json()["detail"]

# INT-026/005
def test_assign_users_api_user_not_found(client, task_base_path, create_test_task):
    """Assign nonexistent user to task returns 404."""
    task = create_test_task
    
    payload = {"user_ids": [INVALID_USER_ID]}
    response = client.post(f"{task_base_path}/{task['id']}/assignees", json=payload)
    
    assert response.status_code == 404
    assert "User" in response.json()["detail"] and "not found" in response.json()["detail"]

# INT-026/006
def test_assign_users_api_empty_payload_validation(client, task_base_path, create_test_task):
    """Assign users with empty user_ids list returns validation error."""
    task = create_test_task
    
    payload = {"user_ids": []}
    response = client.post(f"{task_base_path}/{task['id']}/assignees", json=payload)
    
    assert response.status_code == 422  # Validation error

# ================================ unassign_users API Tests ================================

# INT-026/007
def test_unassign_users_api_success(client, task_base_path, create_test_task, create_test_users, test_db_session):
    """Remove multiple user assignments via API successfully."""
    task = create_test_task
    user_ids = create_test_users
    
    # First assign users
    assign_payload = {"user_ids": user_ids}
    assign_response = client.post(f"{task_base_path}/{task['id']}/assignees", json=assign_payload)
    assert assign_response.status_code == 200
    
    # Then unassign users
    import json
    unassign_payload = {"user_ids": user_ids}
    response = client.request(
        "DELETE",
        f"{task_base_path}/{task['id']}/assignees", 
        json=unassign_payload
    )
    
    assert response.status_code == 200
    result = response.json()
    assert result["Removed"] == 2

# INT-026/008
def test_unassign_users_api_no_assignments(client, task_base_path, create_test_task, create_test_users):
    """Remove users with no existing assignments returns 0."""
    task = create_test_task
    user_ids = create_test_users
    
    unassign_payload = {"user_ids": user_ids}
    response = client.request(
        "DELETE",
        f"{task_base_path}/{task['id']}/assignees", 
        json=unassign_payload
    )
    
    assert response.status_code == 200
    result = response.json()
    assert result["Removed"] == 0

# INT-026/009
def test_unassign_users_api_task_not_found(client, task_base_path, create_test_users):
    """Remove users from nonexistent task returns 404."""
    user_ids = create_test_users
    
    unassign_payload = {"user_ids": user_ids}
    response = client.request(
        "DELETE",
        f"{task_base_path}/{INVALID_TASK_ID_NONEXISTENT}/assignees", 
        json=unassign_payload
    )
    
    assert response.status_code == 404
    assert "Task not found" in response.json()["detail"]

# INT-026/010
def test_unassign_users_api_user_not_found(client, task_base_path, create_test_task):
    """Remove nonexistent user from task returns 404."""
    task = create_test_task
    
    unassign_payload = {"user_ids": [INVALID_USER_ID]}
    response = client.request(
        "DELETE",
        f"{task_base_path}/{task['id']}/assignees", 
        json=unassign_payload
    )
    
    assert response.status_code == 404
    assert "User" in response.json()["detail"] and "not found" in response.json()["detail"]

# ================================ clear_task_assignees API Tests ================================

# INT-026/011
def test_clear_task_assignees_api_success(client, task_base_path, create_test_task, create_test_users, test_db_session):
    """Clear all user assignments from task via API successfully."""
    task = create_test_task
    user_ids = create_test_users
    
    # First assign users
    assign_payload = {"user_ids": user_ids}
    assign_response = client.post(f"{task_base_path}/{task['id']}/assignees", json=assign_payload)
    assert assign_response.status_code == 200
    
    # Then clear all assignments
    response = client.delete(f"{task_base_path}/{task['id']}/assignees/all")
    
    assert response.status_code == 200
    result = response.json()
    assert result["Removed"] == 2

# INT-026/012
def test_clear_task_assignees_api_no_assignments(client, task_base_path, create_test_task):
    """Clear assignments from task with no assignments returns 0."""
    task = create_test_task
    
    response = client.delete(f"{task_base_path}/{task['id']}/assignees/all")
    
    assert response.status_code == 200
    result = response.json()
    assert result["Removed"] == 0

# INT-026/013
def test_clear_task_assignees_api_task_not_found(client, task_base_path):
    """Clear assignments from nonexistent task returns 404."""
    response = client.delete(f"{task_base_path}/{INVALID_TASK_ID_NONEXISTENT}/assignees/all")
    
    assert response.status_code == 404
    assert "Task not found" in response.json()["detail"]

# ================================ list_assignees API Tests ================================

# INT-026/014
def test_list_assignees_api_success(client, task_base_path, create_test_task, create_test_users, test_db_session):
    """List users assigned to a task via API successfully."""
    task = create_test_task
    user_ids = create_test_users
    
    # First assign users
    assign_payload = {"user_ids": user_ids}
    assign_response = client.post(f"{task_base_path}/{task['id']}/assignees", json=assign_payload)
    assert assign_response.status_code == 200
    
    # Then list assignees
    response = client.get(f"{task_base_path}/{task['id']}/assignees")
    
    assert response.status_code == 200
    assignees = response.json()
    assert len(assignees) == 2
    
    # Verify assignee data structure
    assignee_ids = [assignee["user_id"] for assignee in assignees]
    assert VALID_USER_ADMIN_TASK_ASSIGNMENT["user_id"] in assignee_ids
    assert VALID_USER_EMPLOYEE_TASK_ASSIGNMENT["user_id"] in assignee_ids
    
    # Verify UserRead schema fields are present
    for assignee in assignees:
        assert "user_id" in assignee
        assert "name" in assignee
        assert "email" in assignee
        assert "role" in assignee
        assert "admin" in assignee

# INT-026/015
def test_list_assignees_api_no_assignments(client, task_base_path, create_test_task):
    """List assignees for task with no assignments returns empty list."""
    task = create_test_task
    
    response = client.get(f"{task_base_path}/{task['id']}/assignees")
    
    assert response.status_code == 200
    assignees = response.json()
    assert assignees == []

# INT-026/016
def test_list_assignees_api_task_not_found(client, task_base_path):
    """List assignees for nonexistent task returns 404."""
    response = client.get(f"{task_base_path}/{INVALID_TASK_ID_NONEXISTENT}/assignees")
    
    assert response.status_code == 404
    assert "Task" in response.json()["detail"] and "not found" in response.json()["detail"]

# ================================ Database Persistence Tests ================================

# INT-026/017
def test_assign_users_database_persistence(client, task_base_path, create_test_task, create_test_users, test_db_session):
    """Verify that user assignments persist in the database."""
    task = create_test_task
    user_ids = create_test_users
    
    # Assign users via API
    payload = {"user_ids": user_ids}
    response = client.post(f"{task_base_path}/{task['id']}/assignees", json=payload)
    assert response.status_code == 200
    
    # Verify database state
    db_assignments = test_db_session.execute(
        text("SELECT task_id, user_id FROM task_assignment WHERE task_id = :task_id"),
        {"task_id": task["id"]}
    ).fetchall()
    
    assert len(db_assignments) == 2
    assignment_tuples = [(row[0], row[1]) for row in db_assignments]
    assert (task["id"], VALID_USER_ADMIN_TASK_ASSIGNMENT["user_id"]) in assignment_tuples
    assert (task["id"], VALID_USER_EMPLOYEE_TASK_ASSIGNMENT["user_id"]) in assignment_tuples

# INT-026/018
def test_unassign_users_database_removal(client, task_base_path, create_test_task, create_test_users, test_db_session):
    """Verify that unassigning users removes records from the database."""
    task = create_test_task
    user_ids = create_test_users
    
    # First assign users
    assign_payload = {"user_ids": user_ids}
    assign_response = client.post(f"{task_base_path}/{task['id']}/assignees", json=assign_payload)
    assert assign_response.status_code == 200
    
    # Verify assignments exist
    db_assignments = test_db_session.execute(
        text("SELECT COUNT(*) FROM task_assignment WHERE task_id = :task_id"),
        {"task_id": task["id"]}
    ).scalar()
    assert db_assignments == 2
    
    # Unassign users
    unassign_payload = {"user_ids": user_ids}
    unassign_response = client.request("DELETE", f"{task_base_path}/{task['id']}/assignees", json=unassign_payload)
    assert unassign_response.status_code == 200
    
    # Verify assignments removed
    db_assignments = test_db_session.execute(
        text("SELECT COUNT(*) FROM task_assignment WHERE task_id = :task_id"),
        {"task_id": task["id"]}
    ).scalar()
    assert db_assignments == 0

# INT-026/019
def test_clear_task_assignees_database_removal(client, task_base_path, create_test_task, create_test_users, test_db_session):
    """Verify that clearing task assignees removes all records from the database."""
    task = create_test_task
    user_ids = create_test_users
    
    # First assign users
    assign_payload = {"user_ids": user_ids}
    assign_response = client.post(f"{task_base_path}/{task['id']}/assignees", json=assign_payload)
    assert assign_response.status_code == 200
    
    # Verify assignments exist
    db_assignments = test_db_session.execute(
        text("SELECT COUNT(*) FROM task_assignment WHERE task_id = :task_id"),
        {"task_id": task["id"]}
    ).scalar()
    assert db_assignments == 2
    
    # Clear all assignments
    clear_response = client.delete(f"{task_base_path}/{task['id']}/assignees/all")
    assert clear_response.status_code == 200
    
    # Verify assignments removed
    db_assignments = test_db_session.execute(
        text("SELECT COUNT(*) FROM task_assignment WHERE task_id = :task_id"),
        {"task_id": task["id"]}
    ).scalar()
    assert db_assignments == 0

# ================================ Complete Workflow Tests ================================

# INT-026/020
def test_complete_assignment_workflow(client, task_base_path, create_test_task, create_test_users, test_db_session):
    """Test complete workflow: assign users, list assignees, unassign some, list again."""
    task = create_test_task
    user_ids = create_test_users
    
    # Step 1: Assign all users
    assign_payload = {"user_ids": user_ids}
    assign_response = client.post(f"{task_base_path}/{task['id']}/assignees", json=assign_payload)
    assert assign_response.status_code == 200
    assert assign_response.json()["created"] == 2
    
    # Step 2: List assignees
    list_response = client.get(f"{task_base_path}/{task['id']}/assignees")
    assert list_response.status_code == 200
    assignees = list_response.json()
    assert len(assignees) == 2
    
    # Step 3: Unassign one user
    unassign_payload = {"user_ids": [user_ids[0]]}
    unassign_response = client.request("DELETE", f"{task_base_path}/{task['id']}/assignees", json=unassign_payload)
    assert unassign_response.status_code == 200
    assert unassign_response.json()["Removed"] == 1
    
    # Step 4: List assignees again
    list_response2 = client.get(f"{task_base_path}/{task['id']}/assignees")
    assert list_response2.status_code == 200
    assignees2 = list_response2.json()
    assert len(assignees2) == 1
    assert assignees2[0]["user_id"] == user_ids[1]
    
    # Step 5: Clear remaining assignments
    clear_response = client.delete(f"{task_base_path}/{task['id']}/assignees/all")
    assert clear_response.status_code == 200
    assert clear_response.json()["Removed"] == 1
    
    # Step 6: Verify no assignees remain
    list_response3 = client.get(f"{task_base_path}/{task['id']}/assignees")
    assert list_response3.status_code == 200
    assignees3 = list_response3.json()
    assert len(assignees3) == 0

# INT-026/021
def test_multiple_tasks_assignment_independence(client, task_base_path, create_test_users, test_db_session):
    """Test that assignments to different tasks are independent."""
    user_ids = create_test_users
    
    # Create two tasks
    task1_response = client.post(f"{task_base_path}/", json=serialize_payload(TASK_CREATE_PAYLOAD))
    assert task1_response.status_code == 201
    task1 = task1_response.json()
    
    task2_response = client.post(f"{task_base_path}/", json=serialize_payload(TASK_2_PAYLOAD))
    assert task2_response.status_code == 201
    task2 = task2_response.json()
    
    # Assign users to both tasks
    assign_payload = {"user_ids": user_ids}
    
    task1_assign = client.post(f"{task_base_path}/{task1['id']}/assignees", json=assign_payload)
    assert task1_assign.status_code == 200
    
    task2_assign = client.post(f"{task_base_path}/{task2['id']}/assignees", json=assign_payload)
    assert task2_assign.status_code == 200
    
    # Verify both tasks have assignees
    task1_list = client.get(f"{task_base_path}/{task1['id']}/assignees")
    assert task1_list.status_code == 200
    assert len(task1_list.json()) == 2
    
    task2_list = client.get(f"{task_base_path}/{task2['id']}/assignees")
    assert task2_list.status_code == 200
    assert len(task2_list.json()) == 2
    
    # Clear assignments from one task
    task1_clear = client.delete(f"{task_base_path}/{task1['id']}/assignees/all")
    assert task1_clear.status_code == 200
    
    # Verify independence: task1 has no assignees, task2 still has assignees
    task1_list2 = client.get(f"{task_base_path}/{task1['id']}/assignees")
    assert task1_list2.status_code == 200
    assert len(task1_list2.json()) == 0
    
    task2_list2 = client.get(f"{task_base_path}/{task2['id']}/assignees")
    assert task2_list2.status_code == 200
    assert len(task2_list2.json()) == 2
