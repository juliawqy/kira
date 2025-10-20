import pytest
from unittest.mock import patch, MagicMock
from backend.src.services import comment as comment_service
from tests.mock_data.comment_data import INVALID_COMMENT_ID

# UNI-095/001
@patch("backend.src.services.comment.SessionLocal")
def test_delete_comment_success(mock_session_local):
    """Successfully deletes an existing comment."""
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session

    mock_comment = MagicMock(comment_id=1)
    mock_session.query().filter().first.return_value = mock_comment

    result = comment_service.delete_comment(1)
    assert result is True


# UNI-095/002
@patch("backend.src.services.comment.SessionLocal")
def test_delete_comment_not_found(mock_session_local):
    """Deleting a missing comment should raise ValueError."""
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    mock_session.query().filter().first.return_value = None

    with pytest.raises(ValueError) as e:
        comment_service.delete_comment(INVALID_COMMENT_ID)
    assert "not found" in str(e.value).lower()


# UNI-095/003
@patch("backend.src.services.comment.SessionLocal")
def test_delete_comment_db_error(mock_session_local):
    """Simulate database error on delete operation."""
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    mock_session.query().filter().first.side_effect = Exception("DB error")

    with pytest.raises(Exception) as e:
        comment_service.delete_comment(1)
    assert "db" in str(e.value).lower()

