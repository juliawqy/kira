import pytest
from unittest.mock import patch, MagicMock
from backend.src.services import comment as comment_service
from tests.mock_data.comment.unit_data import (
    VALID_TASK_ID,
    INVALID_TASK_ID,
    MOCK_COMMENTS_LIST,
    MOCK_EMPTY_LIST,
    ERR_INVALID_TASK,
)

# UNI-012/003
@patch("backend.src.services.comment.SessionLocal")
def test_list_comments_success(mock_session_local):
    """Should return list of dicts when comments exist."""
    mock_session = MagicMock()
    mock_session_local.return_value.__enter__.return_value = mock_session
    mock_session.query().filter().all.return_value = [
        MagicMock(**comment) for comment in MOCK_COMMENTS_LIST
    ]

    result = comment_service.list_comments(VALID_TASK_ID)
    assert isinstance(result, list)
    assert len(result) == 2
    assert all("comment" in c for c in result)


# UNI-012/004
@patch("backend.src.services.comment.SessionLocal")
def test_list_comments_none(mock_session_local):
    """If no comments exist, return empty list."""
    mock_session = MagicMock()
    mock_session_local.return_value.__enter__.return_value = mock_session
    mock_session.query().filter().all.return_value = MOCK_EMPTY_LIST

    result = comment_service.list_comments(VALID_TASK_ID)
    assert result == []


# UNI-012/005
def test_list_comments_invalid_task():
    """Invalid task ID should raise ValueError."""
    with pytest.raises(ValueError, match=ERR_INVALID_TASK):
        raise ValueError(ERR_INVALID_TASK)
