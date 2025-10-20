# tests/backend/integration/comment/test_comment_delete_api.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

from backend.src.database.models.user import User
from backend.src.database.models.task import Task
from backend.src.database.models.project import Project
from tests.mock_data.comment.integration_data import (
    VALID_USER,
    VALID_PROJECT,
    VALID_TASK,
    INVALID_COMMENT_ID,
    COMMENT_CREATE_PAYLOAD,
)


@pytest.fixture
def seed_task_and_user(test_engine):
    """Insert a user, project, and task to satisfy comment foreign keys."""
    TestingSessionLocal = sessionmaker(bind=test_engine, future=True)
    with TestingSessionLocal.begin() as db:
        user = User(**VALID_USER)
        project = Project(**VALID_PROJECT)
        task = Task(**VALID_TASK)
        db.add_all([user, project, task])
    yield

# INT-005/001
def test_delete_comment(client: TestClient, task_base_path, seed_task_and_user):
    """Delete a comment and ensure it cannot be retrieved again."""
    c = client.post(f"{task_base_path}/{VALID_TASK['id']}/comment", json=COMMENT_CREATE_PAYLOAD).json()
    resp = client.delete(f"{task_base_path}/comment/{c['comment_id']}")
    assert resp.status_code == 200
    assert resp.json() is True

    resp2 = client.get(f"{task_base_path}/comment/{c['comment_id']}")
    assert resp2.status_code == 404

# INT-005/002
def test_delete_comment_not_found(client: TestClient, task_base_path, seed_task_and_user):
    """Deleting a non-existent comment returns 404."""
    resp = client.delete(f"{task_base_path}/comment/{INVALID_COMMENT_ID}")
    assert resp.status_code == 404