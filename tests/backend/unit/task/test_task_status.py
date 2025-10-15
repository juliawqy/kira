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
    
    assert mock_task.status == TaskStatus.IN_PROGRESS.value
    assert result == mock_task

# UNI-022/006
@patch("backend.src.services.task.SessionLocal")
def test_set_task_status_nonexistent_task_raises_error(mock_session_local):
    """Set status for nonexistent task raises ValueError"""
    from backend.src.services import task as task_service
    
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    
    mock_session.get.return_value = None
    
    with pytest.raises(ValueError) as exc:
        task_service.set_task_status(
            task_id=INVALID_TASK_ID_NONEXISTENT,
            new_status=TaskStatus.IN_PROGRESS.value
        )
    
    assert "Task not found" in str(exc.value)
    mock_session.get.assert_called_once_with(task_service.Task, INVALID_TASK_ID_NONEXISTENT)

# UNI-022/007
@pytest.mark.parametrize("invalid_status", INVALID_STATUSES)
def test_set_task_status_invalid_status_raises_error(invalid_status):
    """Set task status with invalid status raises ValueError"""
    from backend.src.services import task as task_service
    
    with pytest.raises(ValueError) as exc:
        task_service.set_task_status(
            task_id=VALID_DEFAULT_TASK["id"],
            new_status=invalid_status
        )
    
    assert "Invalid status" in str(exc.value)
