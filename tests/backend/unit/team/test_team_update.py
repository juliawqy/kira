import pytest
from unittest.mock import patch, MagicMock
from backend.src.services import team as team_service
from tests.mock_data.team_data import MANAGER_USER, MEMBER_USER

def make_user(user_dict):
    return type("User", (), user_dict)

@patch("backend.src.services.team.SessionLocal")
def test_update_team_name_success(mock_session_local):
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    # Mock team object
    mock_team = MagicMock()
    mock_team.team_id = 1
    mock_team.manager_id = MANAGER_USER["user_id"]
    mock_session.get.return_value = mock_team
    user = make_user(MANAGER_USER)
    new_name = "New Team Name"
    result = team_service.update_team_name(1, new_name, user)
    assert result.team_name == new_name
    mock_session.add.assert_called_once_with(mock_team)

@patch("backend.src.services.team.SessionLocal")
def test_update_team_name_not_found(mock_session_local):
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    mock_session.get.return_value = None
    user = make_user(MANAGER_USER)
    with pytest.raises(ValueError):
        team_service.update_team_name(999, "New Name", user)

@patch("backend.src.services.team.SessionLocal")
def test_update_team_name_not_manager(mock_session_local):
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    # Mock team object
    mock_team = MagicMock()
    mock_team.team_id = 1
    mock_team.manager_id = MANAGER_USER["user_id"]
    mock_session.get.return_value = mock_team
    user = make_user(MEMBER_USER)
    with pytest.raises(PermissionError):
        team_service.update_team_name(1, "New Name", user)

@patch("backend.src.services.team.SessionLocal")
def test_update_team_name_invalid_name(mock_session_local):
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    # Mock team object
    mock_team = MagicMock()
    mock_team.team_id = 1
    mock_team.manager_id = MANAGER_USER["user_id"]
    mock_session.get.return_value = mock_team
    user = make_user(MANAGER_USER)
    with pytest.raises(ValueError):
        team_service.update_team_name(1, "   ", user)
