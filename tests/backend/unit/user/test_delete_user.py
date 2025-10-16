# tests/unit/services/test_delete_user.py
from unittest.mock import patch, MagicMock
import pytest
from tests.mock_data.user.unit_data import (
    VALID_USER_ADMIN,
    INVALID_DELETE_PAYLOAD_NONEXISTENT_USER,
    VALID_DELETE_PAYLOAD,
    INVALID_DELETE_PAYLOAD_NOT_ADMIN
)

# UNI-055/001
@patch("backend.src.services.user.SessionLocal")
def test_delete_user_success(mock_session_local):
    from backend.src.services import user as user_service

    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session

    mock_user = MagicMock()
    mock_user.user_id = VALID_USER_ADMIN["user_id"]
    mock_session.get.return_value = mock_user

    ok = user_service.delete_user(**VALID_DELETE_PAYLOAD)
    assert ok is True
    mock_session.delete.assert_called_with(mock_user)

# UNI-055/002
@patch("backend.src.services.user.SessionLocal")
def test_delete_user_not_found(mock_session_local):
    from backend.src.services import user as user_service

    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    mock_session.get.return_value = None

    ok = user_service.delete_user(**INVALID_DELETE_PAYLOAD_NONEXISTENT_USER)
    assert ok is False

# UNI-055/003
@patch("backend.src.services.user.SessionLocal")
def test_delete_user_not_admin_raises_permission_error(mock_session_local):
    from backend.src.services import user as user_service

    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session

    with pytest.raises(PermissionError) as exc:
        user_service.delete_user(**INVALID_DELETE_PAYLOAD_NOT_ADMIN)
    assert "Only admin users can delete accounts" in str(exc.value)
