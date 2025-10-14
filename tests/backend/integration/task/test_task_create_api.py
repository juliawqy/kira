# tests/backend/integration/task/test_task_create_api.py
from __future__ import annotations

import pytest
from sqlalchemy import text
from datetime import date, datetime

from backend.src.enums.task_status import TaskStatus
from tests.mock_data.task.integration_data import (
    TASK_CREATE_PAYLOAD,
    INVALID_TASK_CREATE,
    INVALID_TASK_CREATE_INVALID_PARENT,
    INVALID_TASK_CREATE_INACTIVE_PARENT,
    EXPECTED_TASK_RESPONSE,
    EXPECTED_RESPONSE_FIELDS,
    TASK_CREATE_CHILD,
    INVALID_TASK_ID_NONEXISTENT,
    INACTIVE_TASK_PAYLOAD,
    TASK_3_PAYLOAD
)

def serialize_payload(payload: dict) -> dict:
    """Convert date/datetime objects in payload to ISO strings for JSON serialization."""
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

    if final_count != initial_count:
        print(f"Database state changed: {initial_count} -> {final_count} tasks")


# INT-001/001
def test_create_task_successful(client, task_base_path, test_db_session, verify_database_state):
    initial_count = verify_database_state()

    response = client.post(f"{task_base_path}/", json=serialize_payload(TASK_CREATE_PAYLOAD))
    assert response.status_code == 201

    data = response.json()

    for field in EXPECTED_RESPONSE_FIELDS:
        assert field in data

    expected_response = EXPECTED_TASK_RESPONSE
    for field, expected_value in expected_response.items():
        if (field == "start_date" or field == "deadline") and isinstance(expected_value, date):
            assert data[field] == expected_value.isoformat(), f"Field {field}: expected {expected_value.isoformat()}, got {data[field]}"
        else:
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

    data = client.post(f"{task_base_path}/", json=serialize_payload(TASK_CREATE_PAYLOAD))
    data = data.json()
    id = data["id"]
    client.post(f"{task_base_path}/{id}/delete")
    response = client.post(f"{task_base_path}/", json=INVALID_TASK_CREATE_INACTIVE_PARENT)
    assert response.status_code == 400

# INT-013/001
def test_create_parent_assignment_success(client, task_base_path, test_db_session, verify_database_state):
    """Attach a child task to a parent task via API; verify assignment persists in DB."""
    initial_count = verify_database_state()

    parent_resp = client.post(f"{task_base_path}/", json=serialize_payload(TASK_CREATE_PAYLOAD))
    assert parent_resp.status_code == 201
    parent_task = parent_resp.json()

    child_resp = client.post(f"{task_base_path}/", json=serialize_payload(TASK_CREATE_CHILD))
    assert child_resp.status_code == 201
    child_task = child_resp.json()

    attach_resp = client.post(
        f"{task_base_path}/{parent_task['id']}/subtasks",
        json={"subtask_ids": [child_task["id"]]}
    )
    assert attach_resp.status_code == 200
    updated_parent = attach_resp.json()
    assert any(st["id"] == child_task["id"] for st in updated_parent["subTasks"])

    db_assignment = test_db_session.execute(
        text("SELECT subtask_id, parent_id FROM parent_assignment WHERE subtask_id = :cid"),
        {"cid": child_task["id"]}
    ).fetchone()
    assert db_assignment == (child_task["id"], parent_task["id"])

    final_count = verify_database_state()
    assert final_count == initial_count + 2 

# INT-013/002
def test_create_parent_assignment_nonexistent_parent(client, task_base_path, test_db_session, verify_database_state):
    """Attaching a child to a nonexistent parent should return 404 and no DB row created."""
    initial_count = verify_database_state()

    child_resp = client.post(f"{task_base_path}/", json=serialize_payload(TASK_CREATE_CHILD))
    assert child_resp.status_code == 201
    child_task = child_resp.json()

    attach_resp = client.post(
        f"{task_base_path}/{INVALID_TASK_ID_NONEXISTENT}/subtasks",
        json={"subtask_ids": [child_task["id"]]}
    )
    assert attach_resp.status_code == 404
    assert "not found" in attach_resp.json()["detail"].lower()

    db_assignment = test_db_session.execute(
        text("SELECT COUNT(*) FROM parent_assignment WHERE subtask_id = :cid"),
        {"cid": child_task["id"]}
    ).scalar()
    assert db_assignment == 0

    final_count = verify_database_state()
    assert final_count == initial_count + 1

