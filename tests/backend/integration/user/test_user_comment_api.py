# tests/backend/integration/user/test_user_comment_api.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

from backend.src.database.models.user import User
from backend.src.database.models.task import Task
from backend.src.database.models.project import Project
from backend.src.database.models.comment import Comment

from tests.mock_data.comment.integration_data import (
    VALID_USER,
    VALID_PROJECT,
    VALID_TASK,
    ANOTHER_USER,
    INVALID_USER_ID,
)

@pytest.fixture(autouse=True)
def override_clean_db(test_engine):
    """Override the clean_db fixture to not interfere with user-comment tests."""
    # Do nothing - this overrides the autouse clean_db fixture
    yield


def create_user_comment_test_data(test_engine):
    """Helper function to create test data for user comment API tests."""
    from sqlalchemy.orm import sessionmaker
    
    # Create a session that uses the same engine as the API
    TestingSessionLocal = sessionmaker(bind=test_engine, future=True)
    with TestingSessionLocal.begin() as session:
        # Clean up any existing data first
        session.execute(text("DELETE FROM comment"))
        session.execute(text("DELETE FROM task"))
        session.execute(text("DELETE FROM project"))
        session.execute(text("DELETE FROM user"))
        
        # Insert test data
        user1 = User(**VALID_USER)
        user2 = User(**ANOTHER_USER)
        session.add_all([user1, user2])
        session.flush()
        
        project = Project(**VALID_PROJECT)
        task = Task(**VALID_TASK)
        session.add_all([project, task])
        session.flush()
        
        # Create some comments
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
        session.add_all([comment1, comment2, comment3])
        # commit() is called automatically by the context manager

@pytest.fixture
def user_base_path() -> str:
    """Discover base path for user routes."""
    from backend.src.main import app
    for route in app.routes:
        try:
            if getattr(route, "name", None) == "get_user_comments" and "GET" in route.methods:
                return route.path.split("/{user_id}")[0].rstrip("/")
        except Exception:
            continue
    return "/kira/app/api/v1/user"


# INT-USER-COMMENT/001
def test_get_user_comments_success(client: TestClient, user_base_path, test_engine):
    """Test getting all comments made by a specific user via API."""
    create_user_comment_test_data(test_engine)
    
    user_id = VALID_USER['user_id']
    resp = client.get(f"{user_base_path}/{user_id}/comments")
    
    assert resp.status_code == 200
    comments = resp.json()
    
    # Should have 2 comments from user 1
    assert len(comments) == 2
    assert all(comment['user_id'] == user_id for comment in comments)
    
    # Check that user information is included
    for comment in comments:
        assert 'user' in comment
        assert comment['user']['user_id'] == user_id
        assert comment['user']['email'] == VALID_USER['email']
        assert comment['user']['name'] == VALID_USER['name']

# INT-USER-COMMENT/002
def test_get_user_comments_empty(client: TestClient, user_base_path, test_db_session):
    """Test getting comments for a user who has made no comments."""
    # Create a user with no comments
    user = User(
        user_id=999,
        email="nocomments@example.com",
        name="No Comments User",
        role="STAFF",
        admin=False,
        hashed_pw="dummy_hash"
    )
    test_db_session.add(user)
    test_db_session.commit()
    
    resp = client.get(f"{user_base_path}/999/comments")
    
    assert resp.status_code == 200
    comments = resp.json()
    assert len(comments) == 0

# INT-USER-COMMENT/003
def test_get_user_comments_user_not_found(client: TestClient, user_base_path):
    """Test getting comments for a non-existent user."""
    resp = client.get(f"{user_base_path}/{INVALID_USER_ID}/comments")
    
    assert resp.status_code == 404
    assert f"User {INVALID_USER_ID} not found" in resp.text

