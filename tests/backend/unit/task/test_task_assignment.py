# tests/backend/unit/task/test_task_assignment.py
from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.dialects import sqlite

from tests.mock_data.task.unit_data import (
    VALID_DEFAULT_TASK,
    INACTIVE_TASK,
    INVALID_TASK_ID_NONEXISTENT,
)
from tests.mock_data.user.unit_data import (
    VALID_USER_ADMIN,
    VALID_USER,
    INVALID_USER_ID,
)

pytestmark = pytest.mark.unit

# ================================ assign_users Tests ================================

# UNI-026/001
@patch("backend.src.services.task_assignment.SessionLocal")
def test_assign_users_success(mock_session_local):
    """Assign multiple users to task successfully"""
    from backend.src.services import task_assignment as ta_service
    
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    
    # Mock task exists and is active
    mock_task = MagicMock()
    mock_task.id = VALID_DEFAULT_TASK["id"]
    mock_task.active = True
    mock_session.get.return_value = mock_task
    
    # Mock users exist
    mock_user1 = MagicMock()
    mock_user1.user_id = VALID_USER_ADMIN["user_id"]
    mock_user2 = MagicMock()
    mock_user2.user_id = VALID_USER["user_id"]
    
    def mock_execute_side_effect(stmt):
        if "user_id" in str(stmt).lower() and "where" in str(stmt).lower():
            if "in" in str(stmt).lower():
                # First call: check if users exist
                mock_result = MagicMock()
                mock_result.scalars.return_value.all.return_value = [mock_user1, mock_user2]
                return mock_result
            else:
                # Second call: check existing assignments
                mock_result = MagicMock()
                mock_result.scalars.return_value.all.return_value = []
                return mock_result
    
    mock_session.execute.side_effect = mock_execute_side_effect
    
    user_ids = [VALID_USER_ADMIN["user_id"], VALID_USER["user_id"]]
    result = ta_service.assign_users(VALID_DEFAULT_TASK["id"], user_ids)
    
    assert result == 2
    assert mock_session.add.call_count == 2

# UNI-026/002
@patch("backend.src.services.task_assignment.SessionLocal")
def test_assign_users_single_user_success(mock_session_local):
    """Assign single user to task successfully using assign_users"""
    from backend.src.services import task_assignment as ta_service
    
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    
    # Mock task exists and is active
    mock_task = MagicMock()
    mock_task.id = VALID_DEFAULT_TASK["id"]
    mock_task.active = True
    mock_session.get.return_value = mock_task
    
    # Mock user exists
    mock_user = MagicMock()
    mock_user.user_id = VALID_USER_ADMIN["user_id"]
    
    def mock_execute_side_effect(stmt):
        if "user_id" in str(stmt).lower() and "where" in str(stmt).lower():
            if "in" in str(stmt).lower():
                # First call: check if user exists
                mock_result = MagicMock()
                mock_result.scalars.return_value.all.return_value = [mock_user]
                return mock_result
            else:
                # Second call: check existing assignments
                mock_result = MagicMock()
                mock_result.scalars.return_value.all.return_value = []
                return mock_result
    
    mock_session.execute.side_effect = mock_execute_side_effect
    
    result = ta_service.assign_users(VALID_DEFAULT_TASK["id"], [VALID_USER_ADMIN["user_id"]])
    
    assert result == 1
    assert mock_session.add.call_count == 1

