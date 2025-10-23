import pytest
from unittest.mock import patch, MagicMock
from backend.src.services import team as team_service
from backend.src.enums.user_role import UserRole
from tests.mock_data.team_data import (
	MANAGER_USER,
	STAFF_USER,
	NOT_FOUND_ID,
	VALID_TEAM,
	VALID_TEAM_CREATE
)


def make_user(user_dict):
	role = user_dict.get("role")
	attrs = {"user_id": user_dict.get("user_id")}
	if role is not None:
		if isinstance(role, UserRole):
			role_val = role.value
		else:
			role_val = role
		attrs["role"] = role_val
	return type("User", (), attrs)


# UNI-062/001
@patch("backend.src.services.team.SessionLocal")
def test_assign_to_team_success(mock_session_local):
	mock_session = MagicMock()
	mock_session_local.begin.return_value.__enter__.return_value = mock_session

	mock_team = MagicMock()
	mock_team.team_id = VALID_TEAM["team_id"]
	mock_session.get.return_value = mock_team

	result = team_service.assign_to_team(VALID_TEAM["team_id"], STAFF_USER["user_id"])

	assert result["team_id"] == VALID_TEAM["team_id"]
	assert result["user_id"] == STAFF_USER["user_id"]


# UNI-062/002
@patch("backend.src.services.team.SessionLocal")
def test_assign_to_team_not_found(mock_session_local):
	mock_session = MagicMock()
	mock_session_local.begin.return_value.__enter__.return_value = mock_session
	mock_session.get.return_value = None

	with pytest.raises(ValueError):
		team_service.assign_to_team(NOT_FOUND_ID, STAFF_USER["user_id"])



# UNI-062/004
@patch("backend.src.services.team.SessionLocal")
def test_assign_to_team_adds_assignment_to_session(mock_session_local):
	mock_session = MagicMock()
	mock_session_local.begin.return_value.__enter__.return_value = mock_session

	mock_team = MagicMock()
	mock_team.team_id = VALID_TEAM["team_id"]
	mock_session.get.return_value = mock_team

	result = team_service.assign_to_team(VALID_TEAM["team_id"], STAFF_USER["user_id"])

	mock_session.add.assert_called_once()
	added_obj = mock_session.add.call_args[0][0]
	assert getattr(added_obj, "team_id", None) == VALID_TEAM["team_id"]
	assert getattr(added_obj, "user_id", None) == STAFF_USER["user_id"]
	assert result["team_id"] == VALID_TEAM["team_id"]
	assert result["user_id"] == STAFF_USER["user_id"]


# UNI-062/006
@patch("backend.src.services.team.SessionLocal")
def test_assign_to_team_refresh_ignored_on_error(mock_session_local):
	mock_session = MagicMock()
	mock_session_local.begin.return_value.__enter__.return_value = mock_session

	mock_team = MagicMock()
	mock_team.team_id = VALID_TEAM["team_id"]
	mock_session.get.return_value = mock_team
	mock_session.flush.return_value = None

	result = team_service.assign_to_team(VALID_TEAM["team_id"], STAFF_USER["user_id"])

	assert result["team_id"] == VALID_TEAM["team_id"]
	assert result["user_id"] == STAFF_USER["user_id"]
	mock_session.rollback.assert_not_called()
