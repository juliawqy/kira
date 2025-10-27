import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from backend.src.database.models.user import User
from backend.src.database.models.task import Task
from backend.src.database.models.project import Project
from tests.mock_data.comment.integration_data import (
    VALID_USER,
    ANOTHER_USER,
    VALID_PROJECT,
    VALID_TASK,
    INVALID_COMMENT_ID,
    COMMENT_CREATE_PAYLOAD,
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
    yield

# INT-005/001
def test_delete_comment(client: TestClient, task_base_path, seed_task_and_users):
    c = client.post(f"{task_base_path}/{VALID_TASK['id']}/comment", json=COMMENT_CREATE_PAYLOAD).json()
    resp = client.delete(f"{task_base_path}/comment/{c['comment_id']}")
    assert resp.status_code == 200
    assert resp.json() is True
    resp2 = client.get(f"{task_base_path}/comment/{c['comment_id']}")
    assert resp2.status_code == 404

# INT-005/002
def test_delete_comment_not_found(client: TestClient, task_base_path, seed_task_and_users):
    resp = client.delete(f"{task_base_path}/comment/{INVALID_COMMENT_ID}")
    assert resp.status_code == 404

# INT-005/003 - Authorization Test
def test_delete_comment_unauthorized(client: TestClient, task_base_path, seed_task_and_users):
    """Test that only the comment author can delete their comment."""
    # Create comment with user 1
    c = client.post(f"{task_base_path}/{VALID_TASK['id']}/comment", json=COMMENT_CREATE_PAYLOAD).json()
    
    # Try to delete with user 2 (different user) - should fail
    unauthorized_payload = {
        "requesting_user_id": ANOTHER_USER["user_id"]
    }
    resp = client.delete(f"{task_base_path}/comment/{c['comment_id']}", json=unauthorized_payload)
    assert resp.status_code == 403  # Forbidden
    assert "Only the comment author can delete this comment" in resp.json()["detail"]

# INT-005/004 - Author can delete their own comment
def test_delete_comment_authorized(client: TestClient, task_base_path, seed_task_and_users):
    """Test that the comment author can delete their own comment."""
    # Create comment with user 1
    c = client.post(f"{task_base_path}/{VALID_TASK['id']}/comment", json=COMMENT_CREATE_PAYLOAD).json()
    
    # Delete with same user (author) - should succeed
    authorized_payload = {
        "requesting_user_id": VALID_USER["user_id"]
    }
    resp = client.delete(f"{task_base_path}/comment/{c['comment_id']}", json=authorized_payload)
    assert resp.status_code == 200
    assert resp.json() is True
    
    # Verify comment is deleted
    resp2 = client.get(f"{task_base_path}/comment/{c['comment_id']}")
    assert resp2.status_code == 404