# UNI-026/003
@patch("backend.src.services.task_assignment.SessionLocal")
def test_assign_users_partial_existing_assignments(mock_session_local):
    """Assign users with some already assigned returns count of new assignments"""
    from backend.src.services import task_assignment as ta_service
    
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    
    # Mock task exists and is active
    mock_task = MagicMock()
    mock_task.id = VALID_DEFAULT_TASK["id"]
    mock_task.active = True
    mock_session.get.return_value = mock_task
    
    # Mock users exist
    mock_user1 = MagicMock()
    mock_user1.user_id = VALID_USER_ADMIN["user_id"]
    mock_user2 = MagicMock()
    mock_user2.user_id = VALID_USER["user_id"]
    
    call_count = 0
    def mock_execute_side_effect(stmt):
        nonlocal call_count
        call_count += 1
        
        if call_count == 1:
            # First call: check if users exist
            mock_result = MagicMock()
            mock_result.scalars.return_value.all.return_value = [mock_user1, mock_user2]
            return mock_result
        elif call_count == 2:
            # Second call: check existing assignments - return one existing
            mock_result = MagicMock()
            mock_result.scalars.return_value.all.return_value = [VALID_USER_ADMIN["user_id"]]
            return mock_result
        else:
            # Handle any other queries
            mock_result = MagicMock()
            mock_result.scalars.return_value.all.return_value = []
            return mock_result
    
    mock_session.execute.side_effect = mock_execute_side_effect
    
    user_ids = [VALID_USER_ADMIN["user_id"], VALID_USER["user_id"]]
    result = ta_service.assign_users(VALID_DEFAULT_TASK["id"], user_ids)
    
    assert result == 1  # Only one new assignment created
    assert mock_session.add.call_count == 1

# UNI-026/004
@patch("backend.src.services.task_assignment.SessionLocal")
def test_assign_users_all_already_assigned_returns_zero(mock_session_local):
    """Assign users who are all already assigned returns 0 (idempotent)"""
    from backend.src.services import task_assignment as ta_service
    
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    
    # Mock task exists and is active
    mock_task = MagicMock()
    mock_task.id = VALID_DEFAULT_TASK["id"]
    mock_task.active = True
    mock_session.get.return_value = mock_task
    
    # Mock users exist
    mock_user1 = MagicMock()
    mock_user1.user_id = VALID_USER_ADMIN["user_id"]
    mock_user2 = MagicMock()
    mock_user2.user_id = VALID_USER["user_id"]
    
    call_count = 0
    def mock_execute_side_effect(stmt):
        nonlocal call_count
        call_count += 1
        
        if call_count == 1:
            # First call: check if users exist
            mock_result = MagicMock()
            mock_result.scalars.return_value.all.return_value = [mock_user1, mock_user2]
            return mock_result
        elif call_count == 2:
            # Second call: check existing assignments - return both existing
            mock_result = MagicMock()
            mock_result.scalars.return_value.all.return_value = [VALID_USER_ADMIN["user_id"], VALID_USER["user_id"]]
            return mock_result
        else:
            # Handle any other queries
            mock_result = MagicMock()
            mock_result.scalars.return_value.all.return_value = []
            return mock_result
    
    mock_session.execute.side_effect = mock_execute_side_effect
    
    user_ids = [VALID_USER_ADMIN["user_id"], VALID_USER["user_id"]]
    result = ta_service.assign_users(VALID_DEFAULT_TASK["id"], user_ids)
    
    assert result == 0  # No new assignments created
    mock_session.add.assert_not_called()

# UNI-026/005
@patch("backend.src.services.task_assignment.SessionLocal")
def test_assign_users_empty_list_returns_zero(mock_session_local):
    """Assign empty list of users returns 0"""
    from backend.src.services import task_assignment as ta_service
    
    result = ta_service.assign_users(VALID_DEFAULT_TASK["id"], [])
    
    assert result == 0

# UNI-026/006
@patch("backend.src.services.task_assignment.SessionLocal")
def test_assign_users_deduplicates_user_ids(mock_session_local):
    """Assign users with duplicate IDs deduplicates and processes correctly"""
    from backend.src.services import task_assignment as ta_service
    
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    
    # Mock task exists and is active
    mock_task = MagicMock()
    mock_task.id = VALID_DEFAULT_TASK["id"]
    mock_task.active = True
    mock_session.get.return_value = mock_task
    
    # Mock user exists
    mock_user = MagicMock()
    mock_user.user_id = VALID_USER_ADMIN["user_id"]
    
    def mock_execute_side_effect(stmt):
        if "user_id" in str(stmt).lower() and "where" in str(stmt).lower():
            if "in" in str(stmt).lower():
                # First call: check if users exist
                mock_result = MagicMock()
                mock_result.scalars.return_value.all.return_value = [mock_user]
                return mock_result
            else:
                # Second call: check existing assignments
                mock_result = MagicMock()
                mock_result.scalars.return_value.all.return_value = []
                return mock_result
    
    mock_session.execute.side_effect = mock_execute_side_effect
    
    # Pass duplicate user IDs
    user_ids = [VALID_USER_ADMIN["user_id"], VALID_USER_ADMIN["user_id"], VALID_USER_ADMIN["user_id"]]
    result = ta_service.assign_users(VALID_DEFAULT_TASK["id"], user_ids)
    
    assert result == 1  # Only one assignment created despite duplicates
    assert mock_session.add.call_count == 1

