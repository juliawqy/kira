# tests/backend/integration/comment/test_comment_get_api.py
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

# INT-012/001
def test_list_comments_for_task(client: TestClient, task_base_path, seed_task_and_user):
    """List all comments associated with a given task."""
    from tests.mock_data.comment.integration_data import COMMENT_LIST_TEXTS

    for text in COMMENT_LIST_TEXTS:
        resp = client.post(f"{task_base_path}/{VALID_TASK['id']}/comment", json={
            "user_id": VALID_USER["user_id"],
            "comment": text
        })
        assert resp.status_code in (200, 201)

    resp = client.get(f"{task_base_path}/{VALID_TASK['id']}/comment")
    assert resp.status_code == 200
    comments = resp.json()
    assert len(comments) == len(COMMENT_LIST_TEXTS)

    texts = [c["comment"] for c in comments]
    for expected in COMMENT_LIST_TEXTS:
        assert expected in texts

# INT-012/002
def test_get_comment_not_found(client: TestClient, task_base_path, seed_task_and_user):
    """Fetching a non-existent comment returns 404."""
    resp = client.get(f"{task_base_path}/comment/{INVALID_COMMENT_ID}")
    assert resp.status_code == 404

# INT-012/003
def test_get_comment_by_id(client: TestClient, task_base_path, seed_task_and_user):
    """Fetch a specific comment by its ID."""
    resp = client.post(f"{task_base_path}/{VALID_TASK['id']}/comment", json=COMMENT_CREATE_PAYLOAD)
    assert resp.status_code in (200, 201)

    resp2 = client.get(f"{task_base_path}/comment/{COMMENT_RESPONSE['comment_id']}")
    assert resp2.status_code == 200
    fetched = resp2.json()
    assert fetched["comment_id"] == COMMENT_RESPONSE["comment_id"]
    assert fetched["comment"] == COMMENT_RESPONSE["comment"]

