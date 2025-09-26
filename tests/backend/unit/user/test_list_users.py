# tests/unit/services/test_list_users.py
from unittest.mock import patch, MagicMock
from tests.mock_data.user_data import VALID_USER_ADMIN, VALID_USER

@patch("backend.src.services.user.SessionLocal")
def test_list_users_empty(mock_session_local):
    from backend.src.services import user as user_service

    mock_session = MagicMock()
    mock_session_local.return_value = mock_session

    execute_result = MagicMock()
    execute_result.scalars.return_value.all.return_value = []
    mock_session.execute.return_value = execute_result

    res = user_service.list_users()
    assert isinstance(res, list)
    assert len(res) == 0

@patch("backend.src.services.user.SessionLocal")
def test_list_users_nonempty(mock_session_local):
    from backend.src.services import user as user_service

    mock_session = MagicMock()
    mock_session_local.return_value = mock_session

    # Create two MagicMock ORM-like users
    orm1 = MagicMock()
    orm1.email = VALID_USER_ADMIN["email"]
    orm2 = MagicMock()
    orm2.email = VALID_USER["email"]

    execute_result = MagicMock()
    execute_result.scalars.return_value.all.return_value = [orm1, orm2]
    mock_session.execute.return_value = execute_result

    res = user_service.list_users()
    assert len(res) == 2
    assert res[0].email == VALID_USER_ADMIN["email"]
    assert res[1].email == VALID_USER["email"]
