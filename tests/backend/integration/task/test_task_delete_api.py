# # tests/backend/integration/task/test_task_delete_api.py
from __future__ import annotations
from sqlalchemy import text

import pytest
from datetime import date, datetime
from backend.src.database.models.project import Project
from backend.src.database.models.user import User

from tests.mock_data.task.integration_data import (
    TASK_CREATE_PAYLOAD,
    EXPECTED_TASK_RESPONSE,
    TASK_2_PAYLOAD,
    TASK_2,
    TASK_3_PAYLOAD,
    TASK_3,
    INACTIVE_TASK_PAYLOAD,
    INACTIVE_TASK,
    INVALID_TASK_ID_NONEXISTENT,
    TASK_CREATE_CHILD,
    EXPECTED_TASK_CHILD_RESPONSE,
    VALID_PROJECT,
    VALID_PROJECT_2,
    VALID_USER
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
def create_test_project(test_db_session, clean_db):
    """Ensure a valid project exists for task creation (project_id=1)."""
    
    manager = User(**VALID_USER)
    test_db_session.add(manager)
    test_db_session.flush()

    project = Project(**VALID_PROJECT)
    project2 = Project(**VALID_PROJECT_2)
    test_db_session.add_all([project, project2])
    test_db_session.commit()

# INT-004/001
def test_delete_task_success(client, task_base_path):
    """Verify task deletion."""
    response = client.post(f"{task_base_path}/", json=serialize_payload(TASK_CREATE_PAYLOAD))
    assert response.status_code == 201
    task_id = EXPECTED_TASK_RESPONSE["id"]

    response = client.post(f"{task_base_path}/{task_id}/delete")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == EXPECTED_TASK_RESPONSE["id"]
    assert data["active"] is False

    response = client.get(f"{task_base_path}/")
    assert len(response.json()) == 0

# INT-004/002
def test_delete_task_nonexistent_id_returns_404(client, task_base_path):
    """Verify deleting non-existent task ID returns 404."""
    response = client.post(f"{task_base_path}/{INVALID_TASK_ID_NONEXISTENT}/delete")
    assert response.status_code == 404

# INT-004/003
def test_delete_task_already_inactive_returns_404(client, task_base_path):
    """Verify deleting already inactive task returns 404."""
    response = client.post(f"{task_base_path}/", json=serialize_payload(INACTIVE_TASK_PAYLOAD))
    assert response.status_code == 201
    task_id = INACTIVE_TASK["id"]

    response = client.post(f"{task_base_path}/{task_id}/delete")
    assert response.status_code == 404

# INT-023/001
def test_delete_task_with_subtasks_success(client, task_base_path, test_db_session):
    """Verify deleting a task with subtasks."""
    response = client.post(f"{task_base_path}/", json=serialize_payload(TASK_CREATE_PAYLOAD))
    assert response.status_code == 201
    parent_task_id = EXPECTED_TASK_RESPONSE["id"]

    response = client.post(f"{task_base_path}/", json=serialize_payload(TASK_CREATE_CHILD))
    assert response.status_code == 201
    child_task_id = EXPECTED_TASK_CHILD_RESPONSE["id"]

    attach_resp = client.post(
        f"{task_base_path}/{parent_task_id}/subtasks",
        json={"subtask_ids": [child_task_id]}
    )
    assert attach_resp.status_code == 200

    db_assignment = test_db_session.execute(
        text("SELECT COUNT(*) FROM parent_assignment WHERE parent_id = :pid AND subtask_id = :cid"),
        {"pid": parent_task_id, "cid": child_task_id}
    ).scalar()
    assert db_assignment == 1

    response = client.post(f"{task_base_path}/{parent_task_id}/delete")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == parent_task_id
    assert data["active"] is False

    response = client.get(f"{task_base_path}/")
    assert len(response.json()) == 1

    response = client.get(f"{task_base_path}/{child_task_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == child_task_id

    db_assignment = test_db_session.execute(
        text("SELECT COUNT(*) FROM parent_assignment WHERE subtask_id = :cid"),
        {"cid": child_task_id}
    ).scalar()
    assert db_assignment == 0

# INT-023/002
def test_delete_task_parent_assignment_success(client, task_base_path, test_db_session):
    """Verify ParentAssignment entries are removed when a parent task is deleted."""
    response = client.post(f"{task_base_path}/", json=serialize_payload(TASK_CREATE_PAYLOAD))
    assert response.status_code == 201
    parent_task_id = EXPECTED_TASK_RESPONSE["id"]

    response = client.post(f"{task_base_path}/", json=serialize_payload(TASK_CREATE_CHILD))
    assert response.status_code == 201
    child_task_id = EXPECTED_TASK_CHILD_RESPONSE["id"]

    attach_resp = client.post(
        f"{task_base_path}/{parent_task_id}/subtasks",
        json={"subtask_ids": [child_task_id]}
    )
    assert attach_resp.status_code == 200

    db_assignment = test_db_session.execute(
        text("SELECT COUNT(*) FROM parent_assignment WHERE parent_id = :pid AND subtask_id = :cid"),
        {"pid": parent_task_id, "cid": child_task_id}
    ).scalar()
    assert db_assignment == 1

    response = client.delete(f"{task_base_path}/{parent_task_id}/subtasks/{child_task_id}")
    assert response.status_code == 204

    db_assignment = test_db_session.execute(
        text("SELECT COUNT(*) FROM parent_assignment WHERE subtask_id = :cid"),
        {"cid": child_task_id}
    ).scalar()
    assert db_assignment == 0

    response = client.get(f"{task_base_path}/")
    assert len(response.json()) == 2

# INT-023/003
def test_delete_task_parent_assignment_wrong_child(client, task_base_path, test_db_session):
    """Verify deleting ParentAssignment with wrong child ID returns 404 and does not delete."""
    response = client.post(f"{task_base_path}/", json=serialize_payload(TASK_CREATE_PAYLOAD))
    assert response.status_code == 201
    parent_task_id = EXPECTED_TASK_RESPONSE["id"]

    response = client.post(f"{task_base_path}/", json=serialize_payload(TASK_CREATE_CHILD))
    assert response.status_code == 201
    child_task_id = EXPECTED_TASK_CHILD_RESPONSE["id"]

    attach_resp = client.post(
        f"{task_base_path}/{parent_task_id}/subtasks",
        json={"subtask_ids": [child_task_id]}
    )
    assert attach_resp.status_code == 200

    response = client.post(f"{task_base_path}/", json=serialize_payload(TASK_2_PAYLOAD))
    assert response.status_code == 201
    other_parent_task_id = TASK_2["id"]

    response = client.post(f"{task_base_path}/", json=serialize_payload(TASK_3_PAYLOAD))
    assert response.status_code == 201
    other_child_task_id = TASK_3["id"]

    attach_resp = client.post(
        f"{task_base_path}/{other_parent_task_id}/subtasks",
        json={"subtask_ids": [other_child_task_id]}
    )
    assert attach_resp.status_code == 200

    db_assignment = test_db_session.execute(
        text("SELECT COUNT(*) FROM parent_assignment")
    ).scalar()
    assert db_assignment == 2

    response = client.delete(f"{task_base_path}/{parent_task_id}/subtasks/{other_child_task_id}")
    assert response.status_code == 404

    db_assignment = test_db_session.execute(
        text("SELECT COUNT(*) FROM parent_assignment")
    ).scalar()
    assert db_assignment == 2

# INT-023/004
def test_delete_task_parent_assignment_nonexistent_ids_return_404(client, task_base_path, test_db_session):
    """Verify deleting ParentAssignment with non-existent IDs returns 404."""

    response = client.post(f"{task_base_path}/", json=serialize_payload(TASK_CREATE_PAYLOAD))
    assert response.status_code == 201
    parent_task_id = EXPECTED_TASK_RESPONSE["id"]

    response = client.post(f"{task_base_path}/", json=serialize_payload(TASK_CREATE_CHILD))
    assert response.status_code == 201
    child_task_id = EXPECTED_TASK_CHILD_RESPONSE["id"]

    attach_resp = client.post(
        f"{task_base_path}/{parent_task_id}/subtasks",
        json={"subtask_ids": [child_task_id]}
    )
    assert attach_resp.status_code == 200

    db_assignment = test_db_session.execute(
        text("SELECT COUNT(*) FROM parent_assignment WHERE parent_id = :pid AND subtask_id = :cid"),
        {"pid": parent_task_id, "cid": child_task_id}
    ).scalar()
    assert db_assignment == 1

    response = client.delete(f"{task_base_path}/{parent_task_id}/subtasks/{INVALID_TASK_ID_NONEXISTENT}")
    assert response.status_code == 404

    response = client.delete(f"{task_base_path}/{INVALID_TASK_ID_NONEXISTENT}/subtasks/{child_task_id}")
    assert response.status_code == 404

# # UNI-004/003
# @patch("backend.src.services.task.SessionLocal")
# def test_delete_nonexistent_task_raises_value_error(mock_session_local):
#     """Delete non-existent task raises ValueError."""
#     from backend.src.services import task as task_service
    
#     mock_session = MagicMock()
#     mock_session_local.begin.return_value.__enter__.return_value = mock_session

#     mock_session.get.return_value = None
    
#     with pytest.raises(ValueError) as exc:
#         task_service.delete_task(INVALID_TASK_ID_NONEXISTENT)

#     assert "Task not found" in str(exc.value)
#     mock_session.get.assert_called_once_with(task_service.Task, INVALID_TASK_ID_NONEXISTENT)

# # UNI-004/004
# @patch("backend.src.services.task.SessionLocal")
# def test_delete_already_inactive_task_raises_value_error(mock_session_local):
#     """Delete already inactive task raises ValueError."""
#     from backend.src.services import task as task_service
    
#     mock_session = MagicMock()
#     mock_session_local.begin.return_value.__enter__.return_value = mock_session
    
#     # Mock existing inactive task
#     mock_task = MagicMock()
#     mock_task.id = INACTIVE_TASK["id"]
#     mock_task.active = False
#     mock_session.get.return_value = mock_task
    
#     with pytest.raises(ValueError) as exc:
#         task_service.delete_task(INACTIVE_TASK["id"])
    
#     assert "Task not found" in str(exc.value)
#     mock_session.get.assert_called_once_with(task_service.Task, INACTIVE_TASK["id"])