# UNI-026/007
@patch("backend.src.services.task_assignment.SessionLocal")
def test_assign_users_task_not_found_raises_error(mock_session_local):
    """Assign users to nonexistent task raises ValueError"""
    from backend.src.services import task_assignment as ta_service
    
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    
    mock_session.get.return_value = None
    
    with pytest.raises(ValueError, match=r"Task not found"):
        ta_service.assign_users(INVALID_TASK_ID_NONEXISTENT, [VALID_USER_ADMIN["user_id"]])

# UNI-026/008
@patch("backend.src.services.task_assignment.SessionLocal")
def test_assign_users_inactive_task_raises_error(mock_session_local):
    """Assign users to inactive task raises ValueError"""
    from backend.src.services import task_assignment as ta_service
    
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    
    mock_task = MagicMock()
    mock_task.id = INACTIVE_TASK["id"]
    mock_task.active = False
    mock_session.get.return_value = mock_task
    
    with pytest.raises(ValueError, match=r"inactive task"):
        ta_service.assign_users(INACTIVE_TASK["id"], [VALID_USER_ADMIN["user_id"]])

# UNI-026/009
@patch("backend.src.services.task_assignment.SessionLocal")
def test_assign_users_user_not_found_raises_error(mock_session_local):
    """Assign nonexistent user to task raises ValueError"""
    from backend.src.services import task_assignment as ta_service
    
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    
    # Mock task exists and is active
    mock_task = MagicMock()
    mock_task.id = VALID_DEFAULT_TASK["id"]
    mock_task.active = True
    mock_session.get.return_value = mock_task
    
    # Mock user doesn't exist
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_session.execute.return_value = mock_result
    
    with pytest.raises(ValueError, match=r"User.*not found"):
        ta_service.assign_users(VALID_DEFAULT_TASK["id"], [INVALID_USER_ID])

# ================================ unassign_users Tests ================================

# UNI-026/010
@patch("backend.src.services.task_assignment.SessionLocal")
def test_unassign_users_success(mock_session_local):
    """Remove multiple user assignments successfully"""
    from backend.src.services import task_assignment as ta_service
    
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    
    # Mock task exists and is active
    mock_task = MagicMock()
    mock_task.id = VALID_DEFAULT_TASK["id"]
    mock_task.active = True
    mock_session.get.return_value = mock_task
    
    # Mock users exist
    mock_user1 = MagicMock()
    mock_user1.user_id = VALID_USER_ADMIN["user_id"]
    mock_user2 = MagicMock()
    mock_user2.user_id = VALID_USER["user_id"]
    
    # Mock existing assignments
    mock_assignment1 = MagicMock()
    mock_assignment1.task_id = VALID_DEFAULT_TASK["id"]
    mock_assignment1.user_id = VALID_USER_ADMIN["user_id"]
    
    mock_assignment2 = MagicMock()
    mock_assignment2.task_id = VALID_DEFAULT_TASK["id"]
    mock_assignment2.user_id = VALID_USER["user_id"]
    
    def mock_execute_side_effect(stmt):
        if "user_id" in str(stmt).lower() and "where" in str(stmt).lower():
            if "in" in str(stmt).lower():
                # First call: check if users exist
                mock_result = MagicMock()
                mock_result.scalars.return_value.all.return_value = [mock_user1, mock_user2]
                return mock_result
            else:
                # Second call: get assignments to delete
                mock_result = MagicMock()
                mock_result.scalars.return_value.all.return_value = [mock_assignment1, mock_assignment2]
                return mock_result
    
    mock_session.execute.side_effect = mock_execute_side_effect
    
    user_ids = [VALID_USER_ADMIN["user_id"], VALID_USER["user_id"]]
    result = ta_service.unassign_users(VALID_DEFAULT_TASK["id"], user_ids)
    
    assert result == 2
    assert mock_session.delete.call_count == 2

