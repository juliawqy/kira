# tests/unit/services/test_update_user.py
import pytest
from unittest.mock import patch, MagicMock
from tests.mock_data.user.unit_data import VALID_USER_ADMIN, VALID_UPDATE_NAME, VALID_UPDATE_EMAIL, VALID_USER
from backend.src.enums.user_role import UserRole

# UNI-053/001
@patch("backend.src.services.user.SessionLocal")
def test_update_user_success_name_and_email(mock_session_local):
    from backend.src.services import user as user_service

    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session

    user_obj = MagicMock()
    user_obj.user_id = VALID_USER_ADMIN["user_id"]
    user_obj.name = VALID_USER_ADMIN["name"]
    user_obj.email = VALID_USER_ADMIN["email"]
    mock_session.get.return_value = user_obj

    execute_result = MagicMock()
    execute_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = execute_result

    updated = user_service.update_user(user_obj.user_id, **VALID_UPDATE_NAME)
    assert updated.name == VALID_UPDATE_NAME["name"]

    updated2 = user_service.update_user(user_obj.user_id, **VALID_UPDATE_EMAIL)
    assert updated2.email == VALID_UPDATE_EMAIL["email"]

# UNI-053/002
@patch("backend.src.services.user.SessionLocal")
def test_update_user_not_found(mock_session_local):
    from backend.src.services import user as user_service
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    mock_session.get.return_value = None

    res = user_service.update_user(9999, name="No One")
    assert res is None

# UNI-053/003
@patch("backend.src.services.user.SessionLocal")
def test_update_user_email_conflict(mock_session_local):
    from backend.src.services import user as user_service

    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session

    user_obj = MagicMock()
    user_obj.user_id = VALID_USER_ADMIN["user_id"]
    mock_session.get.return_value = user_obj

    execute_result = MagicMock()
    other_user = MagicMock()
    other_user.user_id = VALID_USER["user_id"]
    execute_result.scalar_one_or_none.return_value = other_user
    mock_session.execute.return_value = execute_result

    with pytest.raises(ValueError):
        user_service.update_user(user_obj.user_id, email=VALID_USER["email"])

# UNI-053/004
@patch("backend.src.services.user.SessionLocal")
def test_update_user_role_success(mock_session_local):
    """
    Ensure update_user updates the role when provided.
    """
    from backend.src.services import user as user_service

    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session

    user_obj = MagicMock()
    user_obj.user_id = VALID_USER_ADMIN["user_id"]
    user_obj.role = VALID_USER_ADMIN["role"]
    mock_session.get.return_value = user_obj
    updated = user_service.update_user(user_obj.user_id, role=UserRole.MANAGER)
    assert updated is not None
    assert updated.role == UserRole.MANAGER.value

# UNI-053/005
@patch("backend.src.services.user.SessionLocal")
def test_update_user_department_and_admin_success(mock_session_local):
    """
    Ensure update_user updates department_id and admin flag together.
    """
    from backend.src.services import user as user_service

    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session

    user_obj = MagicMock()
    user_obj.user_id = VALID_USER_ADMIN["user_id"]
    user_obj.department_id = None
    user_obj.admin = False
    mock_session.get.return_value = user_obj

    updated = user_service.update_user(user_obj.user_id, department_id=42, admin=True)
    assert updated is not None
    assert updated.department_id == 42
    assert updated.admin is True

# UNI-053/006
@patch("backend.src.services.user.SessionLocal")
def test_update_user_invalid_role_type(mock_session_local):
    from backend.src.services import user as user_service
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    mock_session.get.return_value = MagicMock(user_id=1, role=UserRole.STAFF.value)

    with pytest.raises(ValueError) as exc:
        user_service.update_user(1, role="manager")  # invalid string
    assert "role must be a valid UserRole" in str(exc.value)
