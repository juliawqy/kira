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
    COMMENT_DELETE_ERROR_PAYLOAD,
    COMMENT_DELETE_AUTHORIZED_PAYLOAD,
    COMMENT_DELETE_UNAUTHORIZED_PAYLOAD,
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

# INT-005/001
def test_delete_comment(client: TestClient, task_base_path, seed_task_and_users):
    resp = client.request("DELETE", f"{task_base_path}/comment/{VALID_COMMENT_ID}", json=COMMENT_DELETE_AUTHORIZED_PAYLOAD)
    assert resp.status_code == 200
    assert resp.json() is True
    resp2 = client.get(f"{task_base_path}/comment/{VALID_COMMENT_ID}")
    assert resp2.status_code == 404

# INT-005/002
def test_delete_comment_not_found(client: TestClient, task_base_path, seed_task_and_users):
    resp = client.request("DELETE", f"{task_base_path}/comment/{INVALID_COMMENT_ID}", json=COMMENT_DELETE_AUTHORIZED_PAYLOAD)
    assert resp.status_code == 404

# INT-005/003
def test_delete_comment_unauthorized(client: TestClient, task_base_path, seed_task_and_users):
    resp = client.request("DELETE", f"{task_base_path}/comment/{VALID_COMMENT_ID}", json=COMMENT_DELETE_UNAUTHORIZED_PAYLOAD)
    assert resp.status_code == 403
    assert "Only the comment author can delete this comment" in resp.json()["detail"]

# INT-005/004
def test_delete_comment_authorized(client: TestClient, task_base_path, seed_task_and_users):
    resp = client.request("DELETE", f"{task_base_path}/comment/{VALID_COMMENT_ID}", json=COMMENT_DELETE_AUTHORIZED_PAYLOAD)
    assert resp.status_code == 200
    assert resp.json() is True
    resp2 = client.get(f"{task_base_path}/comment/{VALID_COMMENT_ID}")
    assert resp2.status_code == 404

# INT-005/005
def test_delete_comment_value_error_handling(client: TestClient, task_base_path, seed_task_and_users):
    resp = client.request("DELETE", f"{task_base_path}/comment/{INVALID_COMMENT_ID}", json=COMMENT_DELETE_ERROR_PAYLOAD)
    assert resp.status_code == 404
