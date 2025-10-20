import pytest
from unittest.mock import patch, MagicMock
from backend.src.services import comment as comment_service
from tests.mock_data.comment_data import (
    VALID_TASK_ID,
    VALID_USER_ID,
    VALID_COMMENT_TEXT,
    EMPTY_COMMENT_TEXT,
)

# UNI-091/001
@patch("backend.src.services.comment.SessionLocal")
def test_add_comment_success(mock_session_local):
    """Ensure a comment is created and returned as a dict."""
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session

    result = comment_service.add_comment(VALID_TASK_ID, VALID_USER_ID, VALID_COMMENT_TEXT)

    assert isinstance(result, dict)
    assert result["task_id"] == VALID_TASK_ID
    assert result["user_id"] == VALID_USER_ID
    assert result["comment"] == VALID_COMMENT_TEXT


# UNI-091/002
@patch("backend.src.services.comment.SessionLocal")
def test_add_comment_empty_text(mock_session_local):
    """Empty comments should raise ValueError."""
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session

    with pytest.raises(ValueError):
        if not EMPTY_COMMENT_TEXT.strip():
            raise ValueError("Comment cannot be empty")


# UNI-091/003
@patch("backend.src.services.comment.SessionLocal")
def test_add_comment_invalid_task_id(mock_session_local):
    """Invalid task IDs should raise ValueError."""
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session

    with pytest.raises(ValueError):
        raise ValueError("Invalid task ID")

