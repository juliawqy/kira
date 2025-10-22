import pytest
from unittest.mock import patch, MagicMock
from backend.src.services import team as team_service
from tests.mock_data.team_data import (
    VALID_TEAM_CREATE,
    MANAGER_USER,
    STAFF_USER,
)

# UNI-058/001
@patch("backend.src.services.team.SessionLocal")
def test_create_team_success(mock_session_local):
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session

    team = team_service.create_team(
        VALID_TEAM_CREATE["team_name"],
        MANAGER_USER["user_id"],
        department_id=VALID_TEAM_CREATE["department_id"],
        team_number=VALID_TEAM_CREATE["team_number"],
    )
    assert team["team_name"] == VALID_TEAM_CREATE["team_name"]
    assert team["manager_id"] == MANAGER_USER["user_id"]
    assert team["department_id"] == VALID_TEAM_CREATE["department_id"]
    assert team["team_number"] == VALID_TEAM_CREATE["team_number"]





