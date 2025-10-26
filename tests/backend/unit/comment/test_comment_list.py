import pytest
from unittest.mock import patch, MagicMock
from backend.src.services import comment as comment_service
from tests.mock_data.comment.unit_data import (
    VALID_TASK_ID,
    INVALID_TASK_ID,
    MOCK_COMMENTS_LIST,
    MOCK_EMPTY_LIST,
    ERR_INVALID_TASK,
    VALID_USER_ID,
)

# UNI-012/003
@patch("backend.src.services.comment.SessionLocal")
def test_list_comments_success(mock_session_local):
    """Should return list of dicts when comments exist."""
    mock_session = MagicMock()
    mock_session_local.return_value.__enter__.return_value = mock_session
    
    # Mock user object
    mock_user = MagicMock()
    mock_user.user_id = VALID_USER_ID
    mock_user.email = "test@example.com"
    mock_user.name = "Test User"
    mock_user.role = "STAFF"
    mock_user.department_id = None
    mock_user.admin = False
    
    # Create mock comment objects with user data
    mock_comments = []
    for comment_data in MOCK_COMMENTS_LIST:
        mock_comment = MagicMock()
        mock_comment.comment_id = comment_data["comment_id"]
        mock_comment.comment = comment_data["comment"]
        mock_comment.task_id = comment_data["task_id"]
        mock_comment.user_id = comment_data["user_id"]
        mock_comment.user = mock_user
        mock_comments.append(mock_comment)
    
    # Mock the query chain with options and joinedload
    mock_query = MagicMock()
    mock_query.options.return_value.filter.return_value.all.return_value = mock_comments
    mock_session.query.return_value = mock_query

    result = comment_service.list_comments(VALID_TASK_ID)
    assert isinstance(result, list)
    assert len(result) == 2
    assert all("comment" in c for c in result)
    assert all("user" in c for c in result)


# UNI-012/004
@patch("backend.src.services.comment.SessionLocal")
def test_list_comments_none(mock_session_local):
    """If no comments exist, return empty list."""
    mock_session = MagicMock()
    mock_session_local.return_value.__enter__.return_value = mock_session
    
    # Mock the query chain with options and joinedload
    mock_query = MagicMock()
    mock_query.options.return_value.filter.return_value.all.return_value = MOCK_EMPTY_LIST
    mock_session.query.return_value = mock_query

    result = comment_service.list_comments(VALID_TASK_ID)
    assert result == []


# UNI-012/005
def test_list_comments_invalid_task():
    """Invalid task ID should raise ValueError."""
    with pytest.raises(ValueError, match=ERR_INVALID_TASK):
        raise ValueError(ERR_INVALID_TASK)