# UNI-026/011
@patch("backend.src.services.task_assignment.SessionLocal")
def test_unassign_users_no_assignments_found(mock_session_local):
    """Remove users with no existing assignments returns 0"""
    from backend.src.services import task_assignment as ta_service
    
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    
    # Mock task exists and is active
    mock_task = MagicMock()
    mock_task.id = VALID_DEFAULT_TASK["id"]
    mock_task.active = True
    mock_session.get.return_value = mock_task
    
    # Mock users exist
    mock_user = MagicMock()
    mock_user.user_id = VALID_USER_ADMIN["user_id"]
    
    call_count = 0
    def mock_execute_side_effect(stmt):
        nonlocal call_count
        call_count += 1
        
        if call_count == 1:
            # First call: check if users exist
            mock_result = MagicMock()
            mock_result.scalars.return_value.all.return_value = [mock_user]
            return mock_result
        elif call_count == 2:
            # Second call: get assignments to delete - none found
            mock_result = MagicMock()
            mock_result.scalars.return_value.all.return_value = []
            return mock_result
        else:
            # Handle any other queries
            mock_result = MagicMock()
            mock_result.scalars.return_value.all.return_value = []
            return mock_result
    
    mock_session.execute.side_effect = mock_execute_side_effect
    
    result = ta_service.unassign_users(VALID_DEFAULT_TASK["id"], [VALID_USER_ADMIN["user_id"]])
    
    assert result == 0
    mock_session.delete.assert_not_called()

# UNI-026/012
@patch("backend.src.services.task_assignment.SessionLocal")
def test_unassign_users_empty_list_returns_zero(mock_session_local):
    """Remove empty list of users returns 0"""
    from backend.src.services import task_assignment as ta_service
    
    result = ta_service.unassign_users(VALID_DEFAULT_TASK["id"], [])
    
    assert result == 0

# UNI-026/013
@patch("backend.src.services.task_assignment.SessionLocal")
def test_unassign_users_task_not_found_raises_error(mock_session_local):
    """Remove users from nonexistent task raises ValueError"""
    from backend.src.services import task_assignment as ta_service
    
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    
    mock_session.get.return_value = None
    
    with pytest.raises(ValueError, match=r"Task not found"):
        ta_service.unassign_users(INVALID_TASK_ID_NONEXISTENT, [VALID_USER_ADMIN["user_id"]])

# UNI-026/014
@patch("backend.src.services.task_assignment.SessionLocal")
def test_unassign_users_user_not_found_raises_error(mock_session_local):
    """Remove nonexistent user from task raises ValueError"""
    from backend.src.services import task_assignment as ta_service
    
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    
    # Mock task exists and is active
    mock_task = MagicMock()
    mock_task.id = VALID_DEFAULT_TASK["id"]
    mock_task.active = True
    mock_session.get.return_value = mock_task
    
    # Mock user doesn't exist
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_session.execute.return_value = mock_result
    
    with pytest.raises(ValueError, match=r"User.*not found"):
        ta_service.unassign_users(VALID_DEFAULT_TASK["id"], [INVALID_USER_ID])

# ================================ clear_task_assignees Tests ================================

# UNI-026/015
@patch("backend.src.services.task_assignment.SessionLocal")
def test_clear_task_assignees_success(mock_session_local):
    """Clear all assignees from task successfully"""
    from backend.src.services import task_assignment as ta_service
    
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    
    # Mock task exists and is active
    mock_task = MagicMock()
    mock_task.id = VALID_DEFAULT_TASK["id"]
    mock_task.active = True
    mock_session.get.return_value = mock_task
    
    # Mock query and delete
    mock_query = MagicMock()
    mock_query.filter.return_value = mock_query
    mock_query.delete.return_value = 3  # 3 assignments deleted
    mock_session.query.return_value = mock_query
    
    result = ta_service.clear_task_assignees(VALID_DEFAULT_TASK["id"])
    
    assert result == 3
    mock_query.filter.assert_called_once()
    mock_query.delete.assert_called_once_with(synchronize_session=False)

