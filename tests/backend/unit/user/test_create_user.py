# tests/backend/unit/user/test_create_user.py
import pytest
from unittest.mock import patch, MagicMock
from tests.mock_data.user.unit_data import (
    VALID_CREATE_PAYLOAD_ADMIN,
    VALID_CREATE_PAYLOAD_USER,
    VALID_USER_ADMIN,
    INVALID_CREATE_SHORT_PASSWORD,
    INVALID_CREATE_NO_SPECIAL,
    INVALID_ADMIN_TYPE
)

# UNI-052/008
@patch("backend.src.services.user.SessionLocal")
@patch("backend.src.services.user._hash_password", return_value="hashed_pw")
def test_create_user_success(mock_hash, mock_session_local):
    from backend.src.services import user as user_service

    # Mock session context manager
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session

    # Mock query to check existing email
    mock_execute_result = MagicMock()
    mock_execute_result.scalar_one_or_none.return_value = None  # User does not exist
    mock_session.execute.return_value = mock_execute_result

    result = user_service.create_user(**VALID_CREATE_PAYLOAD_ADMIN)

    assert result.email == VALID_USER_ADMIN["email"]
    mock_hash.assert_called_with(VALID_CREATE_PAYLOAD_ADMIN["password"])
    mock_session.add.assert_called()
    mock_session.flush.assert_called()
    mock_session.refresh.assert_called_with(result)

# UNI-052/009
@patch("backend.src.services.user.SessionLocal")
def test_create_user_duplicate_email(mock_session_local):
    from backend.src.services import user as user_service

    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session

    execute_result = MagicMock()
    execute_result.scalar_one_or_none.return_value = MagicMock()
    mock_session.execute.return_value = execute_result

    with pytest.raises(ValueError) as exc:
        user_service.create_user(**VALID_CREATE_PAYLOAD_USER)
    assert "already exists" in str(exc.value)

# UNI-052/010
def test_create_user_password_validation_fail():
    from backend.src.services import user as user_service

    with pytest.raises(ValueError):
        user_service.create_user(**INVALID_CREATE_SHORT_PASSWORD)
    with pytest.raises(ValueError):
        user_service.create_user(**INVALID_CREATE_NO_SPECIAL)

# UNI-052/011
def test_create_user_invalid_role_type():
    from backend.src.services import user as user_service

    with pytest.raises(ValueError) as exc:
        user_service.create_user(
            name=VALID_CREATE_PAYLOAD_USER["name"],
            email=VALID_CREATE_PAYLOAD_USER["email"],
            role=INVALID_ADMIN_TYPE,  # invalid type, string instead of UserRole
            password=VALID_CREATE_PAYLOAD_USER["password"],
        )
    assert "role must be a valid UserRole" in str(exc.value)

# UNI-052/012
def test_create_user_missing_name():
    from backend.src.services import user as user_service

    with pytest.raises(TypeError):
        user_service.create_user(
            name=None,
            email=VALID_CREATE_PAYLOAD_USER["email"],
            role=VALID_CREATE_PAYLOAD_USER["role"],
            password=VALID_CREATE_PAYLOAD_USER["password"],
        )

# UNI-052/013
def test_create_user_missing_email():
    from backend.src.services import user as user_service

    with pytest.raises(TypeError):
        user_service.create_user(
            name=VALID_CREATE_PAYLOAD_USER["name"],
            email=None,
            role=VALID_CREATE_PAYLOAD_USER["role"],
            password=VALID_CREATE_PAYLOAD_USER["password"],
        )

# UNI-052/014
def test_create_user_non_admin():
    from backend.src.services import user as user_service
    # placeholder to fill in test for user creation with non admin account
    pass