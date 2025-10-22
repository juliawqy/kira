from __future__ import annotations

import pytest
from sqlalchemy import text
from backend.src.database.models.project import Project
from backend.src.database.models.user import User
import backend.src.services.user as user_service
import backend.src.services.project as project_service
import backend.src.services.task as task_service
from sqlalchemy.orm import sessionmaker
from tests.mock_data.task.integration_data import (
    TASK_CREATE_PAYLOAD,
    TASK_2_PAYLOAD,
    TASK_3_PAYLOAD,
    TASK_4_PAYLOAD,
    INACTIVE_TASK_PAYLOAD,
    INVALID_TASK_ID_NONEXISTENT,
    VALID_PROJECT,
    VALID_PROJECT_2,
    VALID_PROJECT_ID,
    VALID_USER_ID,
    INVALID_PROJECT_ID,
    INVALID_USER_ID,
    VALID_USER_ADMIN_TASK_ASSIGNMENT,
    VALID_USER_EMPLOYEE_TASK_ASSIGNMENT,
    VALID_CREATE_PAYLOAD_ADMIN,
    VALID_CREATE_PAYLOAD_USER,
    EXPECTED_TASK_RESPONSE,
    VALID_ASSIGNMENT_PAYLOAD,
    VALID_ASSIGNMENT_PAYLOAD_MULTIPLE,
    INVALID_ASSIGNMENT_PAYLOAD,
    EMPTY_ASSIGNMENT_PAYLOAD
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


# -------------------- Fixtures --------------------

@pytest.fixture
def test_db_session(test_engine):
    """Create a database session using the same SessionLocal as the API."""
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
    """Fixture to verify database state before and after tests."""
    def _verify_state():
        result = test_db_session.execute(text("SELECT COUNT(*) FROM task"))
        return result.scalar()

    initial_count = _verify_state()
    yield _verify_state
    final_count = _verify_state()

@pytest.fixture
def create_test_users_and_project(test_db_session):
    """Seed two valid users and two projects with correct foreign key IDs."""
    admin_user = User(**VALID_CREATE_PAYLOAD_ADMIN)
    employee_user = User(**VALID_CREATE_PAYLOAD_USER)
    project = Project(**VALID_PROJECT)
    project2 = Project(**VALID_PROJECT_2)
    test_db_session.add_all([admin_user, employee_user, project, project2])
    test_db_session.commit()

    return [admin_user.user_id, employee_user.user_id]

@pytest.fixture(scope="session", autouse=True)
def unify_sessions(test_engine):
    """Ensure all services share the same session factory."""
    TestingSessionLocal = sessionmaker(
        bind=test_engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
        future=True,
    )
    user_service.SessionLocal = TestingSessionLocal
    project_service.SessionLocal = TestingSessionLocal
    task_service.SessionLocal = TestingSessionLocal
    yield

@pytest.fixture
def create_test_task(client, task_base_path, create_test_users_and_project):
    """Create a test task after seeding users and project."""
    response = client.post(f"{task_base_path}/", json=serialize_payload(TASK_CREATE_PAYLOAD))
    assert response.status_code == 201, f"Task creation failed: {response.text}"
    return response.json()


# ================================ assign_users API Tests ================================

# INT-026/001
def test_assign_users_api_success(client, task_base_path, create_test_task):
    """Assign multiple users to a task via API successfully."""

    response = client.post(f"{task_base_path}/{EXPECTED_TASK_RESPONSE['id']}/assignees", json=VALID_ASSIGNMENT_PAYLOAD_MULTIPLE)

    assert response.status_code == 200
    result = response.json()
    assert result["created"] == 2
    assert "created" in result

# INT-026/002
def test_assign_users_api_single_user_success(client, task_base_path, create_test_task):
    """Assign single user to a task via API successfully."""

    response = client.post(f"{task_base_path}/{EXPECTED_TASK_RESPONSE['id']}/assignees", json=VALID_ASSIGNMENT_PAYLOAD)

    assert response.status_code == 200
    result = response.json()
    assert result["created"] == 1

# INT-026/003
def test_assign_users_api_idempotent_behavior(client, task_base_path, create_test_task):
    """Assign same users multiple times returns 0 for second assignment (idempotent)."""

    response1 = client.post(f"{task_base_path}/{EXPECTED_TASK_RESPONSE['id']}/assignees", json=VALID_ASSIGNMENT_PAYLOAD_MULTIPLE)
    assert response1.status_code == 200
    assert response1.json()["created"] == 2

    response2 = client.post(f"{task_base_path}/{EXPECTED_TASK_RESPONSE['id']}/assignees", json=VALID_ASSIGNMENT_PAYLOAD)
    assert response2.status_code == 200
    assert response2.json()["created"] == 0

# INT-026/004
def test_assign_users_api_task_not_found(client, task_base_path, create_test_users_and_project):
    """Assign users to nonexistent task returns 404."""

    response = client.post(f"{task_base_path}/{INVALID_TASK_ID_NONEXISTENT}/assignees", json=VALID_ASSIGNMENT_PAYLOAD)

    assert response.status_code == 404
    assert "Task not found" in response.json()["detail"]

# INT-026/005
def test_assign_users_api_user_not_found(client, task_base_path, create_test_task):
    """Assign nonexistent user to task returns 404."""

    response = client.post(f"{task_base_path}/{EXPECTED_TASK_RESPONSE['id']}/assignees", json=INVALID_ASSIGNMENT_PAYLOAD)

    assert response.status_code == 404
    assert "User" in response.json()["detail"] and "not found" in response.json()["detail"]

# INT-026/006
def test_assign_users_api_empty_payload_validation(client, task_base_path, create_test_task):
    """Assign users with empty user_ids list returns validation error."""

    response = client.post(f"{task_base_path}/{EXPECTED_TASK_RESPONSE['id']}/assignees", json=EMPTY_ASSIGNMENT_PAYLOAD)

    assert response.status_code == 422 

# ================================ unassign_users API Tests ================================

# INT-026/007
def test_unassign_users_api_success(client, task_base_path, create_test_task):
    """Remove multiple user assignments via API successfully."""

    assign_response = client.post(f"{task_base_path}/{EXPECTED_TASK_RESPONSE['id']}/assignees", json=VALID_ASSIGNMENT_PAYLOAD_MULTIPLE)
    assert assign_response.status_code == 200

    response = client.request("DELETE", f"{task_base_path}/{EXPECTED_TASK_RESPONSE['id']}/assignees", json=VALID_ASSIGNMENT_PAYLOAD_MULTIPLE)

    assert response.status_code == 200
    result = response.json()
    assert result["Removed"] == 2

# INT-026/008
def test_unassign_users_api_no_assignments(client, task_base_path, create_test_task):
    """Remove users with no existing assignments returns 0."""

    response = client.request("DELETE", f"{task_base_path}/{EXPECTED_TASK_RESPONSE['id']}/assignees", json=VALID_ASSIGNMENT_PAYLOAD_MULTIPLE)

    assert response.status_code == 200
    result = response.json()
    assert result["Removed"] == 0

# INT-026/009
def test_unassign_users_api_task_not_found(client, task_base_path, create_test_users_and_project):
    """Remove users from nonexistent task returns 404."""

    response = client.request("DELETE", f"{task_base_path}/{INVALID_TASK_ID_NONEXISTENT}/assignees", json=VALID_ASSIGNMENT_PAYLOAD_MULTIPLE)

    assert response.status_code == 404
    assert "Task not found" in response.json()["detail"]

# INT-026/010
def test_unassign_users_api_user_not_found(client, task_base_path, create_test_task):
    """Remove nonexistent user from task returns 404."""

    response = client.request("DELETE", f"{task_base_path}/{EXPECTED_TASK_RESPONSE['id']}/assignees", json=INVALID_ASSIGNMENT_PAYLOAD)

    assert response.status_code == 404
    assert "User" in response.json()["detail"] and "not found" in response.json()["detail"]

# ============================= clear_task_assignees API Tests =============================

# INT-026/011
def test_clear_task_assignees_api_success(client, task_base_path, create_test_task):
    """Clear all user assignments from task via API successfully."""
    task = create_test_task
    user_ids = [VALID_USER_ADMIN_TASK_ASSIGNMENT["user_id"], VALID_USER_EMPLOYEE_TASK_ASSIGNMENT["user_id"]]

    assign_payload = {"user_ids": user_ids}
    assign_response = client.post(f"{task_base_path}/{task['id']}/assignees", json=assign_payload)
    assert assign_response.status_code == 200

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
def test_list_assignees_api_success(client, task_base_path, create_test_task, create_test_users_and_project, test_db_session):
    """List users assigned to a task via API successfully."""
    task = create_test_task
    user_ids = create_test_users_and_project
    
    assign_payload = {"user_ids": user_ids}
    assign_response = client.post(f"{task_base_path}/{task['id']}/assignees", json=assign_payload)
    assert assign_response.status_code == 200
    
    response = client.get(f"{task_base_path}/{task['id']}/assignees")
    
    assert response.status_code == 200
    assignees = response.json()
    assert len(assignees) == 2
    
    assignee_ids = [assignee["user_id"] for assignee in assignees]
    assert VALID_USER_ADMIN_TASK_ASSIGNMENT["user_id"] in assignee_ids
    assert VALID_USER_EMPLOYEE_TASK_ASSIGNMENT["user_id"] in assignee_ids
    
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
def test_assign_users_database_persistence(client, task_base_path, create_test_task, create_test_users_and_project, test_db_session):
    """Verify that user assignments persist in the database."""
    task = create_test_task
    user_ids = create_test_users_and_project
    
    payload = {"user_ids": user_ids}
    response = client.post(f"{task_base_path}/{task['id']}/assignees", json=payload)
    assert response.status_code == 200
    
    db_assignments = test_db_session.execute(
        text("SELECT task_id, user_id FROM task_assignment WHERE task_id = :task_id"),
        {"task_id": task["id"]}
    ).fetchall()
    
    assert len(db_assignments) == 2
    assignment_tuples = [(row[0], row[1]) for row in db_assignments]
    assert (task["id"], VALID_USER_ADMIN_TASK_ASSIGNMENT["user_id"]) in assignment_tuples
    assert (task["id"], VALID_USER_EMPLOYEE_TASK_ASSIGNMENT["user_id"]) in assignment_tuples

# INT-026/018
def test_unassign_users_database_removal(client, task_base_path, create_test_task, create_test_users_and_project, test_db_session):
    """Verify that unassigning users removes records from the database."""
    task = create_test_task
    user_ids = create_test_users_and_project
    
    assign_payload = {"user_ids": user_ids}
    assign_response = client.post(f"{task_base_path}/{task['id']}/assignees", json=assign_payload)
    assert assign_response.status_code == 200
    
    db_assignments = test_db_session.execute(
        text("SELECT COUNT(*) FROM task_assignment WHERE task_id = :task_id"),
        {"task_id": task["id"]}
    ).scalar()
    assert db_assignments == 2
    
    unassign_payload = {"user_ids": user_ids}
    unassign_response = client.request("DELETE", f"{task_base_path}/{task['id']}/assignees", json=unassign_payload)
    assert unassign_response.status_code == 200
    
    db_assignments = test_db_session.execute(
        text("SELECT COUNT(*) FROM task_assignment WHERE task_id = :task_id"),
        {"task_id": task["id"]}
    ).scalar()
    assert db_assignments == 0

# INT-026/019
def test_clear_task_assignees_database_removal(client, task_base_path, create_test_task, create_test_users_and_project, test_db_session):
    """Verify that clearing task assignees removes all records from the database."""
    task = create_test_task
    user_ids = create_test_users_and_project
    
    assign_payload = {"user_ids": user_ids}
    assign_response = client.post(f"{task_base_path}/{task['id']}/assignees", json=assign_payload)
    assert assign_response.status_code == 200
    
    db_assignments = test_db_session.execute(
        text("SELECT COUNT(*) FROM task_assignment WHERE task_id = :task_id"),
        {"task_id": task["id"]}
    ).scalar()
    assert db_assignments == 2
    
    clear_response = client.delete(f"{task_base_path}/{task['id']}/assignees/all")
    assert clear_response.status_code == 200
    
    db_assignments = test_db_session.execute(
        text("SELECT COUNT(*) FROM task_assignment WHERE task_id = :task_id"),
        {"task_id": task["id"]}
    ).scalar()
    assert db_assignments == 0

# ================================ Complete Workflow Tests ================================

# INT-026/020
def test_complete_assignment_workflow(client, task_base_path, create_test_task, create_test_users_and_project, test_db_session):
    """Test complete workflow: assign users, list assignees, unassign some, list again."""
    task = create_test_task
    user_ids = create_test_users_and_project
    
    assign_payload = {"user_ids": user_ids}
    assign_response = client.post(f"{task_base_path}/{task['id']}/assignees", json=assign_payload)
    assert assign_response.status_code == 200
    assert assign_response.json()["created"] == 2
    
    list_response = client.get(f"{task_base_path}/{task['id']}/assignees")
    assert list_response.status_code == 200
    assignees = list_response.json()
    assert len(assignees) == 2
    
    unassign_payload = {"user_ids": [user_ids[0]]}
    unassign_response = client.request("DELETE", f"{task_base_path}/{task['id']}/assignees", json=unassign_payload)
    assert unassign_response.status_code == 200
    assert unassign_response.json()["Removed"] == 1
    
    list_response2 = client.get(f"{task_base_path}/{task['id']}/assignees")
    assert list_response2.status_code == 200
    assignees2 = list_response2.json()
    assert len(assignees2) == 1
    assert assignees2[0]["user_id"] == user_ids[1]
    
    clear_response = client.delete(f"{task_base_path}/{task['id']}/assignees/all")
    assert clear_response.status_code == 200
    assert clear_response.json()["Removed"] == 1
    
    list_response3 = client.get(f"{task_base_path}/{task['id']}/assignees")
    assert list_response3.status_code == 200
    assignees3 = list_response3.json()
    assert len(assignees3) == 0

# INT-026/021
def test_multiple_tasks_assignment_independence(client, task_base_path, create_test_users_and_project, test_db_session):
    """Test that assignments to different tasks are independent."""
    user_ids = create_test_users_and_project
    
    task1_response = client.post(f"{task_base_path}/", json=serialize_payload(TASK_CREATE_PAYLOAD))
    assert task1_response.status_code == 201
    task1 = task1_response.json()
    
    task2_response = client.post(f"{task_base_path}/", json=serialize_payload(TASK_2_PAYLOAD))
    assert task2_response.status_code == 201
    task2 = task2_response.json()
    
    assign_payload = {"user_ids": user_ids}
    
    task1_assign = client.post(f"{task_base_path}/{task1['id']}/assignees", json=assign_payload)
    assert task1_assign.status_code == 200
    
    task2_assign = client.post(f"{task_base_path}/{task2['id']}/assignees", json=assign_payload)
    assert task2_assign.status_code == 200
    
    task1_list = client.get(f"{task_base_path}/{task1['id']}/assignees")
    assert task1_list.status_code == 200
    assert len(task1_list.json()) == 2
    
    task2_list = client.get(f"{task_base_path}/{task2['id']}/assignees")
    assert task2_list.status_code == 200
    assert len(task2_list.json()) == 2
    
    task1_clear = client.delete(f"{task_base_path}/{task1['id']}/assignees/all")
    assert task1_clear.status_code == 200
    
    task1_list2 = client.get(f"{task_base_path}/{task1['id']}/assignees")
    assert task1_list2.status_code == 200
    assert len(task1_list2.json()) == 0
    
    task2_list2 = client.get(f"{task_base_path}/{task2['id']}/assignees")
    assert task2_list2.status_code == 200
    assert len(task2_list2.json()) == 2

# INT-133/001
def test_list_project_tasks_by_user(client, task_base_path, test_db_session, create_test_users_and_project):
    for payload in (
        TASK_CREATE_PAYLOAD,
        TASK_2_PAYLOAD,     
        TASK_3_PAYLOAD,     
        TASK_4_PAYLOAD,
        INACTIVE_TASK_PAYLOAD    
    ):
        resp = client.post(f"{task_base_path}/", json=serialize_payload(payload))
        assert resp.status_code == 201

    user_ids = [VALID_USER_ADMIN_TASK_ASSIGNMENT["user_id"]]

    payload = {"user_ids": user_ids}
    response = client.post(f"{task_base_path}/{EXPECTED_TASK_RESPONSE['id']}/assignees", json=payload)
    assert response.status_code == 200

    response = client.get(f"{task_base_path}/project-user/{VALID_PROJECT_ID}/{VALID_USER_ID}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1

# INT-133/002
def test_list_project_tasks_by_invalid_user(client, task_base_path, create_test_users_and_project):
    for payload in (
        TASK_CREATE_PAYLOAD,
        TASK_2_PAYLOAD,     
        TASK_3_PAYLOAD,     
        TASK_4_PAYLOAD,
        INACTIVE_TASK_PAYLOAD    
    ):
        resp = client.post(f"{task_base_path}/", json=serialize_payload(payload))
        assert resp.status_code == 201

    response = client.get(f"{task_base_path}/project-user/{VALID_PROJECT_ID}/{INVALID_USER_ID}")
    assert response.status_code == 400

# INT-133-003
def test_list_user_project_tasks_by_invalid_project(client, task_base_path, create_test_users_and_project):
    for payload in (
        TASK_CREATE_PAYLOAD,
        TASK_2_PAYLOAD,     
        TASK_3_PAYLOAD,     
        TASK_4_PAYLOAD,
        INACTIVE_TASK_PAYLOAD    
    ):
        resp = client.post(f"{task_base_path}/", json=serialize_payload(payload))
        assert resp.status_code == 201

    response = client.get(f"{task_base_path}/project-user/{INVALID_PROJECT_ID}/{INVALID_USER_ID}")
    assert response.status_code == 400
