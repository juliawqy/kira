import pytest
from unittest.mock import patch, MagicMock
from tests.mock_data.task_data import VALID_TASK_1, VALID_TASK_2, VALID_TASK_ID, INVALID_TASK_ID

# KIRA-001/001 (test case id corresponding to test case sheets)
@patch("backend.src.services.task.SessionLocal")
def test_get_task_by_id_success(mock_session_local):
    from backend.src.services import task as task_service

    mock_session = MagicMock()
    mock_task = MagicMock()
    mock_task.id = VALID_TASK_1["id"]
    mock_task.title = VALID_TASK_1["title"]
    
    mock_session_local.return_value.__enter__.return_value = mock_session
    mock_session.execute.return_value.scalar_one_or_none.return_value = mock_task # Mock returns actual value instead of mocked object

    task = task_service.get_task_with_subtasks(VALID_TASK_ID)
    assert task.id == VALID_TASK_ID
    assert task.title == VALID_TASK_1["title"]

# KIRA-001/001 (test case id corresponding to test case sheets)
@patch("backend.src.services.task.SessionLocal")
def test_get_task_by_id_failure(mock_session_local):
    from backend.src.services import task as task_service

    mock_session = MagicMock()
    mock_session_local.return_value.__enter__.return_value = mock_session
    mock_session.execute.return_value.scalar_one_or_none.return_value = None

    task = task_service.get_task_with_subtasks(INVALID_TASK_ID)
    assert task is None

# KIRA-001/001 (test case id corresponding to test case sheets)
@patch("backend.src.services.task.SessionLocal")
def test_list_all_tasks_success(mock_session_local):
    from backend.src.services import task as task_service

    mock_session = MagicMock()
    mock_task_1 = MagicMock()
    mock_task_1.id = VALID_TASK_1["id"]
    mock_task_1.title = VALID_TASK_1["title"]
    
    mock_task_2 = MagicMock()
    mock_task_2.id = VALID_TASK_2["id"]
    mock_task_2.title = VALID_TASK_2["title"]
    
    mock_session_local.return_value.__enter__.return_value = mock_session
    mock_session.execute.return_value.scalars.return_value.all.return_value = [
        mock_task_1,
        mock_task_2,
    ]

    tasks = task_service.list_parent_tasks()
    assert len(tasks) == 2
