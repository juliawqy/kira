import pytest
import tempfile
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.src.database.db_setup import Base
from backend.src.services import comment as comment_service
from backend.src.database.models.task import Task
from backend.src.database.models.user import User
from tests.mock_data.comment_data import (
    VALID_TASK_ID,
    VALID_USER_ID,
    VALID_COMMENT_TEXT,
    UPDATED_COMMENT_TEXT,
    INVALID_COMMENT_ID,
)
from unittest.mock import patch
from backend.src.database.models.project import Project


@pytest.fixture(autouse=True)
def isolated_test_db():
    """Create an isolated SQLite DB for each integration test."""
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)
    engine = create_engine(f"sqlite:///{db_path}", echo=False)
    Base.metadata.create_all(bind=engine)
    TestSessionLocal = sessionmaker(bind=engine)

    with patch("backend.src.services.comment.SessionLocal", TestSessionLocal):
        yield engine

    engine.dispose()
    try:
        os.unlink(db_path)
    except (OSError, PermissionError):
        pass


@pytest.fixture
def seed_user_and_task(isolated_test_db):
    """Insert a user and task to satisfy comment foreign keys."""
    TestSessionLocal = sessionmaker(bind=isolated_test_db)
    with TestSessionLocal.begin() as db:
        user = User(
            user_id=VALID_USER_ID,
            email="tester@example.com",
            name="Tester",
            role="STAFF",
            admin=False,
            hashed_pw="hashed_pw",
            department_id=None,
        )

        # Insert dummy project
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
            priority=5,  # Must be int
            project_id=project.project_id,
            active=True,
        )
        db.add_all([user, task])
        db.flush()
    yield


# ---------- TEST CASES ----------

# INT-090/001
def test_add_comment_and_retrieve(isolated_test_db, seed_user_and_task):
    """Create a comment and retrieve it by ID."""
    new_comment = comment_service.add_comment(
        task_id=VALID_TASK_ID, user_id=VALID_USER_ID, comment=VALID_COMMENT_TEXT
    )
    assert new_comment["comment"] == VALID_COMMENT_TEXT
    assert new_comment["task_id"] == VALID_TASK_ID
    assert new_comment["user_id"] == VALID_USER_ID

    fetched = comment_service.get_comment(new_comment["comment_id"])
    assert fetched["comment_id"] == new_comment["comment_id"]
    assert fetched["comment"] == VALID_COMMENT_TEXT


# INT-090/002
def test_list_comments_for_task(isolated_test_db, seed_user_and_task):
    """List multiple comments for a single task."""
    comment_service.add_comment(VALID_TASK_ID, VALID_USER_ID, "First comment")
    comment_service.add_comment(VALID_TASK_ID, VALID_USER_ID, "Second comment")

    comments = comment_service.list_comments(VALID_TASK_ID)
    assert len(comments) == 2
    texts = [c["comment"] for c in comments]
    assert "First comment" in texts
    assert "Second comment" in texts


# INT-090/003
def test_update_comment_text(isolated_test_db, seed_user_and_task):
    """Update a comment’s text and verify persistence."""
    c = comment_service.add_comment(VALID_TASK_ID, VALID_USER_ID, VALID_COMMENT_TEXT)
    updated = comment_service.update_comment(c["comment_id"], UPDATED_COMMENT_TEXT)
    assert updated["comment"] == UPDATED_COMMENT_TEXT

    refetched = comment_service.get_comment(c["comment_id"])
    assert refetched["comment"] == UPDATED_COMMENT_TEXT


# INT-090/004
def test_delete_comment(isolated_test_db, seed_user_and_task):
    """Delete a comment and verify it’s gone."""
    c = comment_service.add_comment(VALID_TASK_ID, VALID_USER_ID, VALID_COMMENT_TEXT)
    result = comment_service.delete_comment(c["comment_id"])
    assert result is True

    refetched = comment_service.get_comment(c["comment_id"])
    assert refetched is None


# INT-090/005
def test_get_comment_not_found(isolated_test_db, seed_user_and_task):
    """Fetching a non-existent comment should return None."""
    result = comment_service.get_comment(INVALID_COMMENT_ID)
    assert result is None


# INT-090/006
def test_update_comment_not_found(isolated_test_db, seed_user_and_task):
    """Updating a missing comment should raise ValueError."""
    with pytest.raises(ValueError):
        comment_service.update_comment(INVALID_COMMENT_ID, UPDATED_COMMENT_TEXT)


# INT-090/007
def test_delete_comment_not_found(isolated_test_db, seed_user_and_task):
    """Deleting a missing comment should raise ValueError."""
    with pytest.raises(ValueError):
        comment_service.delete_comment(INVALID_COMMENT_ID)


# INT-090/008
def test_add_multiple_comments_different_users(isolated_test_db, seed_user_and_task):
    """Add comments from two users and verify both appear."""
    TestSessionLocal = sessionmaker(bind=isolated_test_db)
    with TestSessionLocal.begin() as db:
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
        db.flush()

    comment_service.add_comment(VALID_TASK_ID, VALID_USER_ID, "User1 comment")
    comment_service.add_comment(VALID_TASK_ID, 3, "User2 comment")

    comments = comment_service.list_comments(VALID_TASK_ID)
    user_ids = [c["user_id"] for c in comments]

    assert VALID_USER_ID in user_ids
    assert 3 in user_ids
    assert len(comments) == 2

