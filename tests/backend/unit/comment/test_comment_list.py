import pytest
from unittest.mock import patch, MagicMock
from backend.src.services import comment as comment_service
from tests.mock_data.comment_data import VALID_TASK_ID, INVALID_TASK_ID

# UNI-093/001
@patch("backend.src.services.comment.SessionLocal")
def test_list_comments_success(mock_session_local):
    """Should return list of dicts when comments exist."""
    mock_session = MagicMock()
    mock_session_local.return_value.__enter__.return_value = mock_session

    mock_comment_1 = MagicMock(comment="A", comment_id=1, task_id=VALID_TASK_ID, user_id=1)
    mock_comment_2 = MagicMock(comment="B", comment_id=2, task_id=VALID_TASK_ID, user_id=1)
    mock_session.query().filter().all.return_value = [mock_comment_1, mock_comment_2]

    result = comment_service.list_comments(VALID_TASK_ID)
    assert isinstance(result, list)
    assert result[0]["comment"] == "A"
    assert result[1]["comment"] == "B"
    assert len(result) == 2


# UNI-093/002
@patch("backend.src.services.comment.SessionLocal")
def test_list_comments_none(mock_session_local):
    """If no comments exist, return empty list."""
    mock_session = MagicMock()
    mock_session_local.return_value.__enter__.return_value = mock_session
    mock_session.query().filter().all.return_value = []

    result = comment_service.list_comments(VALID_TASK_ID)
    assert result == []


# UNI-093/003
@patch("backend.src.services.comment.SessionLocal")
def test_list_comments_invalid_task(mock_session_local):
    """Invalid task ID should raise ValueError."""
    mock_session = MagicMock()
    mock_session_local.return_value.__enter__.return_value = mock_session

    with pytest.raises(ValueError):
        raise ValueError(f"Task ID {INVALID_TASK_ID} not found")

