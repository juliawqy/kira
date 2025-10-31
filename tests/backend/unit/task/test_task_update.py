# tests/backend/unit/task/test_task_update.py
from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch

from tests.mock_data.task.unit_data import (
    VALID_DEFAULT_TASK, 
    VALID_UPDATE_PAYLOAD,
    EMPTY_UPDATE_PAYLOAD,
    INVALID_UPDATE_PAYLOAD_WITH_ACTIVE,
    INVALID_UPDATE_PAYLOAD_WITH_STATUS,
    INVALID_UPDATE_PAYLOAD_WITH_STATUS_AND_ACTIVE,
    INVALID_TASK_ID_NONEXISTENT, 
    INVALID_PRIORITY_VALUES, 
    INVALID_PRIORITY_TYPES,
    EDGE_CASE_PRIORITY_BOUNDARY_LOW, 
    EDGE_CASE_PRIORITY_BOUNDARY_HIGH
)

pytestmark = pytest.mark.unit

# UNI-003/001
@patch("backend.src.services.task.SessionLocal")
def test_update_task_with_valid_payload(mock_session_local):
    """Update task using comprehensive update payload"""
    from backend.src.services import task as task_service
    
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    
    mock_task = MagicMock()
    mock_task.id = VALID_DEFAULT_TASK["id"]
    mock_task.title = VALID_DEFAULT_TASK["title"]
    mock_task.description = VALID_DEFAULT_TASK["description"]
    mock_task.priority = VALID_DEFAULT_TASK["priority"]
    mock_task.project_id = VALID_DEFAULT_TASK["project_id"]
    mock_task.active = VALID_DEFAULT_TASK["active"]
    mock_task.start_date = VALID_DEFAULT_TASK["start_date"]
    mock_task.deadline = VALID_DEFAULT_TASK["deadline"]
    
    mock_session.get.return_value = mock_task
    mock_session.flush.return_value = None
    
    result = task_service.update_task(
        task_id=VALID_DEFAULT_TASK["id"],
        **VALID_UPDATE_PAYLOAD
    )
    
    mock_session.get.assert_called_once_with(task_service.Task, VALID_DEFAULT_TASK["id"])
    mock_session.add.assert_called_once_with(mock_task)
    mock_session.flush.assert_called_once()

    assert mock_task.title == VALID_UPDATE_PAYLOAD["title"]
    assert mock_task.description == VALID_UPDATE_PAYLOAD["description"]
    assert mock_task.priority == VALID_UPDATE_PAYLOAD["priority"]
    assert mock_task.start_date == VALID_UPDATE_PAYLOAD["start_date"]
    assert mock_task.deadline == VALID_UPDATE_PAYLOAD["deadline"]
    assert result == mock_task

# UNI-003/002
@patch("backend.src.services.task.SessionLocal")
def test_update_task_no_fields_returns_task(mock_session_local):
    """Update task with empty/None fields returns existing task with original values unchanged"""
    from backend.src.services import task as task_service
    
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session

    mock_task = MagicMock()
    mock_task.id = VALID_DEFAULT_TASK["id"]
    mock_task.title = VALID_DEFAULT_TASK["title"]
    mock_task.description = VALID_DEFAULT_TASK["description"]
    mock_task.priority = VALID_DEFAULT_TASK["priority"]
    mock_task.project_id = VALID_DEFAULT_TASK["project_id"]
    mock_task.active = VALID_DEFAULT_TASK["active"]
    mock_task.start_date = VALID_DEFAULT_TASK["start_date"]
    mock_task.deadline = VALID_DEFAULT_TASK["deadline"]
    
    original_title = mock_task.title
    original_description = mock_task.description
    original_priority = mock_task.priority
    original_project_id = mock_task.project_id
    original_active = mock_task.active
    original_start_date = mock_task.start_date
    original_deadline = mock_task.deadline
    
    mock_session.get.return_value = mock_task
    mock_session.flush.return_value = None
    
    result = task_service.update_task(
        task_id=VALID_DEFAULT_TASK["id"],
        **EMPTY_UPDATE_PAYLOAD
    )
    
    mock_session.get.assert_called_once_with(task_service.Task, VALID_DEFAULT_TASK["id"])
    mock_session.add.assert_called_once_with(mock_task)
    mock_session.flush.assert_called_once()
    
    assert mock_task.title == original_title
    assert mock_task.description == original_description
    assert mock_task.priority == original_priority
    assert mock_task.project_id == original_project_id
    assert mock_task.active == original_active
    assert mock_task.start_date == original_start_date
    assert mock_task.deadline == original_deadline
    assert result == mock_task

# UNI-003/003
@patch("backend.src.services.task.SessionLocal")
def test_update_task_nonexistent_raises_error(mock_session_local):
    """Update nonexistent task raises ValueError"""
    from backend.src.services import task as task_service
    
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    
    mock_session.get.return_value = None
    
    with pytest.raises(ValueError) as exc:
        task_service.update_task(
            task_id=INVALID_TASK_ID_NONEXISTENT,
            **VALID_UPDATE_PAYLOAD
        )
    
    assert "Task not found" in str(exc.value)
    mock_session.get.assert_called_once_with(task_service.Task, INVALID_TASK_ID_NONEXISTENT)
    mock_session.add.assert_not_called()
    mock_session.flush.assert_not_called()

# UNI-003/004
@patch("backend.src.services.task.SessionLocal")
def test_update_task_priority_boundary_low(mock_session_local):
    """Update task with minimum valid priority (1)"""
    from backend.src.services import task as task_service
    
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session

    mock_task = MagicMock()
    mock_task.id = VALID_DEFAULT_TASK["id"]
    mock_task.priority = VALID_DEFAULT_TASK["priority"]
    
    mock_session.get.return_value = mock_task
    mock_session.flush.return_value = None
    
    result = task_service.update_task(
        task_id=VALID_DEFAULT_TASK["id"],
        **EDGE_CASE_PRIORITY_BOUNDARY_LOW
    )
    
    mock_session.get.assert_called_once_with(task_service.Task, VALID_DEFAULT_TASK["id"])
    mock_session.add.assert_called_once_with(mock_task)
    mock_session.flush.assert_called_once()
    
    assert mock_task.priority == EDGE_CASE_PRIORITY_BOUNDARY_LOW["priority"]
    assert result == mock_task

# UNI-003/005
@patch("backend.src.services.task.SessionLocal")
def test_update_task_priority_boundary_high(mock_session_local):
    """Update task with maximum valid priority (10)"""
    from backend.src.services import task as task_service
    
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session

    mock_task = MagicMock()
    mock_task.id = VALID_DEFAULT_TASK["id"]
    mock_task.priority = VALID_DEFAULT_TASK["priority"]
    
    mock_session.get.return_value = mock_task
    mock_session.flush.return_value = None
    
    result = task_service.update_task(
        task_id=VALID_DEFAULT_TASK["id"],
        **EDGE_CASE_PRIORITY_BOUNDARY_HIGH
    )
    
    mock_session.get.assert_called_once_with(task_service.Task, VALID_DEFAULT_TASK["id"])
    mock_session.add.assert_called_once_with(mock_task)
    mock_session.flush.assert_called_once()
    
    assert mock_task.priority == EDGE_CASE_PRIORITY_BOUNDARY_HIGH["priority"]
    assert result == mock_task

