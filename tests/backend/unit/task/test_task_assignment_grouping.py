from __future__ import annotations

import types
import pytest
from unittest.mock import MagicMock, patch

from backend.src.handlers import task_assignment_handler as handler
from tests.mock_data.task.unit_data import (
    VALID_DEFAULT_TASK,
    VALID_TASK_EXPLICIT_PRIORITY,
    VALID_TASK_FULL,
    INACTIVE_TASK,
    INVALID_TASK_ID_NONEXISTENT,
    VALID_USER_ADMIN,
    VALID_USER,
    INVALID_USER_ID,
    VALID_USER_DIRECTOR,
    VALID_TEAM,
    VALID_SUBTEAM,
    VALID_DEPARTMENT
)


def make_user(role: str | None):
    return types.SimpleNamespace(role=role)

# ================================ list_tasks_by_manager Tests ================================

# UNI-028/001
@patch("backend.src.handlers.task_assignment_handler.user_service")
def test_manager_not_found_raises(mock_user_service):
    mock_user_service.get_user.return_value = None
    with pytest.raises(ValueError, match=r"Manager not found"):
        handler.list_tasks_by_manager(INVALID_USER_ID)


# UNI-028/002
@patch("backend.src.handlers.task_assignment_handler.user_service")
def test_user_not_manager_raises(mock_user_service):
    mock_user = MagicMock()
    mock_user.role = VALID_USER["role"]
    mock_user_service.get_user.return_value = mock_user

    with pytest.raises(ValueError, match=r"User is not a manager"):
        handler.list_tasks_by_manager(VALID_USER["user_id"])


# UNI-028/003
@patch("backend.src.handlers.task_assignment_handler.team_service")
@patch("backend.src.handlers.task_assignment_handler.user_service")
def test_no_teams_returns_empty(mock_user_service, mock_team_service):
    mock_user = MagicMock()
    mock_user.role = VALID_USER_ADMIN["role"]
    mock_user_service.get_user.return_value = mock_user
    mock_team_service.get_team_by_manager.return_value = []

    result = handler.list_tasks_by_manager(VALID_USER_ADMIN["user_id"])
    assert result == {}


# UNI-028/004
@patch("backend.src.handlers.task_assignment_handler.assignment_service")
@patch("backend.src.handlers.task_assignment_handler.team_service")
@patch("backend.src.handlers.task_assignment_handler.user_service")
def test_aggregates_tasks_by_team_and_subteam(mock_user_service, mock_team_service, mock_assignment_service):
    mock_user = MagicMock()
    mock_user.role = VALID_USER_ADMIN["role"]
    mock_user_service.get_user.return_value = mock_user

    teams = [VALID_TEAM]
    subteams = [VALID_SUBTEAM]
    mock_team_service.get_team_by_manager.return_value = teams

    mock_team_service.get_users_in_team.side_effect = (
        lambda tid: [{"user_id": VALID_USER_ADMIN["user_id"]}] if tid == VALID_TEAM["team_id"] else [{"user_id": VALID_USER["user_id"]}]
    )
    mock_team_service.get_subteam_by_team_number.side_effect = (
        lambda num: subteams if num == VALID_TEAM[f"{VALID_TEAM['team_number']}-{VALID_TEAM['team_name']}"] else []
    )

    user_tasks = {
        VALID_USER_ADMIN["user_id"]: [VALID_DEFAULT_TASK, VALID_TASK_EXPLICIT_PRIORITY],
        VALID_USER["user_id"]: [VALID_TASK_FULL, VALID_TASK_EXPLICIT_PRIORITY],
    }
    mock_assignment_service.list_tasks_for_user.side_effect = (
        lambda uid: user_tasks.get(uid, [])
    )

    result = handler.list_tasks_by_manager(VALID_USER_ADMIN["user_id"])
    assert set(result.keys()) == {VALID_TEAM["team_number"], VALID_SUBTEAM["team_number"]}
    assert result[(VALID_TEAM["team_number"], VALID_TEAM["team_name"])] == [VALID_DEFAULT_TASK, VALID_TASK_EXPLICIT_PRIORITY]
    assert result[(VALID_SUBTEAM["team_number"], VALID_SUBTEAM["team_name"])] == [VALID_TASK_FULL, VALID_TASK_EXPLICIT_PRIORITY]


# ================================ list_tasks_by_director Tests ================================

