import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from backend.src.database.models.user import User
from backend.src.database.models.task import Task
from backend.src.database.models.project import Project
from tests.mock_data.comment.integration_data import (
    VALID_USER,
    ANOTHER_USER,
    VALID_PROJECT,
    VALID_TASK,
    VALID_COMMENT,
    INVALID_COMMENT_ID,
    VALID_COMMENT_ID,
    COMMENT_CREATE_PAYLOAD,
    COMMENT_UPDATE_PAYLOAD,
    COMMENT_UPDATED_RESPONSE,
    COMMENT_UPDATE_ERROR_PAYLOAD,
    COMMENT_UPDATE_AUTHORIZED_PAYLOAD,
    COMMENT_UPDATE_UNAUTHORIZED_PAYLOAD,
)

@pytest.fixture(autouse=True)
def use_test_db(test_engine, monkeypatch):
    from backend.src.services import task, comment, user
    TestSessionLocal = sessionmaker(bind=test_engine, future=True)
    monkeypatch.setattr(task, "SessionLocal", TestSessionLocal)
    monkeypatch.setattr(comment, "SessionLocal", TestSessionLocal)
    monkeypatch.setattr(user, "SessionLocal", TestSessionLocal)

@pytest.fixture
def seed_task_and_users(test_engine):
    TestingSessionLocal = sessionmaker(bind=test_engine, future=True)
    with TestingSessionLocal.begin() as db:
        user1 = User(**VALID_USER)
        user2 = User(**ANOTHER_USER)
        db.add_all([user1, user2])
        db.flush()
        project = Project(**VALID_PROJECT)
        task = Task(**VALID_TASK)
        db.add_all([project, task])
        db.flush()
        from backend.src.database.models.comment import Comment
        comment = Comment(**VALID_COMMENT)
        db.add(comment)
    yield

# INT-027/001
def test_update_comment_text(client: TestClient, task_base_path, seed_task_and_users):
    resp = client.patch(f"{task_base_path}/comment/{VALID_COMMENT_ID}", json=COMMENT_UPDATE_PAYLOAD)
    assert resp.status_code == 200
    updated = resp.json()
    assert updated["comment"] == COMMENT_UPDATED_RESPONSE["comment"]
    refetched = client.get(f"{task_base_path}/comment/{VALID_COMMENT_ID}").json()
    assert refetched["comment"] == COMMENT_UPDATED_RESPONSE["comment"]

# INT-027/002
def test_update_comment_not_found(client: TestClient, task_base_path, seed_task_and_users):
    resp = client.patch(f"{task_base_path}/comment/{INVALID_COMMENT_ID}", json=COMMENT_UPDATE_PAYLOAD)
    assert resp.status_code == 404

# INT-027/003
def test_update_comment_unauthorized(client: TestClient, task_base_path, seed_task_and_users):
    """Test that only the comment author can update their comment."""
    resp = client.patch(f"{task_base_path}/comment/{VALID_COMMENT_ID}", json=COMMENT_UPDATE_UNAUTHORIZED_PAYLOAD)
    assert resp.status_code == 403
    assert "Only the comment author can update this comment" in resp.json()["detail"]

# INT-027/004
def test_update_comment_authorized(client: TestClient, task_base_path, seed_task_and_users):
    """Test that the comment author can update their own comment."""
    resp = client.patch(f"{task_base_path}/comment/{VALID_COMMENT_ID}", json=COMMENT_UPDATE_AUTHORIZED_PAYLOAD)
    assert resp.status_code == 200
    updated = resp.json()
    assert updated["comment"] == COMMENT_UPDATED_RESPONSE["comment"]

# INT-027/005 
def test_update_comment_value_error_handling(client: TestClient, task_base_path, seed_task_and_users):
    resp = client.patch(f"{task_base_path}/comment/{INVALID_COMMENT_ID}", json=COMMENT_UPDATE_ERROR_PAYLOAD)
    assert resp.status_code == 404