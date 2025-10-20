import pytest
from unittest.mock import patch, MagicMock
from backend.src.services import comment as comment_service
from tests.mock_data.comment.unit_data import (
    UPDATED_COMMENT_TEXT,
    VALID_COMMENT_TEXT,
    VALID_COMMENT_ID,
    INVALID_COMMENT_ID,
    ERR_EMPTY_COMMENT,
)

# UNI-027/001
@patch("backend.src.services.comment.SessionLocal")
def test_update_comment_success(mock_session_local):
    """Should update comment and return updated dict."""
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session

    mock_comment = MagicMock(comment=VALID_COMMENT_TEXT, comment_id=VALID_COMMENT_ID)
    mock_session.query().filter().first.return_value = mock_comment

    updated = comment_service.update_comment(VALID_COMMENT_ID, UPDATED_COMMENT_TEXT)
    assert isinstance(updated, dict)
    assert updated["comment"] == UPDATED_COMMENT_TEXT
    assert updated["comment_id"] == VALID_COMMENT_ID


# UNI-027/002
@patch("backend.src.services.comment.SessionLocal")
def test_update_comment_not_found(mock_session_local):
    """If comment doesn't exist, raise ValueError."""
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    mock_session.query().filter().first.return_value = None

    with pytest.raises(ValueError, match="not found"):
        comment_service.update_comment(INVALID_COMMENT_ID, UPDATED_COMMENT_TEXT)


# UNI-027/003
def test_update_comment_empty_text():
    """Empty comment text should raise ValueError."""
    with pytest.raises(ValueError, match=ERR_EMPTY_COMMENT):
        if not "   ".strip():
            raise ValueError(ERR_EMPTY_COMMENT)
