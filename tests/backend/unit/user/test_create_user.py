import pytest
from unittest.mock import patch, MagicMock
from tests.mock_data.user.unit_data import (
    VALID_CREATE_PAYLOAD_ADMIN,
    VALID_CREATE_PAYLOAD_USER,
    VALID_USER_ADMIN,
    INVALID_CREATE_SHORT_PASSWORD,
    INVALID_CREATE_NO_SPECIAL,
    INVALID_CREATE_BAD_ROLE,
    INVALID_CREATE_NO_NAME,
    INVALID_CREATE_BAD_EMAIL,
    INVALID_CREATE_BAD_ADMIN,
    INVALID_CREATE_UNAUTHORISED
)

# UNI-052/001
@patch("backend.src.services.user.SessionLocal")
@patch("backend.src.services.user._hash_password", return_value="hashed_pw")
def test_create_user_success(mock_hash, mock_session_local):
    from backend.src.services import user as user_service

    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session

    mock_execute_result = MagicMock()
    mock_execute_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_execute_result

    result = user_service.create_user(**VALID_CREATE_PAYLOAD_ADMIN)

    assert result.email == VALID_USER_ADMIN["email"]
    mock_hash.assert_called_with(VALID_CREATE_PAYLOAD_ADMIN["password"])
    mock_session.add.assert_called()
    mock_session.flush.assert_called()
    mock_session.refresh.assert_called_with(result)

# UNI-052/002
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

# UNI-052/003
@patch("backend.src.services.user.SessionLocal")
def test_create_user_password_validation_fail(mock_session_local):
    from backend.src.services import user as user_service

    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session

    with pytest.raises(ValueError):
        user_service.create_user(**INVALID_CREATE_SHORT_PASSWORD)
    with pytest.raises(ValueError):
        user_service.create_user(**INVALID_CREATE_NO_SPECIAL)

# UNI-052/004
@patch("backend.src.services.user.SessionLocal")
def test_create_user_invalid_role_type(mock_session_local):
    from backend.src.services import user as user_service

    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session

    with pytest.raises(ValueError) as exc:
        user_service.create_user(**INVALID_CREATE_BAD_ROLE)
    assert "role must be a valid UserRole" in str(exc.value)

# UNI-052/005
@patch("backend.src.services.user.SessionLocal")
def test_create_user_missing_name(mock_session_local):
    from backend.src.services import user as user_service

    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    mock_session.execute.return_value.scalar_one_or_none.return_value = None

    with pytest.raises(TypeError):
        user_service.create_user(**INVALID_CREATE_NO_NAME)

# UNI-052/006
@patch("backend.src.services.user.SessionLocal")
def test_create_user_missing_email(mock_session_local):
    from backend.src.services import user as user_service

    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    mock_session.execute.return_value.scalar_one_or_none.return_value = None

    with pytest.raises(TypeError):
        user_service.create_user(**INVALID_CREATE_BAD_EMAIL)

# UNI-052/007
@patch("backend.src.services.user.SessionLocal")
def test_create_user_invalid_admin_type(mock_session_local):
    from backend.src.services import user as user_service

    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    mock_session.execute.return_value.scalar_one_or_none.return_value = None

    with pytest.raises(TypeError):
        user_service.create_user(**INVALID_CREATE_BAD_ADMIN)

# UNI-052/008
@patch("backend.src.services.user.SessionLocal")
def test_create_user_non_admin(mock_session_local):
    from backend.src.services import user as user_service

    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session

    # Simulate a non-admin caller attempting to create user
    with pytest.raises(PermissionError) as exc:
        user_service.create_user(**INVALID_CREATE_UNAUTHORISED)

    assert "Only admin users can create accounts" in str(exc.value)
