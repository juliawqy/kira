# tests/backend/integration/comment/test_comment.py
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
    VALID_COMMENT_TEXT,
    UPDATED_COMMENT_TEXT,
    INVALID_COMMENT_ID,
    ANOTHER_USER,
    COMMENT_CREATE_PAYLOAD,
    COMMENT_UPDATE_PAYLOAD,
    COMMENT_MULTIPLE_USERS,
    COMMENT_LIST_TEXTS,
)


@pytest.fixture
def seeded_task_and_user(test_engine):
    """Insert a user, project, and task to satisfy comment foreign keys."""
    TestingSessionLocal = sessionmaker(bind=test_engine, future=True)
    with TestingSessionLocal.begin() as db:
        user = User(**VALID_USER)
        project = Project(**VALID_PROJECT)
        task = Task(**VALID_TASK)
        db.add_all([user, project, task])
    yield


@pytest.fixture
def seed_user_and_task(seeded_task_and_user):
    """Compatibility alias; actual seeding done in seeded_task_and_user."""
    yield


# ---------- TEST CASES ----------

# INT-006/001
def test_add_comment_and_retrieve(client: TestClient, task_base_path, seed_user_and_task):
    """Add a comment via API and verify retrieval."""
    resp = client.post(f"{task_base_path}/{VALID_TASK['id']}/comment", json=COMMENT_CREATE_PAYLOAD)
    assert resp.status_code in (200, 201)
    new_comment = resp.json()
    assert new_comment["comment"] == VALID_COMMENT_TEXT
    comment_id = new_comment["comment_id"]

    resp2 = client.get(f"{task_base_path}/comment/{comment_id}")
    assert resp2.status_code == 200
    fetched = resp2.json()
    assert fetched["comment_id"] == comment_id
    assert fetched["comment"] == VALID_COMMENT_TEXT


# INT-012/001
def test_list_comments_for_task(client: TestClient, task_base_path, seed_user_and_task):
    """List all comments associated with a given task."""
    from tests.mock_data.comment.integration_data import COMMENT_LIST_TEXTS

    for text in COMMENT_LIST_TEXTS:
        resp = client.post(f"{task_base_path}/{VALID_TASK['id']}/comment", json={
            "user_id": VALID_USER["user_id"],
            "comment": text
        })
        assert resp.status_code in (200, 201)

    resp = client.get(f"{task_base_path}/{VALID_TASK['id']}/comments")
    assert resp.status_code == 200
    comments = resp.json()
    assert len(comments) == len(COMMENT_LIST_TEXTS)

    texts = [c["comment"] for c in comments]
    for expected in COMMENT_LIST_TEXTS:
        assert expected in texts



# INT-027/001
def test_update_comment_text(client: TestClient, task_base_path, seed_user_and_task):
    """Update an existing comment’s text."""
    c = client.post(f"{task_base_path}/{VALID_TASK['id']}/comment", json=COMMENT_CREATE_PAYLOAD).json()
    resp = client.patch(f"{task_base_path}/comment/{c['comment_id']}", json=COMMENT_UPDATE_PAYLOAD)
    assert resp.status_code == 200
    updated = resp.json()
    assert updated["comment"] == UPDATED_COMMENT_TEXT

    refetched = client.get(f"{task_base_path}/comment/{c['comment_id']}").json()
    assert refetched["comment"] == UPDATED_COMMENT_TEXT


# INT-005/001
def test_delete_comment(client: TestClient, task_base_path, seed_user_and_task):
    """Delete a comment and ensure it cannot be retrieved again."""
    c = client.post(f"{task_base_path}/{VALID_TASK['id']}/comment", json=COMMENT_CREATE_PAYLOAD).json()
    resp = client.delete(f"{task_base_path}/comment/{c['comment_id']}")
    assert resp.status_code == 200
    assert resp.json() is True

    resp2 = client.get(f"{task_base_path}/comment/{c['comment_id']}")
    assert resp2.status_code == 404


# INT-012/002
def test_get_comment_not_found(client: TestClient, task_base_path, seed_user_and_task):
    """Fetching a non-existent comment returns 404."""
    resp = client.get(f"{task_base_path}/comment/{INVALID_COMMENT_ID}")
    assert resp.status_code == 404


# INT-027/002
def test_update_comment_not_found(client: TestClient, task_base_path, seed_user_and_task):
    """Updating a non-existent comment returns 404."""
    resp = client.patch(f"{task_base_path}/comment/{INVALID_COMMENT_ID}", json=COMMENT_UPDATE_PAYLOAD)
    assert resp.status_code == 404


# INT-005/002
def test_delete_comment_not_found(client: TestClient, task_base_path, seed_user_and_task):
    """Deleting a non-existent comment returns 404."""
    resp = client.delete(f"{task_base_path}/comment/{INVALID_COMMENT_ID}")
    assert resp.status_code == 404


# INT-006/002
def test_add_multiple_comments_different_users(client: TestClient, task_base_path, seed_user_and_task, test_engine):
    """Add comments from multiple users and verify both appear."""
    TestingSessionLocal = sessionmaker(bind=test_engine, future=True)
    with TestingSessionLocal.begin() as db:
        db.add(User(**ANOTHER_USER))

    for payload in COMMENT_MULTIPLE_USERS:
        resp = client.post(f"{task_base_path}/{VALID_TASK['id']}/comment", json=payload)
        assert resp.status_code in (200, 201)

    resp = client.get(f"{task_base_path}/{VALID_TASK['id']}/comments")
    assert resp.status_code == 200
    comments = resp.json()
    user_ids = [c["user_id"] for c in comments]
    assert VALID_USER["user_id"] in user_ids
    assert ANOTHER_USER["user_id"] in user_ids
    assert len(comments) == 2
