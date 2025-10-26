# tests/backend/integration/comment/test_comment_handler.py
import pytest
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

from backend.src.database.models.user import User
from backend.src.database.models.task import Task
from backend.src.database.models.project import Project
from backend.src.database.models.comment import Comment

from backend.src.handlers.comment_handler import (
    add_comment,
    list_comments,
    get_comment,
    update_comment,
    delete_comment,
    list_comments_by_user,
    get_user_comment_count,
    get_user_comments_with_task_info,
    get_recent_user_comments,
    get_user_comments_by_task,
)

from tests.mock_data.comment.integration_data import (
    VALID_USER,
    VALID_PROJECT,
    VALID_TASK,
    ANOTHER_USER,
    COMMENT_CREATE_PAYLOAD,
    COMMENT_MULTIPLE_USERS,
    COMMENT_RESPONSE,
    COMMENT_MULTIPLE_RESPONSE,
    INVALID_TASK_ID,
    INVALID_USER_ID,
    INVALID_CREATE_NONEXISTENT_USER,
    VALID_COMMENT_ID,
    INVALID_COMMENT_ID,
)

@pytest.fixture(autouse=True)
def use_test_db(test_engine, monkeypatch):
    """Force all backend services to use the same test database session."""
    from backend.src.services import task, comment, user

    TestSessionLocal = sessionmaker(bind=test_engine, future=True)
    monkeypatch.setattr(task, "SessionLocal", TestSessionLocal)
    monkeypatch.setattr(comment, "SessionLocal", TestSessionLocal)
    monkeypatch.setattr(user, "SessionLocal", TestSessionLocal)

@pytest.fixture
def seed_task_and_users(test_engine):
    """Insert users, project, and task to satisfy comment foreign keys."""
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

@pytest.fixture
def seed_comments(test_engine, seed_task_and_users):
    """Create some comments for testing."""
    TestingSessionLocal = sessionmaker(bind=test_engine, future=True)
    with TestingSessionLocal.begin() as db:
        comment1 = Comment(
            task_id=VALID_TASK['id'],
            user_id=VALID_USER['user_id'],
            comment="First comment by user 1"
        )
        comment2 = Comment(
            task_id=VALID_TASK['id'],
            user_id=ANOTHER_USER['user_id'],
            comment="Second comment by user 2"
        )
        comment3 = Comment(
            task_id=VALID_TASK['id'],
            user_id=VALID_USER['user_id'],
            comment="Third comment by user 1"
        )
        db.add_all([comment1, comment2, comment3])
    yield


# -------- Basic Comment Handler Tests --------------------------------------------

def test_add_comment_success(seed_task_and_users):
    """Test adding a comment via handler."""
    comment = add_comment(
        task_id=VALID_TASK['id'],
        user_id=VALID_USER['user_id'],
        comment_text="Test comment"
    )
    
    assert comment['comment'] == "Test comment"
    assert comment['user_id'] == VALID_USER['user_id']
    assert comment['task_id'] == VALID_TASK['id']
    assert 'comment_id' in comment
    assert 'timestamp' in comment
    assert 'user' in comment
    assert comment['user']['user_id'] == VALID_USER['user_id']
    assert comment['user']['email'] == VALID_USER['email']


def test_add_comment_task_not_found(seed_task_and_users):
    """Test adding comment to non-existent task."""
    with pytest.raises(ValueError, match=f"Task {INVALID_TASK_ID} not found"):
        add_comment(
            task_id=INVALID_TASK_ID,
            user_id=VALID_USER['user_id'],
            comment_text="Test comment"
        )


def test_add_comment_user_not_found(seed_task_and_users):
    """Test adding comment with non-existent user."""
    with pytest.raises(ValueError, match=f"User {INVALID_USER_ID} not found"):
        add_comment(
            task_id=VALID_TASK['id'],
            user_id=INVALID_USER_ID,
            comment_text="Test comment"
        )


def test_list_comments_success(seed_comments):
    """Test listing comments for a task."""
    comments = list_comments(VALID_TASK['id'])
    
    assert len(comments) == 3
    for comment in comments:
        assert 'user' in comment
        assert comment['user']['user_id'] in [VALID_USER['user_id'], ANOTHER_USER['user_id']]
        assert comment['user']['email'] is not None
        assert comment['user']['name'] is not None


def test_list_comments_task_not_found(seed_comments):
    """Test listing comments for non-existent task."""
    with pytest.raises(ValueError, match=f"Task {INVALID_TASK_ID} not found"):
        list_comments(INVALID_TASK_ID)