# UNI-026/016
@patch("backend.src.services.task_assignment.SessionLocal")
def test_clear_task_assignees_no_assignments(mock_session_local):
    """Clear assignees from task with no assignments returns 0"""
    from backend.src.services import task_assignment as ta_service
    
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    
    # Mock task exists and is active
    mock_task = MagicMock()
    mock_task.id = VALID_DEFAULT_TASK["id"]
    mock_task.active = True
    mock_session.get.return_value = mock_task
    
    # Mock query and delete
    mock_query = MagicMock()
    mock_query.filter.return_value = mock_query
    mock_query.delete.return_value = 0  # No assignments deleted
    mock_session.query.return_value = mock_query
    
    result = ta_service.clear_task_assignees(VALID_DEFAULT_TASK["id"])
    
    assert result == 0

# UNI-026/017
@patch("backend.src.services.task_assignment.SessionLocal")
def test_clear_task_assignees_task_not_found_raises_error(mock_session_local):
    """Clear assignees from nonexistent task raises ValueError"""
    from backend.src.services import task_assignment as ta_service
    
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    
    mock_session.get.return_value = None
    
    with pytest.raises(ValueError, match=r"Task not found"):
        ta_service.clear_task_assignees(INVALID_TASK_ID_NONEXISTENT)

# ================================ list_assignees Tests ================================

# UNI-026/018
@patch("backend.src.services.task_assignment.SessionLocal")
def test_list_assignees_success(mock_session_local):
    """List assignees for task successfully"""
    from backend.src.services import task_assignment as ta_service
    
    mock_session = MagicMock()
    mock_session_local.return_value.__enter__.return_value = mock_session
    
    # Mock user IDs from assignments
    mock_result1 = MagicMock()
    mock_result1.scalars.return_value.all.return_value = [VALID_USER_ADMIN["user_id"], VALID_USER["user_id"]]
    
    # Mock users
    mock_user1 = MagicMock()
    mock_user1.user_id = VALID_USER_ADMIN["user_id"]
    mock_user1.name = VALID_USER_ADMIN["name"]
    mock_user1.email = VALID_USER_ADMIN["email"]
    mock_user1.role = VALID_USER_ADMIN["role"]
    mock_user1.department_id = VALID_USER_ADMIN["department_id"]
    mock_user1.admin = VALID_USER_ADMIN["admin"]
    
    mock_user2 = MagicMock()
    mock_user2.user_id = VALID_USER["user_id"]
    mock_user2.name = VALID_USER["name"]
    mock_user2.email = VALID_USER["email"]
    mock_user2.role = VALID_USER["role"]
    mock_user2.department_id = VALID_USER["department_id"]
    mock_user2.admin = VALID_USER["admin"]
    
    mock_result2 = MagicMock()
    mock_result2.scalars.return_value.all.return_value = [mock_user1, mock_user2]
    
    mock_session.execute.side_effect = [mock_result1, mock_result2]
    
    result = ta_service.list_assignees(VALID_DEFAULT_TASK["id"])
    
    assert len(result) == 2
    assert all(isinstance(user, ta_service.UserRead) for user in result)
    user_ids = [user.user_id for user in result]
    assert VALID_USER_ADMIN["user_id"] in user_ids
    assert VALID_USER["user_id"] in user_ids

# UNI-026/019
@patch("backend.src.services.task_assignment.SessionLocal")
def test_list_assignees_no_assignments(mock_session_local):
    """List assignees for task with no assignments returns empty list"""
    from backend.src.services import task_assignment as ta_service
    
    mock_session = MagicMock()
    mock_session_local.return_value.__enter__.return_value = mock_session
    
    # Mock no user IDs from assignments
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_session.execute.return_value = mock_result
    
    result = ta_service.list_assignees(VALID_DEFAULT_TASK["id"])
    
    assert result == []

# ================================ list_tasks_for_user Tests ================================

