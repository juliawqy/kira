# tests/unit/services/test_delete_user.py
from unittest.mock import patch, MagicMock
from tests.mock_data.user.unit_data import VALID_USER_ADMIN

@patch("backend.src.services.user.SessionLocal")
def test_delete_user_success(mock_session_local):
    from backend.src.services import user as user_service

    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session

    mock_user = MagicMock()
    mock_user.user_id = VALID_USER_ADMIN["user_id"]
    mock_session.get.return_value = mock_user

    ok = user_service.delete_user(mock_user.user_id)
    assert ok is True
    mock_session.delete.assert_called_with(mock_user)

@patch("backend.src.services.user.SessionLocal")
def test_delete_user_not_found(mock_session_local):
    from backend.src.services import user as user_service

    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    mock_session.get.return_value = None

    ok = user_service.delete_user(9999)
    assert ok is False