# INT-USER-COMMENT/004
def test_get_user_comment_count_success(client: TestClient, user_base_path, test_engine):
    """Test getting the count of comments made by a user via API."""
    create_user_comment_test_data(test_engine)
    
    user_id = VALID_USER['user_id']
    resp = client.get(f"{user_base_path}/{user_id}/comments/count")
    
    assert resp.status_code == 200
    count = resp.json()
    assert count == 2  # User 1 made 2 comments

# INT-USER-COMMENT/005
def test_get_user_comment_count_zero(client: TestClient, user_base_path, test_db_session):
    """Test getting comment count for a user with no comments."""
    # Create a user with no comments
    user = User(
        user_id=888,
        email="nocount@example.com",
        name="No Count User",
        role="STAFF",
        admin=False,
        hashed_pw="dummy_hash"
    )
    test_db_session.add(user)
    test_db_session.commit()
    
    resp = client.get(f"{user_base_path}/888/comments/count")
    
    assert resp.status_code == 200
    count = resp.json()
    assert count == 0

# INT-USER-COMMENT/006
def test_get_user_comment_count_user_not_found(client: TestClient, user_base_path):
    """Test getting comment count for a non-existent user."""
    resp = client.get(f"{user_base_path}/{INVALID_USER_ID}/comments/count")
    
    assert resp.status_code == 404
    assert f"User {INVALID_USER_ID} not found" in resp.text

# INT-USER-COMMENT/007
def test_user_comments_api_error_handling(client: TestClient, user_base_path):
    """Test error handling in user comments API endpoints."""
    # Test with invalid user ID format (should still work as it's treated as int)
    resp = client.get(f"{user_base_path}/99999/comments")
    assert resp.status_code == 404
    
    resp = client.get(f"{user_base_path}/99999/comments/count")
    assert resp.status_code == 404

# INT-USER-COMMENT/008
def test_user_comments_api_multiple_users(client: TestClient, user_base_path, test_engine):
    """Test user comments API with multiple users."""
    create_user_comment_test_data(test_engine)
    
    # Test user 1 comments
    resp1 = client.get(f"{user_base_path}/{VALID_USER['user_id']}/comments")
    assert resp1.status_code == 200
    comments1 = resp1.json()
    assert len(comments1) == 2
    
    # Test user 2 comments
    resp2 = client.get(f"{user_base_path}/{ANOTHER_USER['user_id']}/comments")
    assert resp2.status_code == 200
    comments2 = resp2.json()
    assert len(comments2) == 1
    
    # Test counts
    count1 = client.get(f"{user_base_path}/{VALID_USER['user_id']}/comments/count").json()
    count2 = client.get(f"{user_base_path}/{ANOTHER_USER['user_id']}/comments/count").json()
    
    assert count1 == 2
    assert count2 == 1
# INT-USER-COMMENT/009
def test_get_user_comments_valueerror_from_service(client: TestClient, user_base_path, test_engine):
    """Test that ValueError from comment service is properly handled."""
    create_user_comment_test_data(test_engine)
    
    # Mock comment service to raise ValueError
    from unittest.mock import patch
    with patch('backend.src.services.comment.list_comments_by_user') as mock_list_comments:
        mock_list_comments.side_effect = ValueError("Comment service error")
        
        user_id = VALID_USER['user_id']
        resp = client.get(f"{user_base_path}/{user_id}/comments")
        
        assert resp.status_code == 404
        assert "Comment service error" in resp.text

# INT-USER-COMMENT/010
def test_get_user_comment_count_valueerror_from_service(client: TestClient, user_base_path, test_engine):
    """Test that ValueError from comment service is properly handled."""
    create_user_comment_test_data(test_engine)
    
    # Mock comment service to raise ValueError
    from unittest.mock import patch
    with patch('backend.src.services.comment.get_user_comment_count') as mock_get_count:
        mock_get_count.side_effect = ValueError("Comment service error")
        
        user_id = VALID_USER['user_id']
        resp = client.get(f"{user_base_path}/{user_id}/comments/count")
        
        assert resp.status_code == 404
        assert "Comment service error" in resp.text
