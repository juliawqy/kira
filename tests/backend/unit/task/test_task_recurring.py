# tests/backend/unit/task/test_task_recurring.py
from __future__ import annotations

from datetime import date, timedelta
from unittest.mock import MagicMock, patch
import pytest

from backend.src.enums.task_status import TaskStatus

pytestmark = pytest.mark.unit


def _extract_new_task_from_adds(mock_session, original_task):
    """Helper to find the newly created task object (if any) from session.add calls."""
    added = [c.args[0] for c in mock_session.add.call_args_list]
    return next((obj for obj in added if obj is not original_task), None)


# UNI-092/001
@patch("backend.src.services.task.SessionLocal")
def test_set_task_status_completed_creates_next_occurrence(mock_session_local):
    """
    When marking a recurring task Completed with a deadline, create the next occurrence (behavior-only).
    """
    from backend.src.services import task as task_service

    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session

    mock_task = MagicMock()
    mock_task.id = 100
    mock_task.title = "Recurring Task"
    mock_task.description = "desc"
    mock_task.start_date = date(2025, 10, 1)
    mock_task.deadline = date(2025, 10, 11)
    mock_task.status = TaskStatus.TO_DO.value
    mock_task.priority = 4
    mock_task.recurring = 7 
    mock_task.project_id = 42
    mock_task.active = True

    mock_session.get.return_value = mock_task

    returned = task_service.set_task_status(
        task_id=mock_task.id,
        new_status=TaskStatus.COMPLETED.value,
    )

    assert mock_task.status == TaskStatus.COMPLETED.value
    assert returned == mock_task

    new_task = _extract_new_task_from_adds(mock_session, mock_task)
    assert new_task is not None, "Expected a new recurring task to be created."

    expected_deadline = mock_task.deadline + timedelta(days=mock_task.recurring)
    assert getattr(new_task, "title") == mock_task.title
    assert getattr(new_task, "description") == mock_task.description
    assert getattr(new_task, "start_date") == mock_task.deadline
    assert getattr(new_task, "deadline") == expected_deadline
    assert getattr(new_task, "status") == TaskStatus.TO_DO.value
    assert getattr(new_task, "priority") == mock_task.priority
    assert getattr(new_task, "recurring") == mock_task.recurring
    assert getattr(new_task, "project_id") == mock_task.project_id
    assert getattr(new_task, "active") is True


# UNI-092/002
@patch("backend.src.services.task.SessionLocal")
def test_set_task_status_completed_no_creation_when_not_recurring(mock_session_local):
    """
    Marking a non-recurring task Completed should NOT create a new task (behavior-only).
    """
    from backend.src.services import task as task_service

    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session

    mock_task = MagicMock()
    mock_task.id = 101
    mock_task.title = "Non-recurring Task"
    mock_task.description = "desc"
    mock_task.start_date = date(2025, 10, 2)
    mock_task.deadline = date(2025, 10, 5)
    mock_task.status = TaskStatus.TO_DO.value
    mock_task.priority = 3
    mock_task.recurring = 0
    mock_task.project_id = None
    mock_task.active = True

    mock_session.get.return_value = mock_task

    returned = task_service.set_task_status(
        task_id=mock_task.id,
        new_status=TaskStatus.COMPLETED.value,
    )

    assert mock_task.status == TaskStatus.COMPLETED.value
    assert returned == mock_task

    new_task = _extract_new_task_from_adds(mock_session, mock_task)
    assert new_task is None, "Did not expect a new task for non-recurring completion."


# UNI-092/003
@patch("backend.src.services.task.SessionLocal")
def test_set_task_status_completed_recurring_without_deadline_raises(mock_session_local):
    """
    If recurring > 0 but deadline is None, marking Completed raises ValueError (behavior-only).
    """
    from backend.src.services import task as task_service

    # Arrange
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session

    mock_task = MagicMock()
    mock_task.id = 102
    mock_task.title = "Recurring w/o deadline"
    mock_task.description = "desc"
    mock_task.start_date = date(2025, 10, 3)
    mock_task.deadline = None         
    mock_task.status = TaskStatus.TO_DO.value
    mock_task.priority = 2
    mock_task.recurring = 5           
    mock_task.project_id = 7
    mock_task.active = True

    mock_session.get.return_value = mock_task

    with pytest.raises(ValueError) as exc:
        task_service.set_task_status(
            task_id=mock_task.id,
            new_status=TaskStatus.COMPLETED.value,
        )

    assert ("deadline" in str(exc.value)) or ("Cannot create next occurrence" in str(exc.value))

    assert mock_task.status == TaskStatus.TO_DO.value