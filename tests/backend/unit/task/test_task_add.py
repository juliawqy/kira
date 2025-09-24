import pytest
from unittest.mock import patch, MagicMock
from tests.mock_data.task_data import (
    VALID_ADD,
    VALID_TASK_1,
    INVALID_TASK_NO_TITLE,
    INVALID_TASK_NO_STATUS,
    INVALID_TASK_NO_PRIORITY,
)

@patch("backend.src.services.task.SessionLocal")
def test_add_task_success(mock_session_local, mock_session):
    from backend.src.services import task as task_service

    mock_session_local.begin.return_value.__enter__.return_value = mock_session

    # Create mock task with ID = 1 (simulating database auto-generation)
    mock_task = MagicMock()
    mock_task.id = VALID_TASK_1["id"]
    mock_task.title = VALID_TASK_1["title"]
    mock_task.description = VALID_TASK_1["description"]
    mock_task.status = VALID_TASK_1["status"]
    mock_task.priority = VALID_TASK_1["priority"]
    mock_task.start_date = VALID_TASK_1["start_date"]
    mock_task.deadline = VALID_TASK_1["deadline"]
    mock_task.collaborators = VALID_TASK_1["collaborators"]

    with patch("backend.src.services.task.Task", return_value=mock_task):
        result = task_service.add_task(**VALID_ADD)
        assert result.id == VALID_TASK_1["id"]
        assert result.title == VALID_TASK_1["title"]

@pytest.mark.parametrize("invalid_task", [
    INVALID_TASK_NO_TITLE,
    INVALID_TASK_NO_STATUS,
    INVALID_TASK_NO_PRIORITY,
])
@patch("backend.src.services.task.SessionLocal")
def test_add_task_failure(mock_session_local, mock_session, invalid_task):
    from backend.src.services import task as task_service

    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    with pytest.raises(ValueError):
        task_service.add_task(**invalid_task)
