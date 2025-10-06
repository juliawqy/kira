import pytest
from unittest.mock import patch, MagicMock
from backend.src.services import team as team_service
from backend.src.enums.user_role import UserRole
from tests.mock_data.team_data import (
	MANAGER_USER,
	STAFF_USER,
	DIRECTOR_USER,
	NO_ROLE_USER,
	NOT_FOUND_ID,
	ASSIGNEE_ID_123,
	ASSIGNEE_ID_222,
	ASSIGNEE_ID_55,
	ASSIGNEE_ID_999,
	TEAM_ID_1,
	TEAM_ID_2,
	TEAM_ID_3,
	TEAM_ID_42,
	TEAM_ID_77,
)



def make_user(user_dict):
	"""Return a lightweight user object. Normalize the role into a UserRole enum when possible."""
	role = user_dict.get("role")
	attrs = {"user_id": user_dict.get("user_id")}
	if role is not None:
		if isinstance(role, str):
			try:
				role_val = UserRole(role)
			except Exception:
				role_val = role
		else:
			role_val = role
		attrs["role"] = role_val
	return type("User", (), attrs)



# UNI-062/001
@patch("backend.src.services.team.SessionLocal")
def test_assign_to_team_success_manager(mock_session_local):
	mock_session = MagicMock()
	mock_session_local.begin.return_value.__enter__.return_value = mock_session
	# mock existing team
	mock_team = MagicMock()
	mock_team.team_id = TEAM_ID_1
	mock_session.get.return_value = mock_team

	user = make_user(MANAGER_USER)
	result = team_service.assign_to_team(TEAM_ID_1, ASSIGNEE_ID_123, user)

	assert result["team_id"] == TEAM_ID_1
	assert result["user_id"] == ASSIGNEE_ID_123
	# result should contain the assignment's id/team_id/user_id
	assert "id" in result
	assert result["team_id"] == TEAM_ID_1
	assert result["user_id"] == ASSIGNEE_ID_123



# UNI-062/002
@patch("backend.src.services.team.SessionLocal")
def test_assign_to_team_success_director(mock_session_local):
	mock_session = MagicMock()
	mock_session_local.begin.return_value.__enter__.return_value = mock_session
	mock_team = MagicMock()
	mock_team.team_id = TEAM_ID_2
	mock_session.get.return_value = mock_team

	user = make_user(DIRECTOR_USER)
	result = team_service.assign_to_team(TEAM_ID_2, ASSIGNEE_ID_222, user)

	assert result["team_id"] == TEAM_ID_2
	assert "id" in result
	assert result["team_id"] == TEAM_ID_2
	assert result["user_id"] == ASSIGNEE_ID_222


# UNI-062/003
@pytest.mark.parametrize("user_dict", [STAFF_USER, NO_ROLE_USER])
@patch("backend.src.services.team.SessionLocal")
def test_assign_to_team_unauthorized(mock_session_local, user_dict):
	mock_session = MagicMock()
	mock_session_local.begin.return_value.__enter__.return_value = mock_session
	user = make_user(user_dict)
	with pytest.raises(ValueError):
		team_service.assign_to_team(TEAM_ID_1, ASSIGNEE_ID_55, user)

# UNI-062/004
@patch("backend.src.services.team.SessionLocal")
def test_assign_to_team_not_found(mock_session_local):
	mock_session = MagicMock()
	mock_session_local.begin.return_value.__enter__.return_value = mock_session
	mock_session.get.return_value = None
	user = make_user(MANAGER_USER)
	with pytest.raises(ValueError):
		team_service.assign_to_team(NOT_FOUND_ID, ASSIGNEE_ID_55, user)


# UNI-062/004
@patch("backend.src.services.team.SessionLocal")
def test_assign_to_team_flush_failure_rolls_back_and_raises(mock_session_local):
	mock_session = MagicMock()
	mock_session_local.begin.return_value.__enter__.return_value = mock_session
	mock_team = MagicMock()
	mock_team.team_id = TEAM_ID_3
	mock_session.get.return_value = mock_team
	# Simulate DB flush error (e.g., unique constraint)
	mock_session.flush.side_effect = Exception("duplicate key")

	user = make_user(MANAGER_USER)
	with pytest.raises(ValueError) as exc:
		team_service.assign_to_team(TEAM_ID_3, ASSIGNEE_ID_55, user)

	assert "Failed to assign" in str(exc.value)
	mock_session.rollback.assert_called_once()


# UNI-062/005
@patch("backend.src.services.team.SessionLocal")
def test_assign_to_team_adds_assignment_to_session(mock_session_local):
	"""Verify that assign_to_team creates a TeamAssignment and adds it to the session."""
	mock_session = MagicMock()
	mock_session_local.begin.return_value.__enter__.return_value = mock_session
	mock_team = MagicMock()
	mock_team.team_id = TEAM_ID_42
	mock_session.get.return_value = mock_team

	user = make_user(MANAGER_USER)
	result = team_service.assign_to_team(TEAM_ID_42, ASSIGNEE_ID_999, user)

	# ensure session.add was called once with an object that has expected attributes
	assert mock_session.add.call_count == 1
	added_obj = mock_session.add.call_args[0][0]
	assert getattr(added_obj, "team_id", None) == TEAM_ID_42
	assert getattr(added_obj, "user_id", None) == ASSIGNEE_ID_999
	assert "id" in result
	assert result["team_id"] == TEAM_ID_42
	assert result["user_id"] == ASSIGNEE_ID_999


# UNI-062/006
@patch("backend.src.services.team.SessionLocal")
def test_assign_to_team_refresh_ignored_on_error(mock_session_local):
	"""If session.refresh raises an exception, assign_to_team should ignore it and still return the assignment info."""
	mock_session = MagicMock()
	mock_session_local.begin.return_value.__enter__.return_value = mock_session
	mock_team = MagicMock()
	mock_team.team_id = TEAM_ID_77
	mock_session.get.return_value = mock_team

	# Make flush succeed but refresh raise
	mock_session.flush.return_value = None
	mock_session.refresh.side_effect = Exception("refresh failed")

	user = make_user(MANAGER_USER)
	result = team_service.assign_to_team(TEAM_ID_77, ASSIGNEE_ID_123, user)

	assert result["team_id"] == TEAM_ID_77
	assert result["user_id"] == ASSIGNEE_ID_123
	assert "id" in result
	# rollback should not have been called for a refresh failure
	mock_session.rollback.assert_not_called()




