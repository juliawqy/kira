# tests/unit/services/test_update_user.py
import pytest
from unittest.mock import patch, MagicMock
from tests.mock_data.user_data import VALID_USER_ADMIN, VALID_UPDATE_NAME, VALID_UPDATE_EMAIL, VALID_USER_EMP

@patch("backend.src.services.user.SessionLocal")
def test_update_user_success_name_and_email(mock_session_local):
    from backend.src.services import user as user_service

    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session

    # existing user returned by session.get
    user_obj = MagicMock()
    user_obj.user_id = VALID_USER_ADMIN["user_id"]
    user_obj.name = VALID_USER_ADMIN["name"]
    user_obj.email = VALID_USER_ADMIN["email"]
    mock_session.get.return_value = user_obj

    # no conflict when checking new email
    execute_result = MagicMock()
    execute_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = execute_result

    updated = user_service.update_user(user_obj.user_id, **VALID_UPDATE_NAME)
    assert updated.name == VALID_UPDATE_NAME["name"]

    # change email
    updated2 = user_service.update_user(user_obj.user_id, **VALID_UPDATE_EMAIL)
    assert updated2.email == VALID_UPDATE_EMAIL["email"]

@patch("backend.src.services.user.SessionLocal")
def test_update_user_not_found(mock_session_local):
    from backend.src.services import user as user_service
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    mock_session.get.return_value = None

    res = user_service.update_user(9999, name="No One")
    assert res is None

@patch("backend.src.services.user.SessionLocal")
def test_update_user_email_conflict_raises(mock_session_local):
    from backend.src.services import user as user_service

    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session

    # existing user to update
    user_obj = MagicMock()
    user_obj.user_id = VALID_USER_ADMIN["user_id"]
    mock_session.get.return_value = user_obj

    # simulate another user with the desired email exists
    execute_result = MagicMock()
    other_user = MagicMock()
    other_user.user_id = VALID_USER_EMP["user_id"]
    execute_result.scalar_one_or_none.return_value = other_user
    mock_session.execute.return_value = execute_result

    with pytest.raises(ValueError):
        user_service.update_user(user_obj.user_id, email=VALID_USER_EMP["email"])
