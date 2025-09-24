import pytest
from unittest.mock import patch, MagicMock
from tests.mock_data.task_data import VALID_TASK_1, VALID_TASK_ID, INVALID_TASK_ID

@patch("backend.src.services.task.SessionLocal")
def test_update_task_fields(mock_session_local, mock_session):
    from backend.src.services import task as task_service

    mock_task = MagicMock(**VALID_TASK_1)
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    mock_session.get.return_value = mock_task

    updated = task_service.update_task(VALID_TASK_ID, title="New Title", description="Updated desc")
    assert updated.title == "New Title"
    assert updated.description == "Updated desc"

@patch("backend.src.services.task.SessionLocal")
def test_update_priority(mock_session_local, mock_session):
    from backend.src.services import task as task_service

    mock_task = MagicMock(**VALID_TASK_1)
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    mock_session.get.return_value = mock_task

    updated = task_service.update_task(VALID_TASK_ID, priority="High")
    assert updated.priority == "High"

@patch("backend.src.services.task.SessionLocal")
def test_update_status(mock_session_local, mock_session):
    from backend.src.services import task as task_service

    mock_task = MagicMock(**VALID_TASK_1)
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    mock_session.get.return_value = mock_task

    updated = task_service.update_task_status(VALID_TASK_ID, "Completed")
    assert updated.status == "Completed"

@patch("backend.src.services.task.SessionLocal")
def test_update_invalid_fields(mock_session_local, mock_session):
    from backend.src.services import task as task_service

    mock_task = MagicMock(**VALID_TASK_1)
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    mock_session.get.return_value = mock_task

    with pytest.raises(TypeError):
        task_service.update_task(VALID_TASK_ID, status="Completed")

@patch("backend.src.services.task.SessionLocal")
def test_update_task_not_found_returns_none(mock_session_local, mock_session):
    from backend.src.services import task as task_service

    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    mock_session.get.return_value = None

    result = task_service.update_task(INVALID_TASK_ID, title="ghost")
    assert result is None