# UNI-028/005
@patch("backend.src.handlers.task_assignment_handler.user_service")
def test_director_not_found_raises(mock_user_service):
    mock_user_service.get_user.return_value = None
    with pytest.raises(ValueError, match=r"Director not found"):
        handler.list_tasks_by_director(VALID_USER_DIRECTOR["user_id"])


# UNI-028/006
@patch("backend.src.handlers.task_assignment_handler.user_service")
def test_user_not_director_raises(mock_user_service):
    mock_user = MagicMock()
    mock_user.role = VALID_USER_ADMIN["role"]
    mock_user_service.get_user.return_value = mock_user

    with pytest.raises(ValueError, match=r"User is not a director"):
        handler.list_tasks_by_director(VALID_USER_ADMIN["user_id"])


# UNI-028/007
@patch("backend.src.handlers.task_assignment_handler.department_service")
@patch("backend.src.handlers.task_assignment_handler.user_service")
def test_no_department_returns_empty(mock_user_service, mock_department_service):
    mock_user = MagicMock()
    mock_user.role = VALID_USER_DIRECTOR["role"]
    mock_user_service.get_user.return_value = mock_user
    mock_department_service.get_department_by_director.return_value = None

    result = handler.list_tasks_by_director(VALID_USER_DIRECTOR["user_id"])
    assert result == {}


# UNI-028/008
@patch("backend.src.handlers.task_assignment_handler.team_service")
@patch("backend.src.handlers.task_assignment_handler.department_service")
@patch("backend.src.handlers.task_assignment_handler.user_service")
def test_no_teams_returns_empty(mock_user_service, mock_department_service, mock_team_service):
    mock_user = MagicMock()
    mock_user.role = VALID_USER_DIRECTOR["role"]
    mock_user_service.get_user.return_value = mock_user
    mock_department_service.get_department_by_director.return_value = {
        "department_id": VALID_USER_DIRECTOR["department_id"]
    }
    mock_team_service.get_teams_by_department.return_value = []

    result = handler.list_tasks_by_director(VALID_USER_DIRECTOR["user_id"])
    assert result == {}


# UNI-028/009
@patch("backend.src.handlers.task_assignment_handler.assignment_service")
@patch("backend.src.handlers.task_assignment_handler.team_service")
@patch("backend.src.handlers.task_assignment_handler.department_service")
@patch("backend.src.handlers.task_assignment_handler.user_service")
def test_aggregates_tasks_by_team_and_subteam(mock_user_service, mock_department_service, mock_team_service, mock_assignment_service):
    mock_user = MagicMock()
    mock_user.role = VALID_USER_DIRECTOR["role"]
    mock_user_service.get_user.return_value = mock_user
    mock_department_service.get_department_by_director.return_value = {
        "department_id": VALID_USER_DIRECTOR["department_id"]
    }

    teams = [VALID_TEAM]
    subteams = [VALID_SUBTEAM]
    mock_team_service.get_teams_by_department.return_value = teams

    mock_team_service.get_users_in_team.side_effect = (
        lambda tid: [{"user_id": VALID_USER_ADMIN["user_id"]}] if tid == VALID_TEAM["team_id"] else [{"user_id": VALID_USER["user_id"]}]
    )
    mock_team_service.get_subteam_by_team_number.side_effect = (
        lambda num: subteams if num == VALID_TEAM["team_number"] else []
    )
    mock_department_service.get_department_by_id.return_value = {
        "department_name": VALID_DEPARTMENT["department_name"]
    }

    user_tasks = {
        VALID_USER_ADMIN["user_id"]: [VALID_DEFAULT_TASK, VALID_TASK_EXPLICIT_PRIORITY],
        VALID_USER["user_id"]: [VALID_TASK_FULL, VALID_TASK_EXPLICIT_PRIORITY],
    }
    mock_assignment_service.list_tasks_for_user.side_effect = (
        lambda uid: user_tasks.get(uid, [])
    )

    result = handler.list_tasks_by_director(VALID_USER_DIRECTOR["user_id"])
    assert set(result.keys()) == {VALID_TEAM["team_number"], VALID_SUBTEAM["team_number"]-VALID_DEPARTMENT["department_name"]}
    assert result[VALID_TEAM["team_number"]] == [VALID_DEFAULT_TASK, VALID_TASK_EXPLICIT_PRIORITY]
    assert result[VALID_SUBTEAM["team_number"]-VALID_DEPARTMENT["department_name"]] == [VALID_TASK_FULL, VALID_TASK_EXPLICIT_PRIORITY]