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
    COMMENT_UPDATE_PAYLOAD,
    COMMENT_UPDATED_RESPONSE,
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

# INT-027/001
def test_update_comment_text(client: TestClient, task_base_path, seed_task_and_user):
    c = client.post(f"{task_base_path}/{VALID_TASK['id']}/comment", json=COMMENT_CREATE_PAYLOAD).json()
    resp = client.patch(f"{task_base_path}/comment/{c['comment_id']}", json=COMMENT_UPDATE_PAYLOAD)
    assert resp.status_code == 200
    updated = resp.json()
    assert updated["comment"] == COMMENT_UPDATED_RESPONSE["comment"]
    refetched = client.get(f"{task_base_path}/comment/{c['comment_id']}").json()
    assert refetched["comment"] == COMMENT_UPDATED_RESPONSE["comment"]

# INT-027/002
def test_update_comment_not_found(client: TestClient, task_base_path, seed_task_and_user):
    resp = client.patch(f"{task_base_path}/comment/{INVALID_COMMENT_ID}", json=COMMENT_UPDATE_PAYLOAD)
    assert resp.status_code == 404
