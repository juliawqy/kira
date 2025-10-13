# tests/backend/integration/task/test_task_create_api.py
from __future__ import annotations

import pytest
from sqlalchemy import text

from backend.src.enums.task_status import TaskStatus
from tests.mock_data.task.integration_data import (
    TASK_CREATE_PAYLOAD,
    INVALID_TASK_CREATE,
    INVALID_TASK_CREATE_INVALID_PARENT,
    INVALID_TASK_CREATE_INACTIVE_PARENT,
    EXPECTED_TASK_RESPONSE,
    EXPECTED_RESPONSE_FIELDS
)


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

    if final_count != initial_count:
        print(f"Database state changed: {initial_count} -> {final_count} tasks")


# INT-001/001
def test_create_task_successful(client, task_base_path, test_db_session, verify_database_state):
    initial_count = verify_database_state()

    response = client.post(f"{task_base_path}/", json=TASK_CREATE_PAYLOAD)
    assert response.status_code == 201

    data = response.json()

    for field in EXPECTED_RESPONSE_FIELDS:
        assert field in data

    expected_response = EXPECTED_TASK_RESPONSE
    for field, expected_value in expected_response.items():
        assert data[field] == expected_value, f"Field {field}: expected {expected_value}, got {data[field]}"

    db_result = test_db_session.execute(
        text("SELECT title, project_id, status, priority, active, description FROM task WHERE id = :id"),
        {"id": expected_response["id"]}
    ).fetchone()
    assert db_result is not None
    assert db_result[0] == expected_response["title"]
    assert db_result[1] == expected_response["project_id"]
    assert db_result[2] == expected_response["status"]
    assert db_result[3] == expected_response["priority"]
    assert db_result[4] == 1
    assert db_result[5] == expected_response["description"]

    final_count = verify_database_state()
    assert final_count == initial_count + 1

# INT-001/002
def test_create_task_invalid_payload(client, task_base_path, test_db_session, verify_database_state):
    """Create task with invalid payload"""
    initial_count = verify_database_state()

    response = client.post(f"{task_base_path}/", json=INVALID_TASK_CREATE)
    assert response.status_code == 422 

    final_count = verify_database_state()
    assert final_count == initial_count  

# INT-001/003
def test_create_task_invalid_parent(client, task_base_path, verify_database_state):
    """Create task with invalid parent id"""
    initial_count = verify_database_state()

    response = client.post(f"{task_base_path}/", json=INVALID_TASK_CREATE_INVALID_PARENT)
    assert response.status_code == 404

    final_count = verify_database_state()
    assert final_count == initial_count  

# INT-001/004
def test_create_task_inactive_parent(client, task_base_path):
    """Create task with inactive parent id"""

    data = client.post(f"{task_base_path}/", json=TASK_CREATE_PAYLOAD)
    data = data.json()
    id = data["id"]
    client.post(f"{task_base_path}/{id}/delete")
    response = client.post(f"{task_base_path}/", json=INVALID_TASK_CREATE_INACTIVE_PARENT)
    assert response.status_code == 400