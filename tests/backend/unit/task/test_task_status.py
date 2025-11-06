# tests/backend/unit/task/test_task_status.py
from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch

from tests.mock_data.task.unit_data import (
    VALID_DEFAULT_TASK,
    INVALID_TASK_ID_NONEXISTENT,
    INVALID_STATUSES
)
from backend.src.enums.task_status import TaskStatus

pytestmark = pytest.mark.unit

# UNI-022/001
@patch("backend.src.services.task.SessionLocal")
def test_set_task_status_to_do_success(mock_session_local):
    """Set task status to To-do successfully"""
    from backend.src.services import task as task_service
    
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    
    mock_task = MagicMock()
    mock_task.id = VALID_DEFAULT_TASK["id"]
    mock_task.status = TaskStatus.IN_PROGRESS.value
    
    mock_session.get.return_value = mock_task
    mock_session.flush.return_value = None
    
    result = task_service.set_task_status(
        task_id=VALID_DEFAULT_TASK["id"],
        new_status=TaskStatus.TO_DO.value
    )
    
    mock_session.get.assert_called_once_with(task_service.Task, VALID_DEFAULT_TASK["id"])
    mock_session.add.assert_called_once_with(mock_task)
    mock_session.flush.assert_called_once()
    
    assert mock_task.status == TaskStatus.TO_DO.value
    assert result == mock_task

# UNI-022/002
@patch("backend.src.services.task.SessionLocal")
def test_set_task_status_in_progress_success(mock_session_local):
    """Set task status to In-progress successfully"""
    from backend.src.services import task as task_service
    
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    
    mock_task = MagicMock()
    mock_task.id = VALID_DEFAULT_TASK["id"]
    mock_task.status = TaskStatus.TO_DO.value
    
    mock_session.get.return_value = mock_task
    mock_session.flush.return_value = None
    
    result = task_service.set_task_status(
        task_id=VALID_DEFAULT_TASK["id"],
        new_status=TaskStatus.IN_PROGRESS.value
    )
    
    mock_session.get.assert_called_once_with(task_service.Task, VALID_DEFAULT_TASK["id"])
    mock_session.add.assert_called_once_with(mock_task)
    mock_session.flush.assert_called_once()
    
    assert mock_task.status == TaskStatus.IN_PROGRESS.value
    assert result == mock_task

# UNI-022/003
@patch("backend.src.services.task.SessionLocal")
def test_set_task_status_completed_success(mock_session_local):
    """Set task status to Completed successfully"""
    from backend.src.services import task as task_service
    
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    
    mock_task = MagicMock()
    mock_task.id = VALID_DEFAULT_TASK["id"]
    mock_task.status = TaskStatus.IN_PROGRESS.value
    
    mock_session.get.return_value = mock_task
    mock_session.flush.return_value = None
    
    result = task_service.set_task_status(
        task_id=VALID_DEFAULT_TASK["id"],
        new_status=TaskStatus.COMPLETED.value
    )
    
    mock_session.get.assert_called_once_with(task_service.Task, VALID_DEFAULT_TASK["id"])
    assert mock_session.add.call_count == 2
    assert mock_session.flush.call_count == 2
    
    assert mock_task.status == TaskStatus.COMPLETED.value
    assert result == mock_task

# UNI-022/004
@patch("backend.src.services.task.SessionLocal")
def test_set_task_status_blocked_success(mock_session_local):
    """Set task status to Blocked successfully"""
    from backend.src.services import task as task_service
    
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    
    mock_task = MagicMock()
    mock_task.id = VALID_DEFAULT_TASK["id"]
    mock_task.status = TaskStatus.TO_DO.value
    
    mock_session.get.return_value = mock_task
    mock_session.flush.return_value = None
    
    result = task_service.set_task_status(
        task_id=VALID_DEFAULT_TASK["id"],
        new_status=TaskStatus.BLOCKED.value
    )
    
    mock_session.get.assert_called_once_with(task_service.Task, VALID_DEFAULT_TASK["id"])
    mock_session.add.assert_called_once_with(mock_task)
    mock_session.flush.assert_called_once()
    
    assert mock_task.status == TaskStatus.BLOCKED.value
    assert result == mock_task

# UNI-022/005
@patch("backend.src.services.task.SessionLocal")
def test_set_task_status_same_status_idempotent(mock_session_local):
    """Setting same status is idempotent and successful"""
    from backend.src.services import task as task_service
    
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    
    mock_task = MagicMock()
    mock_task.id = VALID_DEFAULT_TASK["id"]
    mock_task.status = TaskStatus.IN_PROGRESS.value
    
    mock_session.get.return_value = mock_task
    mock_session.flush.return_value = None
    
    result = task_service.set_task_status(
        task_id=VALID_DEFAULT_TASK["id"],
        new_status=TaskStatus.IN_PROGRESS.value
    )
    
    mock_session.get.assert_called_once_with(task_service.Task, VALID_DEFAULT_TASK["id"])
    mock_session.add.assert_called_once_with(mock_task)
    mock_session.flush.assert_called_once()
    
    assert mock_task.status == TaskStatus.IN_PROGRESS.value
    assert result == mock_task

