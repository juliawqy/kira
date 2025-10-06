import pytest
from unittest.mock import patch, MagicMock
from backend.src.services import team as team_service
from tests.mock_data.team_data import (
	MANAGER_USER,
	STAFF_USER,
	DIRECTOR_USER,
	NO_ROLE_USER,
	NOT_FOUND_ID,
)


def make_user(user_dict):
	return type("User", (), user_dict)

# UNI-062/001
@patch("backend.src.services.team.SessionLocal")
def test_assign_to_team_success_manager(mock_session_local):
	mock_session = MagicMock()
	mock_session_local.begin.return_value.__enter__.return_value = mock_session
	# mock existing team
	mock_team = MagicMock()
	mock_team.team_id = 1
	mock_session.get.return_value = mock_team

	user = make_user(MANAGER_USER)
	result = team_service.assign_to_team(1, 99, user)

	assert result["team_id"] == 1
	assert result["user_id"] == 99
	# result should contain the assignment's id/team_id/user_id
	assert "id" in result
	assert result["team_id"] == 1
	assert result["user_id"] == 99



# UNI-062/002
@patch("backend.src.services.team.SessionLocal")
def test_assign_to_team_success_director(mock_session_local):
	mock_session = MagicMock()
	mock_session_local.begin.return_value.__enter__.return_value = mock_session
	mock_team = MagicMock()
	mock_team.team_id = 2
	mock_session.get.return_value = mock_team

	user = make_user(DIRECTOR_USER)
	result = team_service.assign_to_team(2, 100, user)

	assert result["team_id"] == 2
	assert result["user_id"] == 100
	assert "id" in result
	assert result["team_id"] == 2
	assert result["user_id"] == 100


# UNI-062/003
@pytest.mark.parametrize("user_dict", [STAFF_USER, NO_ROLE_USER])
@patch("backend.src.services.team.SessionLocal")
def test_assign_to_team_unauthorized(mock_session_local, user_dict):
	mock_session = MagicMock()
	mock_session_local.begin.return_value.__enter__.return_value = mock_session
	user = make_user(user_dict)
	with pytest.raises(ValueError):
		team_service.assign_to_team(1, 50, user)

# UNI-062/004
@patch("backend.src.services.team.SessionLocal")
def test_assign_to_team_not_found(mock_session_local):
	mock_session = MagicMock()
	mock_session_local.begin.return_value.__enter__.return_value = mock_session
	mock_session.get.return_value = None
	user = make_user(MANAGER_USER)
	with pytest.raises(ValueError):
		team_service.assign_to_team(NOT_FOUND_ID, 55, user)


# UNI-062/004
@patch("backend.src.services.team.SessionLocal")
def test_assign_to_team_flush_failure_rolls_back_and_raises(mock_session_local):
	mock_session = MagicMock()
	mock_session_local.begin.return_value.__enter__.return_value = mock_session
	mock_team = MagicMock()
	mock_team.team_id = 3
	mock_session.get.return_value = mock_team
	# Simulate DB flush error (e.g., unique constraint)
	mock_session.flush.side_effect = Exception("duplicate key")

	user = make_user(MANAGER_USER)
	with pytest.raises(ValueError) as exc:
		team_service.assign_to_team(3, 77, user)

	assert "Failed to assign" in str(exc.value)
	mock_session.rollback.assert_called_once()


# UNI-062/005
@patch("backend.src.services.team.SessionLocal")
def test_assign_to_team_adds_assignment_to_session(mock_session_local):
	"""Verify that assign_to_team creates a TeamAssignment and adds it to the session."""
	mock_session = MagicMock()
	mock_session_local.begin.return_value.__enter__.return_value = mock_session
	mock_team = MagicMock()
	mock_team.team_id = 42
	mock_session.get.return_value = mock_team

	user = make_user(MANAGER_USER)
	result = team_service.assign_to_team(42, 999, user)

	# ensure session.add was called once with an object that has expected attributes
	assert mock_session.add.call_count == 1
	added_obj = mock_session.add.call_args[0][0]
	assert getattr(added_obj, "team_id", None) == 42
	assert getattr(added_obj, "user_id", None) == 999
	assert "id" in result
	assert result["team_id"] == 42
	assert result["user_id"] == 999


# UNI-062/006
@patch("backend.src.services.team.SessionLocal")
def test_assign_to_team_refresh_ignored_on_error(mock_session_local):
	"""If session.refresh raises an exception, assign_to_team should ignore it and still return the assignment info."""
	mock_session = MagicMock()
	mock_session_local.begin.return_value.__enter__.return_value = mock_session
	mock_team = MagicMock()
	mock_team.team_id = 77
	mock_session.get.return_value = mock_team

	# Make flush succeed but refresh raise
	mock_session.flush.return_value = None
	mock_session.refresh.side_effect = Exception("refresh failed")

	user = make_user(MANAGER_USER)
	result = team_service.assign_to_team(77, 444, user)

	assert result["team_id"] == 77
	assert result["user_id"] == 444
	assert "id" in result
	# rollback should not have been called for a refresh failure
	mock_session.rollback.assert_not_called()