# INT-013/003
def test_create_parent_assignment_inactive_parent(client, task_base_path, test_db_session, verify_database_state):
    """Attaching a child to an inactive parent should return 400 and no DB row created."""
    initial_count = verify_database_state()

    parent_resp = client.post(f"{task_base_path}/", json=serialize_payload(INACTIVE_TASK_PAYLOAD))
    parent_task = parent_resp.json()

    child_resp = client.post(f"{task_base_path}/", json=serialize_payload(TASK_CREATE_CHILD))
    child_task = child_resp.json()

    attach_resp = client.post(
        f"{task_base_path}/{parent_task['id']}/subtasks",
        json={"subtask_ids": [child_task["id"]]}
    )
    assert attach_resp.status_code == 400
    assert "inactive" in attach_resp.json()["detail"].lower()

    db_assignment = test_db_session.execute(
        text("SELECT COUNT(*) FROM parent_assignment WHERE subtask_id = :cid"),
        {"cid": child_task["id"]}
    ).scalar()
    assert db_assignment == 0


# INT-013/004
def test_create_parent_assignment_duplicate(client, task_base_path, test_db_session):
    """Attaching a child that already has a parent should return 409 Conflict and not create new row."""
    parent1 = client.post(f"{task_base_path}/", json=serialize_payload(TASK_CREATE_PAYLOAD)).json()
    child = client.post(f"{task_base_path}/", json=serialize_payload(TASK_CREATE_CHILD)).json()

    client.post(f"{task_base_path}/{parent1['id']}/subtasks", json={"subtask_ids": [child["id"]]})

    parent2 = client.post(f"{task_base_path}/", json=serialize_payload(TASK_3_PAYLOAD)).json()
    resp = client.post(
        f"{task_base_path}/{parent2['id']}/subtasks",
        json={"subtask_ids": [child["id"]]}
    )
    assert resp.status_code == 409
    assert "already have a parent" in resp.json()["detail"].lower()

    assignments = test_db_session.execute(
        text("SELECT parent_id FROM parent_assignment WHERE subtask_id = :cid"),
        {"cid": child["id"]}
    ).fetchall()
    assert len(assignments) == 1
    assert assignments[0][0] == parent1["id"]


# INT-013/005
def test_create_parent_assignment_cycle(client, task_base_path, test_db_session):
    """Prevent cycles: attaching a parent as a child of its own descendant should return 409 and not create row."""
    parent = client.post(f"{task_base_path}/", json=serialize_payload(TASK_CREATE_PAYLOAD)).json()
    child = client.post(f"{task_base_path}/", json=serialize_payload(TASK_CREATE_CHILD)).json()

    client.post(f"{task_base_path}/{parent['id']}/subtasks", json={"subtask_ids": [child["id"]]})

    resp = client.post(
        f"{task_base_path}/{child['id']}/subtasks",
        json={"subtask_ids": [parent["id"]]}
    )
    assert resp.status_code == 409
    assert "cycle" in resp.json()["detail"].lower()

    row = test_db_session.execute(
        text("SELECT COUNT(*) FROM parent_assignment WHERE parent_id = :cid AND subtask_id = :pid"),
        {"cid": child["id"], "pid": parent["id"]}
    ).scalar()
    assert row == 0

    assignments = test_db_session.execute(
        text("SELECT parent_id, subtask_id FROM parent_assignment")
    ).fetchall()
    assert assignments == [(parent["id"], child["id"])]

# INT-013/006
def test_create_parent_assignment_attach_nonexistent_child(client, task_base_path):
    """Attaching a non-existent child should return 404."""
    r_parent = client.post(f"{task_base_path}/", json=serialize_payload(TASK_CREATE_PAYLOAD))
    parent_id = r_parent.json()["id"]

    resp = client.post(f"{task_base_path}/{parent_id}/subtasks", json={"subtask_ids": [INVALID_TASK_ID_NONEXISTENT]})
    assert resp.status_code == 404