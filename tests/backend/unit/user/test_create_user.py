# tests/backend/unit/user/test_create_user.py
import pytest
from unittest.mock import patch, MagicMock
from tests.mock_data.user_data import (
    VALID_CREATE_PAYLOAD_ADMIN,
    VALID_CREATE_PAYLOAD_USER,
    VALID_USER_ADMIN,
    INVALID_CREATE_SHORT_PASSWORD,
    INVALID_CREATE_NO_SPECIAL,
)

# --------------------------
# Success case
# --------------------------
@patch("backend.src.services.user.SessionLocal")
@patch("backend.src.services.user._hash_password", return_value="hashed_pw")
def test_create_user_success(mock_hash, mock_session_local):
    from backend.src.services import user as user_service

    # Mock session context manager
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session

    # **Mock query to check existing email**
    mock_execute_result = MagicMock()
    mock_execute_result.scalar_one_or_none.return_value = None  # <-- User does not exist
    mock_session.execute.return_value = mock_execute_result

    # Let User constructor run normally, don't patch it entirely
    result = user_service.create_user(**VALID_CREATE_PAYLOAD_ADMIN)

    assert result.email == VALID_USER_ADMIN["email"]
    mock_hash.assert_called_with(VALID_CREATE_PAYLOAD_ADMIN["password"])
    mock_session.add.assert_called()
    mock_session.flush.assert_called()
    mock_session.refresh.assert_called_with(result)



# --------------------------
# Duplicate email raises ValueError
# --------------------------
@patch("backend.src.services.user.SessionLocal")
def test_create_user_duplicate_email_raises(mock_session_local):
    from backend.src.services import user as user_service

    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session

    # simulate select(...) returns existing user
    execute_result = MagicMock()
    execute_result.scalar_one_or_none.return_value = MagicMock()
    mock_session.execute.return_value = execute_result

    with pytest.raises(ValueError) as exc:
        user_service.create_user(**VALID_CREATE_PAYLOAD_USER)
    assert "already exists" in str(exc.value)


# --------------------------
# Password validation fails locally (before DB)
# --------------------------
def test_create_user_password_validation_fail_local():
    from backend.src.services import user as user_service

    with pytest.raises(ValueError):
        user_service.create_user(**INVALID_CREATE_SHORT_PASSWORD)
    with pytest.raises(ValueError):
        user_service.create_user(**INVALID_CREATE_NO_SPECIAL)
