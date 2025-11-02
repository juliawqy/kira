# tests/unit/services/test_change_password.py
import pytest
from unittest.mock import patch, MagicMock
from tests.mock_data.user.unit_data import (
    VALID_USER_ADMIN, 
    VALID_PASSWORD_CHANGE, 
    INVALID_PASSWORD_CHANGE_WEAK, 
    INVALID_USER_ID, 
    INVALID_PASSWORD_CHANGE_WRONG_CURRENT,
    INVALID_PASSWORD_TYPE,
    INVALID_PASSWORD_TYPE,
)

OLD_HASHED = "old_hashed"
NEW_HASHED = "new_hashed"

# UNI-053/004
@patch("backend.src.services.user.SessionLocal")
@patch("backend.src.services.user._verify_password", return_value=True)
@patch("backend.src.services.user._hash_password", return_value=NEW_HASHED)
def test_change_password_success(mock_hash, mock_verify, mock_session_local):
    from backend.src.services import user as user_service

    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session

    mock_user = MagicMock()
    mock_user.user_id = VALID_USER_ADMIN["user_id"]
    mock_user.hashed_pw = OLD_HASHED
    mock_session.get.return_value = mock_user

    ok = user_service.change_password(
        mock_user.user_id,
        VALID_PASSWORD_CHANGE["current_password"],
        VALID_PASSWORD_CHANGE["new_password"],
    )
    assert ok is True
    assert mock_user.hashed_pw == NEW_HASHED
    mock_session.add.assert_called_with(mock_user)

# UNI-053/005
@patch("backend.src.services.user.SessionLocal")
@patch("backend.src.services.user._verify_password", return_value=False)
def test_change_password_wrong_current(mock_verify, mock_session_local):
    from backend.src.services import user as user_service

    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    mock_user = MagicMock()
    mock_user.user_id = VALID_USER_ADMIN["user_id"]
    mock_user.hashed_pw = OLD_HASHED
    mock_session.get.return_value = mock_user

    with pytest.raises(ValueError) as exc:
        user_service.change_password(mock_user.user_id, INVALID_PASSWORD_CHANGE_WRONG_CURRENT["current_password"], INVALID_PASSWORD_CHANGE_WRONG_CURRENT["new_password"])
    assert "Current password is incorrect" in str(exc.value)

# UNI-053/006
def test_change_password_weak_new_password_raises():
    from backend.src.services import user as user_service

    with patch("backend.src.services.user.SessionLocal") as mock_session_local:
        with pytest.raises(ValueError):
            user_service.change_password(VALID_USER_ADMIN["user_id"], VALID_USER_ADMIN["password"], INVALID_PASSWORD_CHANGE_WEAK["new_password"])
        assert not mock_session_local.begin.called

# UNI-053/007
def test_hash_and_verify_normal_password():
    """
    Sanity check: hash a normal password and verify it.
    """
    from backend.src.services import user as user_service
    password = VALID_PASSWORD_CHANGE["new_password"]
    hashed = user_service._hash_password(password)
    
    assert hashed, "_hash_password returned empty"
    assert user_service._verify_password(password, hashed) is True
    assert user_service._verify_password(INVALID_PASSWORD_CHANGE_WRONG_CURRENT["current_password"], hashed) is False

# UNI-053/008
def test_verify_with_invalid_inputs():
    """
    _verify_password should safely return False for invalid types.
    """
    from backend.src.services import user as user_service
    hashed = user_service._hash_password(VALID_PASSWORD_CHANGE["new_password"])
    
    assert user_service._verify_password(None, hashed) is False
    assert user_service._verify_password(VALID_PASSWORD_CHANGE["new_password"], None) is False
    assert user_service._verify_password(None, None) is False

# UNI-053/009
def test_hash_password_type_error():
    """
    _hash_password should raise TypeError for non-string input.
    """
    from backend.src.services import user as user_service
    with pytest.raises(TypeError):
        user_service._hash_password(None)
    with pytest.raises(TypeError):
        user_service._hash_password(INVALID_PASSWORD_TYPE)
