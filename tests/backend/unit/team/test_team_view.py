import pytest
from unittest.mock import patch, MagicMock
from backend.src.services import team as team_service
from tests.mock_data.team_data import VALID_TEAM_CREATE, MANAGER_USER, STAFF_USER, NOT_FOUND_ID

def make_user(user_dict):
    return type("User", (), user_dict)

# UNI-061/001
@patch("backend.src.services.team.SessionLocal")
def test_view_team_success(mock_session_local):
    mock_session = MagicMock()
    mock_session_local.return_value.__enter__.return_value = mock_session
    # Mock team object
    mock_team = MagicMock()
    mock_team.team_id = VALID_TEAM_CREATE["team_id"]
    mock_team.team_name = VALID_TEAM_CREATE["team_name"]
    mock_team.manager_id = VALID_TEAM_CREATE.get("manager_id", MANAGER_USER.get("user_id"))
    mock_team.department_id = VALID_TEAM_CREATE.get("department_id")
    mock_team.team_number = VALID_TEAM_CREATE.get("team_number")
    mock_session.get.return_value = mock_team
    result = team_service.get_team_by_id(VALID_TEAM_CREATE["team_id"])
    assert result["team_id"] == VALID_TEAM_CREATE["team_id"]
    assert result["team_name"] == VALID_TEAM_CREATE["team_name"]
    assert result["manager_id"] == VALID_TEAM_CREATE.get("manager_id", MANAGER_USER["user_id"])
    assert result["department_id"] == VALID_TEAM_CREATE.get("department_id")
    assert result["team_number"] == VALID_TEAM_CREATE.get("team_number")

# UNI-061/002
@patch("backend.src.services.team.SessionLocal")
def test_view_team_not_found(mock_session_local):
    mock_session = MagicMock()
    mock_session_local.return_value.__enter__.return_value = mock_session
    mock_session.get.return_value = None
    with pytest.raises(ValueError):
        team_service.get_team_by_id(NOT_FOUND_ID)


