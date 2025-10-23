import pytest
from unittest.mock import patch, MagicMock
from backend.src.services import team as team_service
from tests.mock_data.team_data import (
    VALID_TEAM_CREATE,
    VALID_TEAM
)

# UNI-058/001
@patch("backend.src.services.team.SessionLocal")
def test_create_team_success(mock_session_local):
    from backend.src.services import team as team_service

    mock_session = MagicMock()
    mock_session_local.return_value.__enter__.return_value = mock_session

    mock_team = MagicMock()
    mock_team.team_id = 1
    mock_team.team_name = VALID_TEAM["team_name"]
    mock_team.manager_id = VALID_TEAM["manager_id"]
    mock_team.department_id = VALID_TEAM["department_id"]
    mock_team.team_number = VALID_TEAM["team_number"]

    with patch("backend.src.services.team.Team", return_value=mock_team) as mock_team_constructor:
        result = team_service.create_team(
            VALID_TEAM_CREATE["team_name"],
            VALID_TEAM_CREATE["manager_id"],
            department_id=VALID_TEAM_CREATE["department_id"],
            prefix=str(VALID_TEAM_CREATE["department_id"]),
        )

    mock_team_constructor.assert_called_once_with(
        team_name=VALID_TEAM_CREATE["team_name"],
        manager_id=VALID_TEAM_CREATE["manager_id"],
        department_id=VALID_TEAM_CREATE["department_id"],
        team_number=str(VALID_TEAM_CREATE["department_id"]),
    )

    mock_session.add.assert_called_once_with(mock_team)

    assert result["team_name"] == VALID_TEAM["team_name"]
    assert result["manager_id"] == VALID_TEAM["manager_id"]
    assert result["department_id"] == VALID_TEAM["department_id"]
    assert result["team_number"] == VALID_TEAM["team_number"]
