# tests/backend/unit/task/test_task_delete.py
import pytest
from unittest.mock import patch, MagicMock
from tests.mock_data.task.unit_data import (
    VALID_DEFAULT_TASK,
    INACTIVE_TASK,
    INVALID_TASK_ID_NONEXISTENT
)

pytestmark = pytest.mark.unit

# UNI-004/001
@patch("backend.src.services.task.SessionLocal")
def test_delete_task_sets_active_false(mock_session_local):
    """Delete task successfully sets active=False."""
    from backend.src.services import task as task_service

    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session

    mock_task = MagicMock()
    mock_task.id = VALID_DEFAULT_TASK["id"]
    mock_task.active = True
    mock_session.get.return_value = mock_task

    mock_query = MagicMock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query

    result = task_service.delete_task(VALID_DEFAULT_TASK["id"])

    mock_session.get.assert_called_once_with(task_service.Task, VALID_DEFAULT_TASK["id"])
    assert mock_task.active is False
 
    mock_session.add.assert_called_with(mock_task)
    mock_session.flush.assert_called_once()

    assert result == mock_task

# UNI-004/002
@patch("backend.src.services.task.SessionLocal")
def test_delete_task_returns_deleted_task_object(mock_session_local):
    """Delete task returns the updated task object."""
    from backend.src.services import task as task_service
    
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    
    # Mock existing active task
    mock_task = MagicMock()
    mock_task.id = VALID_DEFAULT_TASK["id"]
    mock_task.title = VALID_DEFAULT_TASK["title"]
    mock_task.active = True
    mock_session.get.return_value = mock_task
    
    # Mock query for ParentAssignment deletions
    mock_query = MagicMock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query

    result = task_service.delete_task(VALID_DEFAULT_TASK["id"])

    # Verify the same task object is returned
    assert result is mock_task
    assert result.id == VALID_DEFAULT_TASK["id"]
    assert result.title == VALID_DEFAULT_TASK["title"]
    assert result.active is False

# UNI-004/003
@patch("backend.src.services.task.SessionLocal")
def test_delete_nonexistent_task_raises_value_error(mock_session_local):
    """Delete non-existent task raises ValueError."""
    from backend.src.services import task as task_service
    
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session

    mock_session.get.return_value = None
    
    with pytest.raises(ValueError) as exc:
        task_service.delete_task(INVALID_TASK_ID_NONEXISTENT)

    assert "Task not found" in str(exc.value)
    mock_session.get.assert_called_once_with(task_service.Task, INVALID_TASK_ID_NONEXISTENT)

# UNI-004/004
@patch("backend.src.services.task.SessionLocal")
def test_delete_already_inactive_task_raises_value_error(mock_session_local):
    """Delete already inactive task raises ValueError."""
    from backend.src.services import task as task_service
    
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    
    # Mock existing inactive task
    mock_task = MagicMock()
    mock_task.id = INACTIVE_TASK["id"]
    mock_task.active = False
    mock_session.get.return_value = mock_task
    
    with pytest.raises(ValueError) as exc:
        task_service.delete_task(INACTIVE_TASK["id"])
    
    assert "Task not found" in str(exc.value)
    mock_session.get.assert_called_once_with(task_service.Task, INACTIVE_TASK["id"])