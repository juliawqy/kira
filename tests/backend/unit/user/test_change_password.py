# tests/unit/services/test_change_password.py
import pytest
from unittest.mock import patch, MagicMock
from tests.mock_data.user.unit_data import VALID_USER_ADMIN, VALID_PASSWORD_CHANGE, INVALID_PASSWORD_CHANGE_WEAK

# UNI-052/001
@patch("backend.src.services.user.SessionLocal")
@patch("backend.src.services.user._verify_password", return_value=True)
@patch("backend.src.services.user._hash_password", return_value="new_hashed")
def test_change_password_success(mock_hash, mock_verify, mock_session_local):
    from backend.src.services import user as user_service

    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session

    mock_user = MagicMock()
    mock_user.user_id = VALID_USER_ADMIN["user_id"]
    mock_user.hashed_pw = "old_hashed"
    mock_session.get.return_value = mock_user

    ok = user_service.change_password(
        mock_user.user_id,
        VALID_PASSWORD_CHANGE["current_password"],
        VALID_PASSWORD_CHANGE["new_password"],
    )
    assert ok is True
    assert mock_user.hashed_pw == "new_hashed"
    mock_session.add.assert_called_with(mock_user)

# UNI-052/002
@patch("backend.src.services.user.SessionLocal")
def test_change_password_user_not_found(mock_session_local):
    from backend.src.services import user as user_service

    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    mock_session.get.return_value = None

    with pytest.raises(ValueError) as exc:
        user_service.change_password(9999, "x", "Y!longpass1")
    assert "User not found" in str(exc.value)

# UNI-052/003
@patch("backend.src.services.user.SessionLocal")
@patch("backend.src.services.user._verify_password", return_value=False)
def test_change_password_wrong_current(mock_verify, mock_session_local):
    from backend.src.services import user as user_service

    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    mock_user = MagicMock()
    mock_user.user_id = VALID_USER_ADMIN["user_id"]
    mock_user.hashed_pw = "old"
    mock_session.get.return_value = mock_user

    with pytest.raises(ValueError) as exc:
        user_service.change_password(mock_user.user_id, "incorrect", "New!Pass1")
    assert "Current password is incorrect" in str(exc.value)

# UNI-052/004
def test_change_password_weak_new_password_raises():
    from backend.src.services import user as user_service

    with patch("backend.src.services.user.SessionLocal") as mock_session_local:
        with pytest.raises(ValueError):
            user_service.change_password(1, VALID_USER_ADMIN["password"], INVALID_PASSWORD_CHANGE_WEAK["new_password"])
        assert not mock_session_local.begin.called
