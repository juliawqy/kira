from unittest.mock import patch, MagicMock
from tests.mock_data.user.unit_data import VALID_USER_ADMIN, VALID_USER

# UNI-054/001
@patch("backend.src.services.user.SessionLocal")
def test_get_user_by_id_found(mock_session_local):
    from backend.src.services import user as user_service

    mock_session = MagicMock()
    mock_session_local.return_value.__enter__.return_value = mock_session

    orm_user = MagicMock()
    orm_user.email = VALID_USER_ADMIN["email"]
    mock_session.get.return_value = orm_user

    res = user_service.get_user(VALID_USER_ADMIN["user_id"])
    assert res is orm_user
    assert getattr(res, "email") == VALID_USER_ADMIN["email"]
    mock_session.get.assert_called_with(user_service.User, VALID_USER_ADMIN["user_id"])

# UNI-054/002
@patch("backend.src.services.user.SessionLocal")
def test_get_user_by_identifier_found(mock_session_local):
    from backend.src.services import user as user_service

    mock_session = MagicMock()
    mock_session_local.return_value.__enter__.return_value = mock_session

    execute_result = MagicMock()
    orm_user = MagicMock()
    orm_user.name = VALID_USER["name"]
    execute_result.scalar_one_or_none.return_value = orm_user
    mock_session.execute.return_value = execute_result

    res = user_service.get_user(VALID_USER["email"])
    assert res is orm_user
    assert getattr(res, "name") == VALID_USER["name"]
    mock_session.execute.assert_called()


# UNI-054/003
@patch("backend.src.services.user.SessionLocal")
def test_get_user_not_found(mock_session_local):
    from backend.src.services import user as user_service

    mock_session = MagicMock()
    mock_session_local.return_value.__enter__.return_value = mock_session

    execute_result = MagicMock()
    execute_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = execute_result

    res = user_service.get_user("nonexistent@example.com")
    assert res is None
    mock_session.execute.assert_called()
