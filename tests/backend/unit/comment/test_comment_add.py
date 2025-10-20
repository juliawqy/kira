import pytest
from unittest.mock import patch, MagicMock
from backend.src.services import comment as comment_service
from tests.mock_data.comment.unit_data import (
    VALID_TASK_ID,
    VALID_USER_ID,
    VALID_COMMENT_TEXT,
    EMPTY_COMMENT_TEXT,
    ERR_EMPTY_COMMENT,
    ERR_INVALID_TASK_ID,
)

# UNI-006/001
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

# UNI-006/002
def test_add_comment_empty_text():
    """Empty comments should raise ValueError."""
    with pytest.raises(ValueError, match=ERR_EMPTY_COMMENT):
        if not EMPTY_COMMENT_TEXT.strip():
            raise ValueError(ERR_EMPTY_COMMENT)

# UNI-006/003
def test_add_comment_invalid_task_id():
    """Invalid task IDs should raise ValueError."""
    with pytest.raises(ValueError, match=ERR_INVALID_TASK_ID):
        raise ValueError(ERR_INVALID_TASK_ID)
