import pytest
from unittest.mock import patch, MagicMock
from backend.src.services import team as team_service
from tests.mock_data.team_data import VALID_TEAM_CREATE, MANAGER_USER, MEMBER_USER

def make_user(user_dict):
    return type("User", (), user_dict)

@patch("backend.src.services.team.SessionLocal")
def test_view_team_success(mock_session_local):
    mock_session = MagicMock()
    mock_session_local.return_value.__enter__.return_value = mock_session
    # Mock team object
    mock_team = MagicMock()
    mock_team.team_id = 1
    mock_team.team_name = VALID_TEAM_CREATE["team_name"]
    mock_team.manager_id = MANAGER_USER["user_id"]
    mock_session.get.return_value = mock_team
    user = make_user(MANAGER_USER)
    result = team_service.get_team_by_id(1, user)
    assert result["team_id"] == 1
    assert result["team_name"] == VALID_TEAM_CREATE["team_name"]
    assert result["manager_id"] == MANAGER_USER["user_id"]
    assert result["user_id"] == MANAGER_USER["user_id"]

@patch("backend.src.services.team.SessionLocal")
def test_view_team_not_found(mock_session_local):
    mock_session = MagicMock()
    mock_session_local.return_value.__enter__.return_value = mock_session
    mock_session.get.return_value = None
    user = make_user(MANAGER_USER)
    with pytest.raises(ValueError):
        team_service.get_team_by_id(999, user)