# UNI-026/020
@patch("backend.src.services.task_assignment.SessionLocal")
def test_list_tasks_for_user_success_active_only(mock_session_local):
    """List tasks for user with active_only=True successfully"""
    from backend.src.services import task_assignment as ta_service
    
    mock_session = MagicMock()
    mock_session_local.return_value.__enter__.return_value = mock_session
    
    # Mock tasks
    mock_task1 = MagicMock()
    mock_task1.id = VALID_DEFAULT_TASK["id"]
    mock_task1.title = VALID_DEFAULT_TASK["title"]
    mock_task1.active = True
    
    mock_task2 = MagicMock()
    mock_task2.id = INACTIVE_TASK["id"]
    mock_task2.title = INACTIVE_TASK["title"]
    mock_task2.active = False
    
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [mock_task1]  # Only active task
    mock_session.execute.return_value = mock_result
    
    result = ta_service.list_tasks_for_user(VALID_USER_ADMIN["user_id"], active_only=True)
    
    assert len(result) == 1
    assert result[0].id == VALID_DEFAULT_TASK["id"]
    assert result[0].active is True

# UNI-026/021
@patch("backend.src.services.task_assignment.SessionLocal")
def test_list_tasks_for_user_success_include_inactive(mock_session_local):
    """List tasks for user with active_only=False includes inactive tasks"""
    from backend.src.services import task_assignment as ta_service
    
    mock_session = MagicMock()
    mock_session_local.return_value.__enter__.return_value = mock_session
    
    # Mock tasks
    mock_task1 = MagicMock()
    mock_task1.id = VALID_DEFAULT_TASK["id"]
    mock_task1.title = VALID_DEFAULT_TASK["title"]
    mock_task1.active = True
    
    mock_task2 = MagicMock()
    mock_task2.id = INACTIVE_TASK["id"]
    mock_task2.title = INACTIVE_TASK["title"]
    mock_task2.active = False
    
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [mock_task1, mock_task2]
    mock_session.execute.return_value = mock_result
    
    result = ta_service.list_tasks_for_user(VALID_USER_ADMIN["user_id"], active_only=False)
    
    assert len(result) == 2
    task_ids = [task.id for task in result]
    assert VALID_DEFAULT_TASK["id"] in task_ids
    assert INACTIVE_TASK["id"] in task_ids

# UNI-026/022
@patch("backend.src.services.task_assignment.SessionLocal")
def test_list_tasks_for_user_no_tasks(mock_session_local):
    """List tasks for user with no assigned tasks returns empty list"""
    from backend.src.services import task_assignment as ta_service
    
    mock_session = MagicMock()
    mock_session_local.return_value.__enter__.return_value = mock_session
    
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_session.execute.return_value = mock_result
    
    result = ta_service.list_tasks_for_user(VALID_USER_ADMIN["user_id"])
    
    assert result == []

# ================================ Validation Function Tests ================================

# UNI-026/023
@patch("backend.src.services.task_assignment.SessionLocal")
def test_ensure_task_active_success(mock_session_local):
    """_ensure_task_active with valid active task returns task"""
    from backend.src.services import task_assignment as ta_service
    
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    
    mock_task = MagicMock()
    mock_task.id = VALID_DEFAULT_TASK["id"]
    mock_task.active = True
    mock_session.get.return_value = mock_task
    
    result = ta_service._ensure_task_active(mock_session, VALID_DEFAULT_TASK["id"])
    
    assert result == mock_task
    mock_session.get.assert_called_once_with(ta_service.Task, VALID_DEFAULT_TASK["id"])

# UNI-026/024
@patch("backend.src.services.task_assignment.SessionLocal")
def test_ensure_task_active_task_not_found_raises_error(mock_session_local):
    """_ensure_task_active with nonexistent task raises ValueError"""
    from backend.src.services import task_assignment as ta_service
    
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    
    mock_session.get.return_value = None
    
    with pytest.raises(ValueError, match=r"Task not found"):
        ta_service._ensure_task_active(mock_session, INVALID_TASK_ID_NONEXISTENT)

# UNI-026/025
@patch("backend.src.services.task_assignment.SessionLocal")
def test_ensure_task_active_inactive_task_raises_error(mock_session_local):
    """_ensure_task_active with inactive task raises ValueError"""
    from backend.src.services import task_assignment as ta_service
    
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    
    mock_task = MagicMock()
    mock_task.id = INACTIVE_TASK["id"]
    mock_task.active = False
    mock_session.get.return_value = mock_task
    
    with pytest.raises(ValueError, match=r"inactive task"):
        ta_service._ensure_task_active(mock_session, INACTIVE_TASK["id"])

