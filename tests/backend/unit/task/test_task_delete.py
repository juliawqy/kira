import pytest
from unittest.mock import patch, MagicMock
from tests.mock_data.task_data import VALID_TASK_1, INVALID_TASK_ID

@patch("backend.src.services.task.SessionLocal")
def test_delete_task_success(mock_session_local, mock_session):
    from backend.src.services import task as task_service

    mock_task = MagicMock(**VALID_TASK_1, subtasks=[])
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    mock_session.get.return_value = mock_task

    result = task_service.delete_task(1)
    assert result["deleted"] == 1

@patch("backend.src.services.task.SessionLocal")
def test_delete_task_failure(mock_session_local, mock_session):
    from backend.src.services import task as task_service

    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    mock_session.get.return_value = None

    with pytest.raises(ValueError):
        task_service.delete_task(INVALID_TASK_ID)
