# # tests/backend/integration/task/test_task_update_api.py
from __future__ import annotations

import pytest
from datetime import date, datetime
from backend.src.database.models.project import Project

from backend.src.enums.task_status import TaskStatus
from tests.mock_data.task.integration_data import (
    TASK_CREATE_PAYLOAD,
    EXPECTED_TASK_RESPONSE,
    TASK_UPDATE_PAYLOAD,
    EXPECTED_TASK_UPDATED,
    TASK_UPDATE_PARTIAL_TITLE,
    TASK_UPDATE_PARTIAL_PRIORITY,
    TASK_UPDATE_PARTIAL_DATES,
    TASK_UPDATE_EMPTY,
    INVALID_STATUS,
    INVALID_TASK_ID_NONEXISTENT,
    VALID_PROJECT,
    VALID_PROJECT_2
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

@pytest.fixture(scope="function")
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

@pytest.fixture(autouse=True)
def create_test_project(test_db_session):
    """Ensure a valid project exists for task creation (project_id=1)."""

    project = Project(**VALID_PROJECT)
    project2 = Project(**VALID_PROJECT_2)
    test_db_session.add_all([project, project2])
    test_db_session.commit()


# INT-003/001
def test_update_task_success(client, task_base_path):
    """Verify task update."""
    response = client.post(f"{task_base_path}/", json=serialize_payload(TASK_CREATE_PAYLOAD))
    assert response.status_code == 201
    task_id = EXPECTED_TASK_RESPONSE["id"]

    response = client.patch(f"{task_base_path}/{task_id}", json=serialize_payload(TASK_UPDATE_PAYLOAD))
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert data["id"] == EXPECTED_TASK_UPDATED["id"]
    assert data["title"] == EXPECTED_TASK_UPDATED["title"]
    assert data["description"] == EXPECTED_TASK_UPDATED["description"]
    assert data["start_date"] == EXPECTED_TASK_UPDATED["start_date"].isoformat()
    assert data["deadline"] == EXPECTED_TASK_UPDATED["deadline"].isoformat()
    assert data["status"] == EXPECTED_TASK_UPDATED["status"]

# INT-003/002
@pytest.mark.parametrize("update_patch", [TASK_UPDATE_PARTIAL_TITLE, TASK_UPDATE_PARTIAL_PRIORITY, TASK_UPDATE_PARTIAL_DATES])
def test_partial_update_task_success(client, task_base_path, update_patch):
    """Verify partial task update works."""
    response = client.post(f"{task_base_path}/", json=serialize_payload(TASK_CREATE_PAYLOAD))
    assert response.status_code == 201
    original_data = response.json()
    task_id = original_data["id"]
    response = client.patch(f"{task_base_path}/{task_id}", json=serialize_payload(update_patch))
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert data["id"] == original_data["id"]
    for key in data.keys():
        if key in update_patch:
            assert data[key] == update_patch[key].isoformat() if isinstance(update_patch[key], (date, datetime)) else update_patch[key]
        else:
            assert data[key] == original_data[key]

# INT-003/003
def test_update_task_invalid_id(client, task_base_path):
    """Verify updating a non-existent task ID returns 404."""
    response = client.patch(f"{task_base_path}/{INVALID_TASK_ID_NONEXISTENT}", json=serialize_payload(TASK_UPDATE_PAYLOAD))
    assert response.status_code == 404

# INT-003/004
def test_update_task_empty_payload(client, task_base_path):
    """Verify updating a task with empty payload updates fields to None."""
    response = client.post(f"{task_base_path}/", json=serialize_payload(TASK_CREATE_PAYLOAD))
    assert response.status_code == 201
    task_id = EXPECTED_TASK_RESPONSE["id"]
    original_data = response.json()

    response = client.patch(f"{task_base_path}/{task_id}", json=TASK_UPDATE_EMPTY)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == original_data["id"]
    assert data["title"] == original_data["title"]
    assert data["description"] == original_data["description"]
    assert data["start_date"] == original_data["start_date"]
    assert data["deadline"] == original_data["deadline"]
    assert data["priority"] == original_data["priority"]
    assert data["project_id"] == original_data["project_id"]
    assert data["status"] == original_data["status"]

# INT-022/001
@pytest.mark.parametrize("valid_status", [status.value for status in TaskStatus])
def test_update_task_status(client, task_base_path, valid_status):
    """Verify 'status' field is updated."""
    response = client.post(f"{task_base_path}/", json=serialize_payload(TASK_CREATE_PAYLOAD))
    assert response.status_code == 201
    task_id = EXPECTED_TASK_RESPONSE["id"]
    original_status = response.json()["status"]
    assert original_status == TaskStatus.TO_DO.value
    if valid_status == original_status:
        original_status = TaskStatus.IN_PROGRESS.value

    response = client.post(f"{task_base_path}/{task_id}/status/{valid_status}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["status"] == valid_status
    assert data["status"] != original_status

# INT-022/002
def test_update_task_status_invalid_status_value(client, task_base_path):
    """Verify updating 'status' to invalid value returns 400."""
    response = client.post(f"{task_base_path}/", json=serialize_payload(TASK_CREATE_PAYLOAD))
    assert response.status_code == 201
    task_id = EXPECTED_TASK_RESPONSE["id"]

    response = client.post(f"{task_base_path}/{task_id}/status/{INVALID_STATUS}")
    assert response.status_code == 404

# INT-022/003
def test_update_task_status_invalid_id(client, task_base_path):
    """Verify updating 'status' of non-existent task ID returns 404."""
    response = client.post(f"{task_base_path}/{INVALID_TASK_ID_NONEXISTENT}/status/{TaskStatus.COMPLETED.value}")
    assert response.status_code == 404
