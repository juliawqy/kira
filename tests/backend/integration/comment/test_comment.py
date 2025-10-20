import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from backend.src.database.models.task import Task
from backend.src.database.models.user import User
from tests.mock_data.comment_data import (
    VALID_TASK_ID,
    VALID_USER_ID,
    VALID_COMMENT_TEXT,
    UPDATED_COMMENT_TEXT,
    INVALID_COMMENT_ID,
)
from backend.src.database.models.project import Project


@pytest.fixture
def seeded_task_and_user(test_engine):
    """Insert a user and task to satisfy comment foreign keys (using test engine)."""
    TestingSessionLocal = sessionmaker(bind=test_engine, future=True)
    with TestingSessionLocal.begin() as db:
        user = User(
            user_id=VALID_USER_ID,
            email="tester@example.com",
            name="Tester",
            role="STAFF",
            admin=False,
            hashed_pw="hashed_pw",
            department_id=None,
        )

        project = Project(
            project_id=1,
            project_name="Integration Test Project",
            project_manager=VALID_USER_ID,
            active=True,
        )
        task = Task(
            id=VALID_TASK_ID,
            title="Task for comments",
            description="Integration test task",
            status="To-do",
            priority=5,
            project_id=project.project_id,
            active=True,
        )
        db.add_all([user, task])
    yield


@pytest.fixture
def seed_user_and_task(seeded_task_and_user):
    """Compatibility alias; actual seeding is done in seeded_task_and_user."""
    yield


# ---------- TEST CASES ----------

def test_add_comment_and_retrieve(client: TestClient, task_base_path, seed_user_and_task):
    # Add comment via API
    resp = client.post(f"{task_base_path}/{VALID_TASK_ID}/comment", json={
        "user_id": VALID_USER_ID,
        "comment": VALID_COMMENT_TEXT
    })
    assert resp.status_code == 200 or resp.status_code == 201
    new_comment = resp.json()
    assert new_comment["comment"] == VALID_COMMENT_TEXT
    comment_id = new_comment["comment_id"]

    # Get comment via API
    resp2 = client.get(f"{task_base_path}/comment/{comment_id}")
    assert resp2.status_code == 200
    fetched = resp2.json()
    assert fetched["comment_id"] == comment_id
    assert fetched["comment"] == VALID_COMMENT_TEXT


# INT-090/002
def test_list_comments_for_task(client: TestClient, task_base_path, seed_user_and_task):
    for text in ("First comment", "Second comment"):
        resp = client.post(f"{task_base_path}/{VALID_TASK_ID}/comment", json={
            "user_id": VALID_USER_ID,
            "comment": text
        })
        assert resp.status_code in (200, 201)

    resp = client.get(f"{task_base_path}/{VALID_TASK_ID}/comments")
    assert resp.status_code == 200
    comments = resp.json()
    assert len(comments) == 2
    texts = [c["comment"] for c in comments]
    assert "First comment" in texts
    assert "Second comment" in texts


# INT-090/003
def test_update_comment_text(client: TestClient, task_base_path, seed_user_and_task):
    c = client.post(f"{task_base_path}/{VALID_TASK_ID}/comment", json={
        "user_id": VALID_USER_ID,
        "comment": VALID_COMMENT_TEXT
    }).json()
    resp = client.patch(f"{task_base_path}/comment/{c['comment_id']}", json={
        "comment": UPDATED_COMMENT_TEXT
    })
    assert resp.status_code == 200
    updated = resp.json()
    assert updated["comment"] == UPDATED_COMMENT_TEXT

    refetched = client.get(f"{task_base_path}/comment/{c['comment_id']}").json()
    assert refetched["comment"] == UPDATED_COMMENT_TEXT


# INT-090/004
def test_delete_comment(client: TestClient, task_base_path, seed_user_and_task):
    c = client.post(f"{task_base_path}/{VALID_TASK_ID}/comment", json={
        "user_id": VALID_USER_ID,
        "comment": VALID_COMMENT_TEXT
    }).json()
    resp = client.delete(f"{task_base_path}/comment/{c['comment_id']}")
    assert resp.status_code == 200
    assert resp.json() is True

    resp2 = client.get(f"{task_base_path}/comment/{c['comment_id']}")
    assert resp2.status_code == 404


# INT-090/005
def test_get_comment_not_found(client: TestClient, task_base_path, seed_user_and_task):
    resp = client.get(f"{task_base_path}/comment/{INVALID_COMMENT_ID}")
    assert resp.status_code == 404


# INT-090/006
def test_update_comment_not_found(client: TestClient, task_base_path, seed_user_and_task):
    resp = client.patch(f"{task_base_path}/comment/{INVALID_COMMENT_ID}", json={
        "comment": UPDATED_COMMENT_TEXT
    })
    assert resp.status_code == 404


# INT-090/007
def test_delete_comment_not_found(client: TestClient, task_base_path, seed_user_and_task):
    resp = client.delete(f"{task_base_path}/comment/{INVALID_COMMENT_ID}")
    assert resp.status_code == 404


# INT-090/008
def test_add_multiple_comments_different_users(client: TestClient, task_base_path, seed_user_and_task, test_engine):
    TestingSessionLocal = sessionmaker(bind=test_engine, future=True)
    with TestingSessionLocal.begin() as db:
        new_user = User(
            user_id=3,
            email="another@example.com",
            name="Another User",
            role="STAFF",
            admin=False,
            hashed_pw="hashed_pw2",
            department_id=None,
        )
        db.add(new_user)

    client.post(f"{task_base_path}/{VALID_TASK_ID}/comment", json={"user_id": VALID_USER_ID, "comment": "User1 comment"})
    client.post(f"{task_base_path}/{VALID_TASK_ID}/comment", json={"user_id": 3, "comment": "User2 comment"})

    resp = client.get(f"{task_base_path}/{VALID_TASK_ID}/comments")
    assert resp.status_code == 200
    comments = resp.json()
    user_ids = [c["user_id"] for c in comments]
    assert VALID_USER_ID in user_ids
    assert 3 in user_ids
    assert len(comments) == 2

