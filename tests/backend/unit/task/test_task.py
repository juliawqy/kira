# import pytest
# from unittest.mock import patch, MagicMock
# from tests.mock_data.task_data import (
#     MOCK_TASK,
#     MOCK_UPDATED_TASK,
#     MOCK_COMPLETED_TASK,
#     MOCK_SUBTASK,
# )

# # Common fixture for a mock DB session
# @pytest.fixture
# def mock_session():
#     return MagicMock()

# # --- TESTS ---

# @patch("backend.src.services.task.SessionLocal")
# def test_add_task(mock_session_local, mock_session):
#     # Mock the service so we can test without a real DB
#     from backend.src.services import task as task_service
    
#     mock_task = MagicMock(**MOCK_TASK, id=1)
#     mock_session_local.begin.return_value.__enter__.return_value = mock_session
    
#     with patch("backend.src.services.task.Task", return_value=mock_task):
#         task = task_service.add_task(**MOCK_TASK)
    
#     assert task.id == 1
#     assert task.title == MOCK_TASK["title"]

# @patch("backend.src.services.task.SessionLocal")
# def test_get_task_with_subtasks(mock_session_local, mock_session):
#     from backend.src.services import task as task_service
    
#     mock_task = MagicMock(id=1, title="Test Task", subtasks=[])
#     mock_session_local.return_value.__enter__.return_value = mock_session
#     mock_session.execute.return_value.scalar_one_or_none.return_value = mock_task
    
#     task = task_service.get_task_with_subtasks(1)
#     assert task.id == 1
#     assert task.title == "Test Task"

# @patch("backend.src.services.task.SessionLocal")
# def test_list_parent_tasks(mock_session_local, mock_session):
#     from backend.src.services import task as task_service
    
#     mock_tasks = [MagicMock(id=1, title="Parent 1"), MagicMock(id=2, title="Parent 2")]
#     mock_session_local.return_value.__enter__.return_value = mock_session
#     mock_session.execute.return_value.scalars.return_value.all.return_value = mock_tasks
    
#     tasks = task_service.list_parent_tasks()
#     assert len(tasks) == 2
#     assert tasks[0].title == "Parent 1"

# @patch("backend.src.services.task.SessionLocal")
# def test_update_task(mock_session_local, mock_session):
#     from backend.src.services import task as task_service
    
#     mock_task = MagicMock(id=1, **MOCK_UPDATED_TASK)
#     mock_session_local.begin.return_value.__enter__.return_value = mock_session
#     mock_session.get.return_value = mock_task
    
#     updated_task = task_service.update_task(1, **MOCK_UPDATED_TASK)
#     assert updated_task.title == MOCK_UPDATED_TASK["title"]

# @patch("backend.src.services.task.SessionLocal")
# def test_update_task_status(mock_session_local, mock_session):
#     from backend.src.services import task as task_service
    
#     mock_task = MagicMock(id=1, status="In-progress")
#     mock_session_local.begin.return_value.__enter__.return_value = mock_session
#     mock_session.get.return_value = mock_task
    
#     updated_task = task_service.update_task_status(1, "In-progress")
#     assert updated_task.status == "In-progress"

# @patch("backend.src.services.task.SessionLocal")
# def test_start_task(mock_session_local, mock_session):
#     from backend.src.services import task as task_service
    
#     mock_task = MagicMock(id=1, status="In-progress")
#     mock_session_local.begin.return_value.__enter__.return_value = mock_session
#     mock_session.get.return_value = mock_task
    
#     started_task = task_service.start_task(1)
#     assert started_task.status == "In-progress"

# @patch("backend.src.services.task.SessionLocal")
# def test_complete_task(mock_session_local, mock_session):
#     from backend.src.services import task as task_service
    
#     mock_task = MagicMock(id=1, **MOCK_COMPLETED_TASK)
#     mock_session_local.begin.return_value.__enter__.return_value = mock_session
#     mock_session.get.return_value = mock_task
    
#     completed_task = task_service.complete_task(1)
#     assert completed_task.status == "Completed"

# @patch("backend.src.services.task.SessionLocal")
# def test_assign_task(mock_session_local, mock_session):
#     from backend.src.services import task as task_service
    
#     mock_task = MagicMock(id=1, collaborators="Alice,Bob")
#     mock_session_local.begin.return_value.__enter__.return_value = mock_session
#     mock_session.get.return_value = mock_task
    
#     with patch("backend.src.services.task._csv_to_list", return_value=["Alice", "Bob"]):
#         with patch("backend.src.services.task._normalize_members", return_value=["Alice", "Bob", "Charlie"]):
#             with patch("backend.src.services.task._list_to_csv", return_value="Alice,Bob,Charlie"):
#                 assigned_task = task_service.assign_task(1, ["Charlie"])
#                 assert "Charlie" in assigned_task.collaborators

# @patch("backend.src.services.task.SessionLocal")
# def test_unassign_task(mock_session_local, mock_session):
#     from backend.src.services import task as task_service
    
#     mock_task = MagicMock(id=1, collaborators="Alice,Bob")
#     mock_session_local.begin.return_value.__enter__.return_value = mock_session
#     mock_session.get.return_value = mock_task
    
#     with patch("backend.src.services.task._csv_to_list", return_value=["Alice", "Bob"]):
#         with patch("backend.src.services.task._normalize_members", return_value=["Bob"]):
#             with patch("backend.src.services.task._list_to_csv", return_value="Bob"):
#                 unassigned_task = task_service.unassign_task(1, ["Alice"])
#                 assert "Alice" not in unassigned_task.collaborators

# @patch("backend.src.services.task.SessionLocal")
# def test_delete_subtask(mock_session_local, mock_session):
#     from backend.src.services import task as task_service
    
#     mock_subtask = MagicMock(id=2, parent_id=1)
#     mock_session_local.begin.return_value.__enter__.return_value = mock_session
#     mock_session.get.return_value = mock_subtask
    
#     result = task_service.delete_subtask(2)
#     assert result is True
#     mock_session.delete.assert_called_with(mock_subtask)

# @patch("backend.src.services.task.SessionLocal")
# def test_delete_task(mock_session_local, mock_session):
#     from backend.src.services import task as task_service
    
#     mock_task = MagicMock(id=1, subtasks=[])
#     mock_session_local.begin.return_value.__enter__.return_value = mock_session
#     mock_session.get.return_value = mock_task
    
#     result = task_service.delete_task(1)
#     assert result == {"deleted": 1, "subtasks_detached": 0}
#     mock_session.delete.assert_called_with(mock_task)