def test_get_comment_success(seed_comments):
    """Test getting a specific comment."""
    comments = list_comments(VALID_TASK['id'])
    comment_id = comments[0]['comment_id']
    
    comment = get_comment(comment_id)
    assert comment['comment_id'] == comment_id
    assert 'user' in comment
    assert comment['user']['user_id'] == comment['user_id']


def test_get_comment_not_found(seed_comments):
    """Test getting non-existent comment."""
    with pytest.raises(ValueError, match=f"Comment {INVALID_COMMENT_ID} not found"):
        get_comment(INVALID_COMMENT_ID)


def test_update_comment_success(seed_comments):
    """Test updating a comment."""
    comments = list_comments(VALID_TASK['id'])
    comment_id = comments[0]['comment_id']
    
    updated_comment = update_comment(comment_id, "Updated comment text")
    assert updated_comment['comment'] == "Updated comment text"
    assert updated_comment['comment_id'] == comment_id


def test_delete_comment_success(seed_comments):
    """Test deleting a comment."""
    comments = list_comments(VALID_TASK['id'])
    comment_id = comments[0]['comment_id']
    
    result = delete_comment(comment_id)
    assert result is True
    
    # Verify comment is deleted
    with pytest.raises(ValueError, match=f"Comment {comment_id} not found"):
        get_comment(comment_id)


# -------- User-Comment Integration Tests -----------------------------------------

def test_list_comments_by_user_success(seed_comments):
    """Test listing comments by a specific user."""
    user_id = VALID_USER['user_id']
    comments = list_comments_by_user(user_id)
    
    assert len(comments) == 2
    assert all(comment['user_id'] == user_id for comment in comments)
    
    # Check that user data is included
    for comment in comments:
        assert 'user' in comment
        assert comment['user']['user_id'] == user_id
        assert comment['user']['email'] == VALID_USER['email']


def test_list_comments_by_user_empty(seed_task_and_users):
    """Test listing comments for a user with no comments."""
    user_id = VALID_USER['user_id']
    comments = list_comments_by_user(user_id)
    assert len(comments) == 0


def test_list_comments_by_user_not_found(seed_comments):
    """Test listing comments for non-existent user."""
    with pytest.raises(ValueError, match=f"User {INVALID_USER_ID} not found"):
        list_comments_by_user(INVALID_USER_ID)


def test_get_user_comment_count_success(seed_comments):
    """Test getting comment count for a user."""
    user_id = VALID_USER['user_id']
    count = get_user_comment_count(user_id)
    assert count == 2


def test_get_user_comment_count_zero(seed_task_and_users):
    """Test getting comment count for a user with no comments."""
    user_id = VALID_USER['user_id']
    count = get_user_comment_count(user_id)
    assert count == 0


def test_get_user_comment_count_not_found(seed_comments):
    """Test getting comment count for non-existent user."""
    with pytest.raises(ValueError, match=f"User {INVALID_USER_ID} not found"):
        get_user_comment_count(INVALID_USER_ID)


def test_get_user_comments_with_task_info_success(seed_comments):
    """Test getting user comments with task information."""
    user_id = VALID_USER['user_id']
    comments = get_user_comments_with_task_info(user_id)
    
    assert len(comments) == 2
    for comment in comments:
        assert 'user' in comment
        assert 'task' in comment
        assert comment['task'] is not None
        assert comment['task']['id'] == VALID_TASK['id']
        assert comment['task']['title'] == VALID_TASK['title']


def test_get_user_comments_with_task_info_not_found(seed_comments):
    """Test getting user comments with task info for non-existent user."""
    with pytest.raises(ValueError, match=f"User {INVALID_USER_ID} not found"):
        get_user_comments_with_task_info(INVALID_USER_ID)


def test_get_user_comments_with_task_info_task_not_found(seed_comments, test_engine):
    """Test getting user comments with task info when task service fails."""
    # Mock the task service to raise an exception to test error handling
    from unittest.mock import patch
    
    user_id = VALID_USER['user_id']
    
    with patch('backend.src.handlers.comment_handler.task_service.get_task_with_subtasks') as mock_get_task:
        # Make the task service raise an exception for the first task
        def side_effect(task_id):
            if task_id == VALID_TASK['id']:
                raise Exception("Task service error")
            return None
        mock_get_task.side_effect = side_effect
        
        comments = get_user_comments_with_task_info(user_id)
        
        # Should include the comment but with task=None due to error handling
        assert len(comments) == 2
        for comment in comments:
            assert comment['task'] is None  # All tasks should be None due to error


