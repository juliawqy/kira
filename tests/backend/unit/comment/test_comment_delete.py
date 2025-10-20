import pytest
from unittest.mock import patch, MagicMock
from backend.src.services import comment as comment_service
from tests.mock_data.comment.unit_data import (
    VALID_COMMENT_ID,
    INVALID_COMMENT_ID,
)

# UNI-005/001
@patch("backend.src.services.comment.SessionLocal")
def test_delete_comment_success(mock_session_local):
    """Successfully deletes an existing comment."""
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session

    mock_comment = MagicMock(comment_id=VALID_COMMENT_ID)
    mock_session.query().filter().first.return_value = mock_comment

    result = comment_service.delete_comment(VALID_COMMENT_ID)
    assert result is True


# UNI-005/002
@patch("backend.src.services.comment.SessionLocal")
def test_delete_comment_not_found(mock_session_local):
    """Deleting a missing comment should raise ValueError."""
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    mock_session.query().filter().first.return_value = None

    with pytest.raises(ValueError, match="not found"):
        comment_service.delete_comment(INVALID_COMMENT_ID)


# UNI-005/003
@patch("backend.src.services.comment.SessionLocal")
def test_delete_comment_db_error(mock_session_local):
    """Simulate database error on delete operation."""
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    mock_session.query().filter().first.side_effect = Exception("DB error")

    with pytest.raises(Exception, match="DB error"):
        comment_service.delete_comment(VALID_COMMENT_ID)
