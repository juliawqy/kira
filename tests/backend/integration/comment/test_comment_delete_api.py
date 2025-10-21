import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
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

@pytest.fixture(autouse=True)
def use_test_db(test_engine, monkeypatch):
    from backend.src.services import task, comment, user
    TestSessionLocal = sessionmaker(bind=test_engine, future=True)
    monkeypatch.setattr(task, "SessionLocal", TestSessionLocal)
    monkeypatch.setattr(comment, "SessionLocal", TestSessionLocal)
    monkeypatch.setattr(user, "SessionLocal", TestSessionLocal)

@pytest.fixture
def seed_task_and_user(test_engine):
    TestingSessionLocal = sessionmaker(bind=test_engine, future=True)
    with TestingSessionLocal.begin() as db:
        db.add_all([User(**VALID_USER), Project(**VALID_PROJECT), Task(**VALID_TASK)])
    yield

# INT-005/001
def test_delete_comment(client: TestClient, task_base_path, seed_task_and_user):
    c = client.post(f"{task_base_path}/{VALID_TASK['id']}/comment", json=COMMENT_CREATE_PAYLOAD).json()
    resp = client.delete(f"{task_base_path}/comment/{c['comment_id']}")
    assert resp.status_code == 200
    assert resp.json() is True
    resp2 = client.get(f"{task_base_path}/comment/{c['comment_id']}")
    assert resp2.status_code == 404

# INT-005/002
def test_delete_comment_not_found(client: TestClient, task_base_path, seed_task_and_user):
    resp = client.delete(f"{task_base_path}/comment/{INVALID_COMMENT_ID}")
    assert resp.status_code == 404
