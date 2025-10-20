# tests/backend/integration/comment/test_comment_update_api.py
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
    ANOTHER_USER,
    COMMENT_CREATE_PAYLOAD,
    COMMENT_UPDATE_PAYLOAD,
    COMMENT_MULTIPLE_USERS,
    COMMENT_RESPONSE,
    COMMENT_UPDATED_RESPONSE,
    COMMENT_MULTIPLE_RESPONSE,
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

# INT-027/001
def test_update_comment_text(client: TestClient, task_base_path, seed_task_and_user):
    """Update an existing comment’s text."""
    c = client.post(f"{task_base_path}/{VALID_TASK['id']}/comment", json=COMMENT_CREATE_PAYLOAD).json()
    resp = client.patch(f"{task_base_path}/comment/{c['comment_id']}", json=COMMENT_UPDATE_PAYLOAD)
    assert resp.status_code == 200
    updated = resp.json()
    assert updated["comment"] == COMMENT_UPDATED_RESPONSE["comment"]

    refetched = client.get(f"{task_base_path}/comment/{c['comment_id']}").json()
    assert refetched["comment"] == COMMENT_UPDATED_RESPONSE["comment"]

# INT-027/002
def test_update_comment_not_found(client: TestClient, task_base_path, seed_task_and_user):
    """Updating a non-existent comment returns 404."""
    resp = client.patch(f"{task_base_path}/comment/{INVALID_COMMENT_ID}", json=COMMENT_UPDATE_PAYLOAD)
    assert resp.status_code == 404


