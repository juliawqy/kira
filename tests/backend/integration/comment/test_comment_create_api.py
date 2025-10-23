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
    ANOTHER_USER,
    COMMENT_CREATE_PAYLOAD,
    COMMENT_MULTIPLE_USERS,
    COMMENT_RESPONSE,
    COMMENT_MULTIPLE_RESPONSE,
    INVALID_TASK_ID,
    INVALID_USER_ID,
    INVALID_CREATE_NONEXISTENT_USER
)

@pytest.fixture(autouse=True)
def use_test_db(test_engine, monkeypatch):
    """Force all backend services to use the same test database session."""
    from backend.src.services import task, comment, user

    TestSessionLocal = sessionmaker(bind=test_engine, future=True)
    monkeypatch.setattr(task, "SessionLocal", TestSessionLocal)
    monkeypatch.setattr(comment, "SessionLocal", TestSessionLocal)
    monkeypatch.setattr(user, "SessionLocal", TestSessionLocal)

@pytest.fixture
def seed_task_and_user(test_engine):
    """Insert a user, project, and task to satisfy comment foreign keys."""
    TestingSessionLocal = sessionmaker(bind=test_engine, future=True)
    with TestingSessionLocal.begin() as db:
        user = User(**VALID_USER)
        db.add(user)
        db.flush()
        project = Project(**VALID_PROJECT)
        task = Task(**VALID_TASK)
        db.add_all([project, task])
    yield

# INT-006/001
def test_add_comment(client: TestClient, task_base_path, seed_task_and_user):
    """Add a comment via API."""
    resp = client.post(f"{task_base_path}/{VALID_TASK['id']}/comment", json=COMMENT_CREATE_PAYLOAD)
    assert resp.status_code == 200, f"Unexpected status: {resp.status_code}, body={resp.text}"

    after = datetime.now()
    new_comment = resp.json()

    assert new_comment["comment"] == COMMENT_RESPONSE["comment"]
    assert new_comment["user_id"] == COMMENT_RESPONSE["user_id"]
    assert new_comment["task_id"] == COMMENT_RESPONSE["task_id"]
    assert "comment_id" in new_comment
    assert datetime.fromisoformat(new_comment["timestamp"]) <= after + timedelta(seconds=5)

# INT-006/002
def test_add_multiple_comments_different_users(client: TestClient, task_base_path, seed_task_and_user, test_engine):
    """Add comments from multiple users and verify both appear."""
    TestingSessionLocal = sessionmaker(bind=test_engine, future=True)
    with TestingSessionLocal.begin() as db:
        db.add(User(**ANOTHER_USER))

    for payload in COMMENT_MULTIPLE_USERS:
        resp = client.post(f"{task_base_path}/{VALID_TASK['id']}/comment", json=payload)
        assert resp.status_code == 200, f"Unexpected status: {resp.status_code}, body={resp.text}"

    resp = client.get(f"{task_base_path}/{VALID_TASK['id']}/comment")
    assert resp.status_code == 200

    comments = resp.json()
    user_ids = [c["user_id"] for c in comments]
    assert VALID_USER["user_id"] in user_ids
    assert ANOTHER_USER["user_id"] in user_ids
    assert len(comments) == 2
    assert comments[0]["comment"] == COMMENT_MULTIPLE_RESPONSE[0]["comment"]
    assert comments[1]["comment"] == COMMENT_MULTIPLE_RESPONSE[1]["comment"]

# INT-006/003
def test_add_comment_task_not_found(client: TestClient, task_base_path, seed_task_and_user):
    resp = client.post(f"{task_base_path}/{INVALID_TASK_ID}/comment", json=COMMENT_CREATE_PAYLOAD)
    assert resp.status_code == 404
    assert f"Task {INVALID_TASK_ID} not found" in resp.text

# INT-006/004
def test_add_comment_user_not_found(client: TestClient, task_base_path, seed_task_and_user):
    resp = client.post(f"{task_base_path}/{VALID_TASK['id']}/comment", json=INVALID_CREATE_NONEXISTENT_USER)
    assert resp.status_code == 404
    assert f"User {INVALID_USER_ID} not found" in resp.text
