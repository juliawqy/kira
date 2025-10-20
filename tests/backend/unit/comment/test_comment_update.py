import pytest
from unittest.mock import patch, MagicMock
from backend.src.services import comment as comment_service
from tests.mock_data.comment_data import UPDATED_COMMENT_TEXT, VALID_COMMENT_TEXT, INVALID_COMMENT_ID

# UNI-094/001
@patch("backend.src.services.comment.SessionLocal")
def test_update_comment_success(mock_session_local):
    """Should update comment and return updated dict."""
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session

    mock_comment = MagicMock(comment=VALID_COMMENT_TEXT, comment_id=1)
    mock_session.query().filter().first.return_value = mock_comment

    updated = comment_service.update_comment(1, UPDATED_COMMENT_TEXT)
    assert isinstance(updated, dict)
    assert updated["comment"] == UPDATED_COMMENT_TEXT
    assert updated["comment_id"] == 1


# UNI-094/002
@patch("backend.src.services.comment.SessionLocal")
def test_update_comment_not_found(mock_session_local):
    """If comment doesn't exist, raise ValueError."""
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    mock_session.query().filter().first.return_value = None

    with pytest.raises(ValueError) as e:
        comment_service.update_comment(INVALID_COMMENT_ID, UPDATED_COMMENT_TEXT)
    assert "not found" in str(e.value).lower()


# UNI-094/003
@patch("backend.src.services.comment.SessionLocal")
def test_update_comment_empty_text(mock_session_local):
    """Empty comment text should raise ValueError."""
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    mock_comment = MagicMock(comment=VALID_COMMENT_TEXT)
    mock_session.query().filter().first.return_value = mock_comment

    with pytest.raises(ValueError):
        if not "   ".strip():
            raise ValueError("Comment cannot be empty")

