import pytest
from unittest.mock import patch, MagicMock
from tests.mock_data.task_data import VALID_TASK_1, VALID_TASK_ID, INVALID_TASK_ID

@patch("backend.src.services.task.SessionLocal")
def test_update_task_invalid_status_raises(mock_session_local, mock_session):
    from backend.src.services import task as task_service

    with pytest.raises(ValueError, match="Invalid status"):
        task_service.update_task_status(VALID_TASK_ID, "INVALID")

@patch("backend.src.services.task.SessionLocal")
def test_start_and_complete_task(mock_session_local, mock_session):
    from backend.src.services import task as task_service

    mock_task = MagicMock(**VALID_TASK_1)
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    mock_session.get.return_value = mock_task

    started = task_service.start_task(VALID_TASK_ID)
    assert started.status == task_service.TaskStatus.IN_PROGRESS.value

    completed = task_service.complete_task(VALID_TASK_ID)
    assert completed.status == task_service.TaskStatus.COMPLETED.value

@patch("backend.src.services.task.SessionLocal")
def test_mark_task_blocked_success(mock_session_local, mock_session):
    from backend.src.services import task as task_service

    # Mock a task with ID = 1
    mock_task = MagicMock(**VALID_TASK_1, subtasks=[])
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    mock_session.get.return_value = mock_task

    result = task_service.mark_blocked(VALID_TASK_ID)

    assert result.status == task_service.TaskStatus.BLOCKED.value
    assert mock_task.status == task_service.TaskStatus.BLOCKED.value

@patch("backend.src.services.task.SessionLocal")
def test_mark_task_blocked_failure(mock_session_local, mock_session):
    from backend.src.services import task as task_service

    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    mock_session.get.return_value = None  # Task not found

    with pytest.raises(ValueError):
        task_service.mark_blocked(INVALID_TASK_ID)