def test_get_user_comments_with_task_info_task_falsy(seed_comments):
    """Test getting user comments with task info when task is falsy."""
    from unittest.mock import patch
    
    user_id = VALID_USER['user_id']
    
    with patch('backend.src.handlers.comment_handler.task_service.get_task_with_subtasks') as mock_get_task:
        # Make the task service return a falsy value (empty string, 0, False, etc.)
        mock_get_task.return_value = False  # This will trigger the else branch
        
        comments = get_user_comments_with_task_info(user_id)
        
        # Should include the comment but with task=None due to falsy task
        assert len(comments) == 2
        for comment in comments:
            assert comment['task'] is None


def test_get_recent_user_comments_success(seed_comments):
    """Test getting recent comments by a user."""
    user_id = VALID_USER['user_id']
    comments = get_recent_user_comments(user_id, limit=1)
    
    assert len(comments) == 1
    assert comments[0]['user_id'] == user_id
    assert 'user' in comments[0]


def test_get_recent_user_comments_with_limit(seed_comments):
    """Test getting recent comments with limit."""
    user_id = VALID_USER['user_id']
    comments = get_recent_user_comments(user_id, limit=5)
    
    assert len(comments) <= 5
    assert all(comment['user_id'] == user_id for comment in comments)


def test_get_recent_user_comments_not_found(seed_comments):
    """Test getting recent comments for non-existent user."""
    with pytest.raises(ValueError, match=f"User {INVALID_USER_ID} not found"):
        get_recent_user_comments(INVALID_USER_ID)


def test_get_user_comments_by_task_success(seed_comments):
    """Test getting user comments for a specific task."""
    user_id = VALID_USER['user_id']
    task_id = VALID_TASK['id']
    
    comments = get_user_comments_by_task(user_id, task_id)
    
    assert len(comments) == 2
    assert all(comment['user_id'] == user_id for comment in comments)
    assert all(comment['task_id'] == task_id for comment in comments)


def test_get_user_comments_by_task_empty(seed_comments, test_engine):
    """Test getting user comments for a task where user has no comments."""
    user_id = ANOTHER_USER['user_id']
    task_id = VALID_TASK['id']
    
    # Create a new task
    TestingSessionLocal = sessionmaker(bind=test_engine, future=True)
    with TestingSessionLocal.begin() as db:
        new_task = Task(
            id=999,
            title="New Task",
            description="Task with no comments from this user",
            status="To-do",
            priority=5,
            project_id=VALID_PROJECT['project_id'],
            active=True
        )
        db.add(new_task)
    
    comments = get_user_comments_by_task(user_id, 999)
    assert len(comments) == 0


def test_get_user_comments_by_task_user_not_found(seed_comments):
    """Test getting user comments by task for non-existent user."""
    with pytest.raises(ValueError, match=f"User {INVALID_USER_ID} not found"):
        get_user_comments_by_task(INVALID_USER_ID, VALID_TASK['id'])


def test_get_user_comments_by_task_task_not_found(seed_comments):
    """Test getting user comments by task for non-existent task."""
    user_id = VALID_USER['user_id']
    with pytest.raises(ValueError, match=f"Task {INVALID_TASK_ID} not found"):
        get_user_comments_by_task(user_id, INVALID_TASK_ID)


# -------- Edge Cases and Error Handling ------------------------------------------

def test_comment_handler_error_propagation(seed_task_and_users):
    """Test that handler properly propagates service errors."""
    # Test with invalid comment ID for update
    with pytest.raises(ValueError):
        update_comment(INVALID_COMMENT_ID, "Updated text")
    
    # Test with invalid comment ID for delete
    with pytest.raises(ValueError):
        delete_comment(INVALID_COMMENT_ID)


def test_multiple_users_comments_integration(seed_comments):
    """Test integration with multiple users making comments."""
    # Get comments for both users
    user1_comments = list_comments_by_user(VALID_USER['user_id'])
    user2_comments = list_comments_by_user(ANOTHER_USER['user_id'])
    
    assert len(user1_comments) == 2
    assert len(user2_comments) == 1
    
    # Verify counts
    assert get_user_comment_count(VALID_USER['user_id']) == 2
    assert get_user_comment_count(ANOTHER_USER['user_id']) == 1
    
    # Verify all comments include user data
    all_comments = user1_comments + user2_comments
    for comment in all_comments:
        assert 'user' in comment
        assert comment['user']['email'] is not None
        assert comment['user']['name'] is not None