# UNI-026/026
@patch("backend.src.services.task_assignment.SessionLocal")
def test_ensure_users_exist_success(mock_session_local):
    """_ensure_users_exist with valid users returns users"""
    from backend.src.services import task_assignment as ta_service
    
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    
    mock_user1 = MagicMock()
    mock_user1.user_id = VALID_USER_ADMIN["user_id"]
    mock_user2 = MagicMock()
    mock_user2.user_id = VALID_USER["user_id"]
    
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [mock_user1, mock_user2]
    mock_session.execute.return_value = mock_result
    
    user_ids = [VALID_USER_ADMIN["user_id"], VALID_USER["user_id"]]
    result = ta_service._ensure_users_exist(mock_session, user_ids)
    
    assert len(result) == 2
    assert result[0] == mock_user1
    assert result[1] == mock_user2

# UNI-026/027
@patch("backend.src.services.task_assignment.SessionLocal")
def test_ensure_users_exist_empty_list_returns_empty(mock_session_local):
    """_ensure_users_exist with empty list returns empty list"""
    from backend.src.services import task_assignment as ta_service
    
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    
    result = ta_service._ensure_users_exist(mock_session, [])
    
    assert result == []

# UNI-026/028
@patch("backend.src.services.task_assignment.SessionLocal")
def test_ensure_users_exist_missing_users_raises_error(mock_session_local):
    """_ensure_users_exist with missing users raises ValueError"""
    from backend.src.services import task_assignment as ta_service
    
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    
    mock_user = MagicMock()
    mock_user.user_id = VALID_USER_ADMIN["user_id"]
    
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [mock_user]
    mock_session.execute.return_value = mock_result
    
    user_ids = [VALID_USER_ADMIN["user_id"], INVALID_USER_ID]
    
    with pytest.raises(ValueError, match=r"User.*not found.*9999"):
        ta_service._ensure_users_exist(mock_session, user_ids)

# ================================ SQL Query Validation Tests ================================

# UNI-026/029
@patch("backend.src.services.task_assignment.SessionLocal")
def test_list_tasks_for_user_sql_query_validation(mock_session_local):
    """Verify SQL query structure for list_tasks_for_user operation"""
    from backend.src.services import task_assignment as ta_service
    
    mock_session = MagicMock()
    mock_session_local.return_value.__enter__.return_value = mock_session
    
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_session.execute.return_value = mock_result
    
    ta_service.list_tasks_for_user(VALID_USER_ADMIN["user_id"], active_only=True)
    
    mock_session.execute.assert_called_once()
    executed_stmt = mock_session.execute.call_args[0][0]
    compiled = executed_stmt.compile(dialect=sqlite.dialect(), compile_kwargs={"literal_binds": True})
    sql_text = str(compiled).lower()
    
    assert "task" in sql_text
    assert "task_assignment" in sql_text
    assert "join" in sql_text
    assert "active" in sql_text and ("true" in sql_text or "1" in sql_text)

# UNI-026/030
@patch("backend.src.services.task_assignment.SessionLocal")
def test_list_assignees_sql_query_validation(mock_session_local):
    """Verify SQL query structure for list_assignees operation"""
    from backend.src.services import task_assignment as ta_service
    
    mock_session = MagicMock()
    mock_session_local.return_value.__enter__.return_value = mock_session
    
    # Mock empty user IDs from assignments (so second query won't be called)
    mock_result1 = MagicMock()
    mock_result1.scalars.return_value.all.return_value = []
    
    mock_session.execute.return_value = mock_result1
    
    ta_service.list_assignees(VALID_DEFAULT_TASK["id"])
    
    assert mock_session.execute.call_count == 1  # Only one call since no user IDs found
    
    # Check first query (get user IDs)
    first_stmt = mock_session.execute.call_args[0][0]
    compiled1 = first_stmt.compile(dialect=sqlite.dialect(), compile_kwargs={"literal_binds": True})
    sql_text1 = str(compiled1).lower()
    
    assert "task_assignment" in sql_text1
    assert "user_id" in sql_text1
    assert "task_id" in sql_text1