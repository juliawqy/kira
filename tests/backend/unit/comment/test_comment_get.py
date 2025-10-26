import pytest
from unittest.mock import patch, MagicMock
from backend.src.services import comment as comment_service
from tests.mock_data.comment.unit_data import (
    VALID_TASK_ID,
    VALID_USER_ID,
    VALID_COMMENT_TEXT,
    INVALID_COMMENT_ID,
    ANOTHER_COMMENT_ID,
)

# UNI-012/001
@patch("backend.src.services.comment.SessionLocal")
def test_get_comment_success(mock_session_local):
    """Get comment should return correct dict when found."""
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

    mock_comment = MagicMock(
        comment_id=ANOTHER_COMMENT_ID,
        comment=VALID_COMMENT_TEXT,
        task_id=VALID_TASK_ID,
        user_id=VALID_USER_ID,
        user=mock_user,
    )
    
    # Mock the query chain with options and joinedload
    mock_query = MagicMock()
    mock_query.options.return_value.filter.return_value.first.return_value = mock_comment
    mock_session.query.return_value = mock_query

    result = comment_service.get_comment(ANOTHER_COMMENT_ID)
    assert isinstance(result, dict)
    assert result["comment"] == VALID_COMMENT_TEXT
    assert result["comment_id"] == ANOTHER_COMMENT_ID
    assert "user" in result
    assert result["user"]["user_id"] == VALID_USER_ID


# UNI-012/002
@patch("backend.src.services.comment.SessionLocal")
def test_get_comment_not_found(mock_session_local):
    """If comment does not exist, return None."""
    mock_session = MagicMock()
    mock_session_local.return_value.__enter__.return_value = mock_session
    
    # Mock the query chain with options and joinedload
    mock_query = MagicMock()
    mock_query.options.return_value.filter.return_value.first.return_value = None
    mock_session.query.return_value = mock_query

    result = comment_service.get_comment(INVALID_COMMENT_ID)
    assert result is None
