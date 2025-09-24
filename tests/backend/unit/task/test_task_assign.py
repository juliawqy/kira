from unittest.mock import patch, MagicMock
from tests.mock_data.task_data import VALID_TASK_1, VALID_TASK_ID

@patch("backend.src.services.task.SessionLocal")
def test_assign_and_unassign_users(mock_session_local, mock_session):
    from backend.src.services import task as task_service

    mock_task = MagicMock(**VALID_TASK_1)
    mock_task.collaborators = None
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    mock_session.get.return_value = mock_task

    assigned = task_service.assign_task(VALID_TASK_ID, ["alice", "bob"])
    assert "alice" in (assigned.collaborators or "")
    assert "bob" in (assigned.collaborators or "")

    unassigned = task_service.unassign_task(VALID_TASK_ID, ["alice"])
    assert "alice" not in (unassigned.collaborators or "")
