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
    COMMENT_RESPONSE,
    INVALID_TASK_ID
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

# INT-012/001
def test_list_comments_for_task(client: TestClient, task_base_path, seed_task_and_user):
    from tests.mock_data.comment.integration_data import COMMENT_LIST_TEXTS
    for text in COMMENT_LIST_TEXTS:
        resp = client.post(f"{task_base_path}/{VALID_TASK['id']}/comment", json={"user_id": VALID_USER["user_id"], "comment": text})
        assert resp.status_code == 200
    resp = client.get(f"{task_base_path}/{VALID_TASK['id']}/comment")
    assert resp.status_code == 200
    comments = resp.json()
    texts = [c["comment"] for c in comments]
    for expected in COMMENT_LIST_TEXTS:
        assert expected in texts

# INT-012/002
def test_get_comment_not_found(client: TestClient, task_base_path, seed_task_and_user):
    resp = client.get(f"{task_base_path}/comment/{INVALID_COMMENT_ID}")
    assert resp.status_code == 404

# INT-012/003
def test_get_comment_by_id(client: TestClient, task_base_path, seed_task_and_user):
    resp = client.post(f"{task_base_path}/{VALID_TASK['id']}/comment", json=COMMENT_CREATE_PAYLOAD)
    assert resp.status_code == 200
    resp2 = client.get(f"{task_base_path}/comment/{COMMENT_RESPONSE['comment_id']}")
    assert resp2.status_code == 200
    fetched = resp2.json()
    assert fetched["comment_id"] == COMMENT_RESPONSE["comment_id"]
    assert fetched["comment"] == COMMENT_RESPONSE["comment"]

# INT-012/004
def test_list_comments_task_not_found(client: TestClient, task_base_path, seed_task_and_user):
    resp = client.get(f"{task_base_path}/{INVALID_TASK_ID}/comment")
    assert resp.status_code == 404
    assert f"Task {INVALID_TASK_ID} not found" in resp.text