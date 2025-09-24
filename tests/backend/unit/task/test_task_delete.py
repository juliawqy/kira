import pytest
from unittest.mock import patch, MagicMock
from tests.mock_data.task_data import VALID_TASK_1, VALID_TASK_ID, INVALID_TASK_ID

@patch("backend.src.services.task.SessionLocal")
def test_delete_task_success(mock_session_local, mock_session):
    from backend.src.services import task as task_service

    mock_task = MagicMock(**VALID_TASK_1, subtasks=[])
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    mock_session.get.return_value = mock_task

    result = task_service.delete_task(VALID_TASK_ID)
    assert result["deleted"] == 1

@patch("backend.src.services.task.SessionLocal")
def test_delete_task_failure(mock_session_local, mock_session):
    from backend.src.services import task as task_service

    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    mock_session.get.return_value = None

    with pytest.raises(ValueError):
        task_service.delete_task(INVALID_TASK_ID)

@patch("backend.src.services.task.SessionLocal")
def test_delete_subtask_not_found_returns_false(mock_session_local, mock_session):
    from backend.src.services import task as task_service

    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    mock_session.get.return_value = None

    assert task_service.delete_subtask(INVALID_TASK_ID) is False

@patch("backend.src.services.task.SessionLocal")
def test_delete_subtask_not_a_subtask_raises(mock_session_local, mock_session):
    from backend.src.services import task as task_service

    mock_task = MagicMock(**VALID_TASK_1, parent_id=None)
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    mock_session.get.return_value = mock_task

    with pytest.raises(ValueError, match="is not a subtask"):
        task_service.delete_subtask(mock_task.id)
