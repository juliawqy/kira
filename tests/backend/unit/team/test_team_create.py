import pytest
from unittest.mock import patch, MagicMock
from backend.src.services import team as team_service
from tests.mock_data.team_data import (
    VALID_TEAM_CREATE,
    MANAGER_USER,
    MEMBER_USER,
    INVALID_TEAM_EMPTY,
    INVALID_TEAM_WHITESPACE,
)

@patch("backend.src.services.team.SessionLocal")
def test_create_team_success(mock_session_local):
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    user = type("User", (), MANAGER_USER)
    team = team_service.create_team(VALID_TEAM_CREATE["team_name"], user)
    assert team["team_name"] == VALID_TEAM_CREATE["team_name"]
    assert team["manager_id"] == MANAGER_USER["user_id"]

@patch("backend.src.services.team.SessionLocal")
def test_create_team_non_manager(mock_session_local):
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    user = type("User", (), MEMBER_USER)
    with pytest.raises(ValueError):
        team_service.create_team(VALID_TEAM_CREATE["team_name"], user)

@pytest.mark.parametrize("invalid_team", [INVALID_TEAM_EMPTY, INVALID_TEAM_WHITESPACE])
@patch("backend.src.services.team.SessionLocal")
def test_create_team_invalid_name(mock_session_local, invalid_team):
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    user = type("User", (), MANAGER_USER)
    with pytest.raises(ValueError):
        team_service.create_team(invalid_team["team_name"], user)


