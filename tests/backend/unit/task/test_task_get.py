# tests/backend/unit/task/test_task_get.py
import pytest
from unittest.mock import patch, MagicMock
from datetime import date, timedelta
from sqlalchemy.dialects import sqlite
from tests.mock_data.task.unit_data import (
    VALID_DEFAULT_TASK,
    VALID_TASK_EXPLICIT_PRIORITY,
    VALID_TASK_FULL,
    INACTIVE_TASK,
    VALID_TASK_TODO,
    VALID_TASK_IN_PROGRESS,
    VALID_TASK_COMPLETED,
    VALID_TASK_BLOCKED,
    EMPTY_PROJECT_ID,
    VALID_PROJECT_ID,
    VALID_PROJECT_ID_INACTIVE_TASK,
    INVALID_TASK_ID_NONEXISTENT,
    INVALID_TASK_ID_TYPE
)

pytestmark = pytest.mark.unit
INVALID_FILTER = "invalid_filter"

# UNI-002/001
@patch("backend.src.services.task.SessionLocal")
def test_list_tasks_default_sort(mock_session_local):
    """List all tasks sorted by priority descending (default)"""
    from backend.src.services import task as task_service
    
    mock_session = MagicMock()
    mock_session_local.return_value.__enter__.return_value = mock_session

    mock_task1 = MagicMock()
    mock_task1.id = VALID_TASK_FULL["id"]
    mock_task1.title = VALID_TASK_FULL["title"]
    mock_task1.priority = VALID_TASK_FULL["priority"]  
    mock_task1.status = VALID_TASK_FULL["status"]
    mock_task1.active = True
    
    mock_task2 = MagicMock()
    mock_task2.id = VALID_TASK_EXPLICIT_PRIORITY["id"]
    mock_task2.title = VALID_TASK_EXPLICIT_PRIORITY["title"]
    mock_task2.priority = VALID_TASK_EXPLICIT_PRIORITY["priority"]  
    mock_task2.status = VALID_TASK_EXPLICIT_PRIORITY["status"]
    mock_task2.active = True
    
    mock_task3 = MagicMock()
    mock_task3.id = VALID_DEFAULT_TASK["id"]
    mock_task3.title = VALID_DEFAULT_TASK["title"]
    mock_task3.priority = VALID_DEFAULT_TASK["priority"]  
    mock_task3.status = VALID_DEFAULT_TASK["status"]
    mock_task3.active = True
    
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [mock_task1, mock_task2, mock_task3]
    mock_session.execute.return_value = mock_result
    
    result = task_service.list_parent_tasks()

    mock_session.execute.assert_called_once()
    executed_stmt = mock_session.execute.call_args[0][0]
    compiled = executed_stmt.compile(dialect=sqlite.dialect(), compile_kwargs={"literal_binds": True})
    sql_text = str(compiled).lower()
    
    assert "order by" in sql_text and "priority" in sql_text, f"Priority ordering not found in SQL: {sql_text}"
    
    assert len(result) == 3
    assert result[0].priority == 9
    assert result[1].priority == 8
    assert result[2].priority == 5

    task_titles = {t.title for t in result}
    assert VALID_DEFAULT_TASK["title"] in task_titles
    assert VALID_TASK_EXPLICIT_PRIORITY["title"] in task_titles
    assert VALID_TASK_FULL["title"] in task_titles

# UNI-002/002
@patch("backend.src.services.task.SessionLocal")
def test_list_tasks_exclude_inactive_tasks(mock_session_local):
    """List tasks excludes inactive tasks by default"""
    from backend.src.services import task as task_service
    
    mock_session = MagicMock()
    mock_session_local.return_value.__enter__.return_value = mock_session

    mock_active_task = MagicMock()
    mock_active_task.id = VALID_DEFAULT_TASK["id"]
    mock_active_task.title = VALID_DEFAULT_TASK["title"]
    mock_active_task.status = VALID_DEFAULT_TASK["status"]
    mock_active_task.active = True

    mock_inactive_task = MagicMock()
    mock_inactive_task.id = INACTIVE_TASK["id"]
    mock_inactive_task.title = INACTIVE_TASK["title"]
    mock_inactive_task.status = INACTIVE_TASK["status"]
    mock_inactive_task.active = False

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [mock_active_task]
    mock_session.execute.return_value = mock_result
    
    result = task_service.list_parent_tasks()
    
    mock_session.execute.assert_called_once()
    executed_stmt = mock_session.execute.call_args[0][0]
    compiled = executed_stmt.compile(dialect=sqlite.dialect(), compile_kwargs={"literal_binds": True})
    sql_text = str(compiled).lower()

    assert "active" in sql_text and ("true" in sql_text or "1" in sql_text), f"Active filter not found in SQL: {sql_text}"
    
    assert len(result) == 1
    assert result[0].title == VALID_DEFAULT_TASK["title"]
    result_titles = {t.title for t in result}
    assert INACTIVE_TASK["title"] not in result_titles

# UNI-002/003
@patch("backend.src.services.task.SessionLocal")
def test_list_tasks_include_inactive_when_requested(mock_session_local):
    """active_only=False includes inactive tasks."""
    from backend.src.services import task as task_service
    
    mock_session = MagicMock()
    mock_session_local.return_value.__enter__.return_value = mock_session

    mock_active_task = MagicMock()
    mock_active_task.id = VALID_DEFAULT_TASK["id"]
    mock_active_task.title = VALID_DEFAULT_TASK["title"]
    mock_active_task.status = VALID_DEFAULT_TASK["status"]
    mock_active_task.active = True
    
    mock_inactive_task = MagicMock()
    mock_inactive_task.id = INACTIVE_TASK["id"]
    mock_inactive_task.title = INACTIVE_TASK["title"]
    mock_inactive_task.status = INACTIVE_TASK["status"]
    mock_inactive_task.active = False
    
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [mock_active_task, mock_inactive_task]
    mock_session.execute.return_value = mock_result
    
    result = task_service.list_parent_tasks(active_only=False)

    mock_session.execute.assert_called_once()
    executed_stmt = mock_session.execute.call_args[0][0]
    compiled = executed_stmt.compile(dialect=sqlite.dialect(), compile_kwargs={"literal_binds": True})
    sql_text = str(compiled).lower()

    assert not ("active" in sql_text and ("true" in sql_text or "1" in sql_text)), f"Active filter should not be present when active_only=False: {sql_text}"
    
    assert len(result) == 2
    titles = {t.title for t in result}
    assert VALID_DEFAULT_TASK["title"] in titles
    assert INACTIVE_TASK["title"] in titles

# UNI-002/004
@patch("backend.src.services.task.SessionLocal")
def test_list_tasks_with_empty_task_list(mock_session_local):
    """List tasks returns empty list when no tasks exist"""
    from backend.src.services import task as task_service
    
    mock_session = MagicMock()
    mock_session_local.return_value.__enter__.return_value = mock_session
    
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_session.execute.return_value = mock_result
    
    result = task_service.list_parent_tasks()
    
    assert len(result) == 0
    assert result == []

# UNI-002/005
@patch("backend.src.services.task.SessionLocal")
def test_list_tasks_with_priority_filter(mock_session_local):
    
    """Filter by priority range returns only matching tasks."""
    from backend.src.services import task as task_service
    
    mock_session = MagicMock()
    mock_session_local.return_value.__enter__.return_value = mock_session

    mock_priority_5_task = MagicMock()
    mock_priority_5_task.id = VALID_DEFAULT_TASK["id"]
    mock_priority_5_task.title = VALID_DEFAULT_TASK["title"]
    mock_priority_5_task.priority = VALID_DEFAULT_TASK["priority"]
    mock_priority_5_task.active = True
    
    mock_priority_8_task = MagicMock()
    mock_priority_8_task.id = VALID_TASK_EXPLICIT_PRIORITY["id"]
    mock_priority_8_task.title = VALID_TASK_EXPLICIT_PRIORITY["title"]
    mock_priority_8_task.priority = VALID_TASK_EXPLICIT_PRIORITY["priority"]
    mock_priority_8_task.active = True

    mock_priority_9_task = MagicMock()
    mock_priority_9_task.id = VALID_TASK_FULL["id"]
    mock_priority_9_task.title = VALID_TASK_FULL["title"]
    mock_priority_9_task.priority = VALID_TASK_FULL["priority"]  
    mock_priority_9_task.active = True

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [mock_priority_5_task, mock_priority_8_task]
    mock_session.execute.return_value = mock_result
    
    result = task_service.list_parent_tasks(filter_by={"priority_range": [5, 8]})

    mock_session.execute.assert_called_once()
    executed_stmt = mock_session.execute.call_args[0][0]
    compiled = executed_stmt.compile(dialect=sqlite.dialect(), compile_kwargs={"literal_binds": True})
    sql_text = str(compiled).lower()

    assert "priority" in sql_text and ("5" in sql_text and "8" in sql_text), f"Priority range filter not found in SQL: {sql_text}"
    
    assert len(result) == 2
    titles = {t.title for t in result}
    assert VALID_DEFAULT_TASK["title"] in titles
    assert VALID_TASK_EXPLICIT_PRIORITY["title"] in titles
    assert VALID_TASK_FULL["title"] not in titles

# UNI-002/006
@patch("backend.src.services.task.SessionLocal")
def test_list_tasks_with_combined_date_filters(mock_session_local):
    """Filter by combined date ranges works correctly - both start_date and due_date filtering together"""
    from backend.src.services import task as task_service
    
    mock_session = MagicMock()
    mock_session_local.return_value.__enter__.return_value = mock_session
        
    mock_task_todo = MagicMock()
    mock_task_todo.id = VALID_TASK_TODO["id"]
    mock_task_todo.title = VALID_TASK_TODO["title"]
    mock_task_todo.start_date = VALID_TASK_TODO["start_date"]
    mock_task_todo.deadline = VALID_TASK_TODO["deadline"]
    mock_task_todo.active = True

    mock_task_in_progress = MagicMock()
    mock_task_in_progress.id = VALID_TASK_IN_PROGRESS["id"]
    mock_task_in_progress.title = VALID_TASK_IN_PROGRESS["title"]
    mock_task_in_progress.start_date = VALID_TASK_IN_PROGRESS["start_date"]
    mock_task_in_progress.deadline = VALID_TASK_IN_PROGRESS["deadline"]
    mock_task_in_progress.active = True
    
    mock_task_completed = MagicMock()
    mock_task_completed.id = VALID_TASK_COMPLETED["id"]
    mock_task_completed.title = VALID_TASK_COMPLETED["title"]
    mock_task_completed.start_date = VALID_TASK_COMPLETED["start_date"]
    mock_task_completed.deadline = VALID_TASK_COMPLETED["deadline"]
    mock_task_completed.active = True
    
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [mock_task_in_progress, mock_task_todo]
    mock_session.execute.return_value = mock_result
    
    start_range = [date.today() - timedelta(days=10), date.today() + timedelta(days=10)]
    due_range = [date.today() - timedelta(days=5), date.today() + timedelta(days=15)]
    
    result = task_service.list_parent_tasks(filter_by={
        "start_date_range": start_range,
        "deadline_range": due_range
    })
    
    mock_session.execute.assert_called_once()
    executed_stmt = mock_session.execute.call_args[0][0]
    compiled = executed_stmt.compile(dialect=sqlite.dialect(), compile_kwargs={"literal_binds": True})
    sql_text = str(compiled).lower()
    
    assert "start_date" in sql_text and "deadline" in sql_text, f"Both date filters not found in SQL: {sql_text}"
    assert len(result) == 2
    result_titles = {t.title for t in result}
    assert VALID_TASK_IN_PROGRESS["title"] in result_titles
    assert VALID_TASK_TODO["title"] in result_titles

# UNI-002/007
@patch("backend.src.services.task.SessionLocal")
def test_list_tasks_with_status_filter(mock_session_local):
    """Filter by status returns only matching tasks from a mixed set"""
    from backend.src.services import task as task_service
    
    mock_session = MagicMock()
    mock_session_local.return_value.__enter__.return_value = mock_session
  
    mock_todo_task = MagicMock()
    mock_todo_task.id = VALID_TASK_TODO["id"]
    mock_todo_task.title = VALID_TASK_TODO["title"]
    mock_todo_task.status = VALID_TASK_TODO["status"]
    mock_todo_task.active = True
    
    mock_in_progress_task = MagicMock()
    mock_in_progress_task.id = VALID_TASK_IN_PROGRESS["id"]
    mock_in_progress_task.title = VALID_TASK_IN_PROGRESS["title"]
    mock_in_progress_task.status = VALID_TASK_IN_PROGRESS["status"]
    mock_in_progress_task.active = True
    
    mock_completed_task = MagicMock()
    mock_completed_task.id = VALID_TASK_COMPLETED["id"]
    mock_completed_task.title = VALID_TASK_COMPLETED["title"]
    mock_completed_task.status = VALID_TASK_COMPLETED["status"]
    mock_completed_task.active = True

    mock_blocked_task = MagicMock()
    mock_blocked_task.id = VALID_TASK_BLOCKED["id"]
    mock_blocked_task.title = VALID_TASK_BLOCKED["title"]
    mock_blocked_task.status = VALID_TASK_BLOCKED["status"]
    mock_blocked_task.active = True

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [mock_blocked_task] 
    mock_session.execute.return_value = mock_result
    
    result = task_service.list_parent_tasks(filter_by={"status": VALID_TASK_BLOCKED["status"]})
    
    mock_session.execute.assert_called_once()
    executed_stmt = mock_session.execute.call_args[0][0]
    compiled = executed_stmt.compile(dialect=sqlite.dialect(), compile_kwargs={"literal_binds": True})
    sql_text = str(compiled).lower()
    expected_status = VALID_TASK_BLOCKED["status"].lower()
    assert "status" in sql_text and expected_status in sql_text, f"Status filter not found in SQL: {sql_text}"

    assert len(result) == 1
    assert result[0].status == VALID_TASK_BLOCKED["status"]
    assert result[0].title == VALID_TASK_BLOCKED["title"]

    result_statuses = {t.status for t in result}
    assert VALID_TASK_TODO["status"] not in result_statuses
    assert VALID_TASK_IN_PROGRESS["status"] not in result_statuses
    assert VALID_TASK_COMPLETED["status"] not in result_statuses

# UNI-002/008
@patch("backend.src.services.task.SessionLocal")
def test_list_tasks_with_start_date_sort(mock_session_local):
    """Sort by start_date_asc orders tasks correctly, with priority as secondary sort for same dates"""
    from backend.src.services import task as task_service
    
    mock_session = MagicMock()
    mock_session_local.return_value.__enter__.return_value = mock_session

    mock_task_completed = MagicMock()
    mock_task_completed.id = VALID_TASK_COMPLETED["id"]
    mock_task_completed.title = VALID_TASK_COMPLETED["title"]
    mock_task_completed.start_date = VALID_TASK_COMPLETED["start_date"] 
    mock_task_completed.priority = VALID_TASK_COMPLETED["priority"]  
    mock_task_completed.active = True

    mock_task_blocked = MagicMock()
    mock_task_blocked.id = VALID_TASK_BLOCKED["id"]
    mock_task_blocked.title = VALID_TASK_BLOCKED["title"]
    mock_task_blocked.start_date = VALID_TASK_BLOCKED["start_date"]  
    mock_task_blocked.priority = VALID_TASK_BLOCKED["priority"]  
    mock_task_blocked.active = True

    mock_task_in_progress = MagicMock()
    mock_task_in_progress.id = VALID_TASK_IN_PROGRESS["id"]
    mock_task_in_progress.title = VALID_TASK_IN_PROGRESS["title"]
    mock_task_in_progress.start_date = VALID_TASK_IN_PROGRESS["start_date"]  
    mock_task_in_progress.priority = VALID_TASK_IN_PROGRESS["priority"]  
    mock_task_in_progress.active = True

    mock_task_todo = MagicMock()
    mock_task_todo.id = VALID_TASK_TODO["id"]
    mock_task_todo.title = VALID_TASK_TODO["title"]
    mock_task_todo.start_date = VALID_TASK_TODO["start_date"]  
    mock_task_todo.priority = VALID_TASK_TODO["priority"]  
    mock_task_todo.active = True
    
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [
        mock_task_completed,  # First: 10 days ago, priority 6 (higher priority than blocked)
        mock_task_blocked,    # Second: 10 days ago, priority 5 (lower priority than completed)
        mock_task_in_progress, # Third: 2 days ago
        mock_task_todo        # Fourth: 1 day from now
    ]
    mock_session.execute.return_value = mock_result
    
    result = task_service.list_parent_tasks(sort_by="start_date_asc")

    mock_session.execute.assert_called_once()
    executed_stmt = mock_session.execute.call_args[0][0]
    compiled = executed_stmt.compile(dialect=sqlite.dialect(), compile_kwargs={"literal_binds": True})
    sql_text = str(compiled).lower()
    
    assert "order by" in sql_text and "start_date" in sql_text, f"Start date ordering not found in SQL: {sql_text}"
    assert len(result) == 4

    assert result[0].title == VALID_TASK_COMPLETED["title"]  # 10 days ago, priority 6
    assert result[1].title == VALID_TASK_BLOCKED["title"]    # 10 days ago, priority 5  
    assert result[2].title == VALID_TASK_IN_PROGRESS["title"] # 2 days ago
    assert result[3].title == VALID_TASK_TODO["title"]       # 1 day from now

# UNI-002/009
@patch("backend.src.services.task.SessionLocal")
def test_list_tasks_with_due_deadline_sort(mock_session_local):
    """Sort by deadline_asc orders tasks correctly, with priority as secondary sort for same dates"""
    from backend.src.services import task as task_service
    
    mock_session = MagicMock()
    mock_session_local.return_value.__enter__.return_value = mock_session

    mock_task_completed = MagicMock()
    mock_task_completed.id = VALID_TASK_COMPLETED["id"]
    mock_task_completed.title = VALID_TASK_COMPLETED["title"]
    mock_task_completed.deadline = VALID_TASK_COMPLETED["deadline"]  
    mock_task_completed.priority = VALID_TASK_COMPLETED["priority"]  
    mock_task_completed.active = True

    mock_task_todo = MagicMock()
    mock_task_todo.id = VALID_TASK_TODO["id"]
    mock_task_todo.title = VALID_TASK_TODO["title"]
    mock_task_todo.deadline = VALID_TASK_TODO["deadline"]  
    mock_task_todo.priority = VALID_TASK_TODO["priority"]  
    mock_task_todo.active = True
    
    mock_task_in_progress = MagicMock()
    mock_task_in_progress.id = VALID_TASK_IN_PROGRESS["id"]
    mock_task_in_progress.title = VALID_TASK_IN_PROGRESS["title"]
    mock_task_in_progress.deadline = VALID_TASK_IN_PROGRESS["deadline"]  
    mock_task_in_progress.priority = VALID_TASK_IN_PROGRESS["priority"]  
    mock_task_in_progress.active = True
    
    mock_task_blocked = MagicMock()
    mock_task_blocked.id = VALID_TASK_BLOCKED["id"]
    mock_task_blocked.title = VALID_TASK_BLOCKED["title"]
    mock_task_blocked.deadline = VALID_TASK_BLOCKED["deadline"]  
    mock_task_blocked.priority = VALID_TASK_BLOCKED["priority"]  
    mock_task_blocked.active = True
    
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [
        mock_task_completed,   # First: 3 days ago
        mock_task_todo,        # Second: 7 days from now
        mock_task_in_progress, # Third: 14 days from now, priority 9 (higher priority than blocked)
        mock_task_blocked      # Fourth: 14 days from now, priority 5 (lower priority than in_progress)
    ]
    mock_session.execute.return_value = mock_result
    result = task_service.list_parent_tasks(sort_by="deadline_asc")

    mock_session.execute.assert_called_once()
    executed_stmt = mock_session.execute.call_args[0][0]
    compiled = executed_stmt.compile(dialect=sqlite.dialect(), compile_kwargs={"literal_binds": True})
    sql_text = str(compiled).lower()
    
    assert "order by" in sql_text and "deadline" in sql_text, f"Deadline ordering not found in SQL: {sql_text}"
    assert len(result) == 4
    
    assert result[0].title == VALID_TASK_COMPLETED["title"]   # 3 days ago
    assert result[1].title == VALID_TASK_TODO["title"]        # 7 days from now
    assert result[2].title == VALID_TASK_IN_PROGRESS["title"] # 14 days from now, priority 9
    assert result[3].title == VALID_TASK_BLOCKED["title"]     # 14 days from now, priority 5

# UNI-002/010
@patch("backend.src.services.task.SessionLocal")
def test_list_tasks_with_status_sort(mock_session_local):
    """Sort by status orders tasks correctly with all status types"""
    from backend.src.services import task as task_service
    
    mock_session = MagicMock()
    mock_session_local.return_value.__enter__.return_value = mock_session
    
    mock_task_blocked = MagicMock()
    mock_task_blocked.id = VALID_TASK_BLOCKED["id"]
    mock_task_blocked.title = VALID_TASK_BLOCKED["title"]
    mock_task_blocked.status = VALID_TASK_BLOCKED["status"]  
    mock_task_blocked.priority = VALID_TASK_BLOCKED["priority"] 
    mock_task_blocked.active = True
    
    mock_task_completed = MagicMock()
    mock_task_completed.id = VALID_TASK_COMPLETED["id"]
    mock_task_completed.title = VALID_TASK_COMPLETED["title"]
    mock_task_completed.status = VALID_TASK_COMPLETED["status"]  
    mock_task_completed.priority = VALID_TASK_COMPLETED["priority"]  
    mock_task_completed.active = True
    
    mock_task_in_progress = MagicMock()
    mock_task_in_progress.id = VALID_TASK_IN_PROGRESS["id"]
    mock_task_in_progress.title = VALID_TASK_IN_PROGRESS["title"]
    mock_task_in_progress.status = VALID_TASK_IN_PROGRESS["status"]  
    mock_task_in_progress.priority = VALID_TASK_IN_PROGRESS["priority"] 
    mock_task_in_progress.active = True
    
    mock_task_todo = MagicMock()
    mock_task_todo.id = VALID_TASK_TODO["id"]
    mock_task_todo.title = VALID_TASK_TODO["title"]
    mock_task_todo.status = VALID_TASK_TODO["status"]
    mock_task_todo.priority = VALID_TASK_TODO["priority"]  
    mock_task_todo.active = True

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [
        mock_task_todo,        # First: TO_DO
        mock_task_in_progress, # Second: IN_PROGRESS
        mock_task_completed,   # Third: COMPLETED
        mock_task_blocked,     # Fourth: BLOCKED (last)
    ]
    mock_session.execute.return_value = mock_result
    result = task_service.list_parent_tasks(sort_by="status")
 
    mock_session.execute.assert_called_once()
    executed_stmt = mock_session.execute.call_args[0][0]
    compiled = executed_stmt.compile(dialect=sqlite.dialect(), compile_kwargs={"literal_binds": True})
    sql_text = str(compiled).lower()
    
    assert "order by" in sql_text and "status" in sql_text, f"Status ordering not found in SQL: {sql_text}"
    assert len(result) == 4

    assert result[0].status == VALID_TASK_TODO["status"]       
    assert result[1].status == VALID_TASK_IN_PROGRESS["status"]
    assert result[2].status == VALID_TASK_COMPLETED["status"]  
    assert result[3].status == VALID_TASK_BLOCKED["status"]    

    assert result[0].title == VALID_TASK_TODO["title"]
    assert result[1].title == VALID_TASK_IN_PROGRESS["title"]
    assert result[2].title == VALID_TASK_COMPLETED["title"]
    assert result[3].title == VALID_TASK_BLOCKED["title"]

# UNI-002/011
@patch("backend.src.services.task.SessionLocal")
def test_list_tasks_with_invalid_sort_raises_error(mock_session_local):
    """Invalid sort parameter raises ValueError"""
    from backend.src.services import task as task_service
    
    mock_session = MagicMock()
    mock_session_local.return_value.__enter__.return_value = mock_session
    
    with pytest.raises(ValueError) as exc:
        task_service.list_parent_tasks(sort_by="invalid_sort")
    
    assert "Invalid sort_by parameter" in str(exc.value)

# UNI-002/012
@patch("backend.src.services.task.SessionLocal")
def test_list_tasks_with_deadline_filter_and_status_sort(mock_session_local):
    """Combine deadline filter with status sorting using all task types"""
    from backend.src.services import task as task_service
    
    mock_session = MagicMock()
    mock_session_local.return_value.__enter__.return_value = mock_session

    mock_task_todo = MagicMock()
    mock_task_todo.id = VALID_TASK_TODO["id"]
    mock_task_todo.title = VALID_TASK_TODO["title"]
    mock_task_todo.status = VALID_TASK_TODO["status"] 
    mock_task_todo.deadline = VALID_TASK_TODO["deadline"]  
    mock_task_todo.priority = VALID_TASK_TODO["priority"]
    mock_task_todo.active = True
    
    mock_task_in_progress = MagicMock()
    mock_task_in_progress.id = VALID_TASK_IN_PROGRESS["id"]
    mock_task_in_progress.title = VALID_TASK_IN_PROGRESS["title"]
    mock_task_in_progress.status = VALID_TASK_IN_PROGRESS["status"] 
    mock_task_in_progress.deadline = VALID_TASK_IN_PROGRESS["deadline"] 
    mock_task_in_progress.priority = VALID_TASK_IN_PROGRESS["priority"]
    mock_task_in_progress.active = True
    
    mock_task_completed = MagicMock()
    mock_task_completed.id = VALID_TASK_COMPLETED["id"]
    mock_task_completed.title = VALID_TASK_COMPLETED["title"]
    mock_task_completed.status = VALID_TASK_COMPLETED["status"]
    mock_task_completed.deadline = VALID_TASK_COMPLETED["deadline"]  
    mock_task_completed.priority = VALID_TASK_COMPLETED["priority"]
    mock_task_completed.active = True
    
    mock_task_blocked = MagicMock()
    mock_task_blocked.id = VALID_TASK_BLOCKED["id"]
    mock_task_blocked.title = VALID_TASK_BLOCKED["title"]
    mock_task_blocked.status = VALID_TASK_BLOCKED["status"]
    mock_task_blocked.deadline = VALID_TASK_BLOCKED["deadline"]  
    mock_task_blocked.priority = VALID_TASK_BLOCKED["priority"]
    mock_task_blocked.active = True
    
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [
        mock_task_todo,
        mock_task_in_progress,
        mock_task_blocked
    ]
    mock_session.execute.return_value = mock_result
    
    deadline_start = date.today()
    deadline_end = date.today() + timedelta(days=20)
    
    result = task_service.list_parent_tasks(
        filter_by={"deadline_range": [deadline_start, deadline_end]},
        sort_by="status"
    )

    mock_session.execute.assert_called_once()
    executed_stmt = mock_session.execute.call_args[0][0]
    compiled = executed_stmt.compile(dialect=sqlite.dialect(), compile_kwargs={"literal_binds": True})
    sql_text = str(compiled).lower()
    
    assert "deadline" in sql_text, f"Deadline filter not found in SQL: {sql_text}"
    assert "order by" in sql_text and "status" in sql_text, f"Status sort not found in SQL: {sql_text}"

    assert len(result) == 3
    assert result[0].status == VALID_TASK_TODO["status"]        
    assert result[1].status == VALID_TASK_IN_PROGRESS["status"] 
    assert result[2].status == VALID_TASK_BLOCKED["status"]     
    
    assert result[0].title == VALID_TASK_TODO["title"]
    assert result[1].title == VALID_TASK_IN_PROGRESS["title"]
    assert result[2].title == VALID_TASK_BLOCKED["title"]

    result_statuses = {t.status for t in result}
    assert VALID_TASK_COMPLETED["status"] not in result_statuses

# UNI-002/013
@patch("backend.src.services.task.SessionLocal")
def test_list_tasks_by_project(mock_session_local):
    """List parent tasks for a specific project with subtasks loaded"""
    from backend.src.services import task as task_service
    
    mock_session = MagicMock()
    mock_session_local.return_value.__enter__.return_value = mock_session

    mock_task_project_10_1 = MagicMock()
    mock_task_project_10_1.id = VALID_DEFAULT_TASK["id"]
    mock_task_project_10_1.title = VALID_DEFAULT_TASK["title"]
    mock_task_project_10_1.project_id = VALID_DEFAULT_TASK["project_id"]
    mock_task_project_10_1.status = VALID_DEFAULT_TASK["status"]
    mock_task_project_10_1.active = True

    mock_task_project_10_2 = MagicMock()
    mock_task_project_10_2.id = VALID_TASK_EXPLICIT_PRIORITY["id"]
    mock_task_project_10_2.title = VALID_TASK_EXPLICIT_PRIORITY["title"]
    mock_task_project_10_2.project_id = VALID_TASK_EXPLICIT_PRIORITY["project_id"]
    mock_task_project_10_2.status = VALID_TASK_EXPLICIT_PRIORITY["status"]
    mock_task_project_10_2.active = True

    mock_task_project_20 = MagicMock()
    mock_task_project_20.id = VALID_TASK_FULL["id"]
    mock_task_project_20.title = VALID_TASK_FULL["title"]
    mock_task_project_20.project_id = VALID_TASK_FULL["project_id"]
    mock_task_project_20.status = VALID_TASK_FULL["status"]
    mock_task_project_20.active = True

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [mock_task_project_10_1, mock_task_project_10_2]
    mock_session.execute.return_value = mock_result
    
    result = task_service.list_tasks_by_project(project_id=VALID_PROJECT_ID)

    mock_session.execute.assert_called_once()
    executed_stmt = mock_session.execute.call_args[0][0]
    compiled = executed_stmt.compile(dialect=sqlite.dialect(), compile_kwargs={"literal_binds": True})
    sql_text = str(compiled).lower()
    
    assert "project_id" in sql_text and f"{VALID_PROJECT_ID}" in sql_text, f"Project ID filter not found in SQL: {sql_text}"
    assert "not (exists" in sql_text or "not exists" in sql_text or "not in" in sql_text, f"Parent-only filter not found in SQL: {sql_text}"

    assert len(result) == 2
    project_ids = {t.project_id for t in result}
    assert VALID_PROJECT_ID in project_ids
    assert 20 not in project_ids
    
    result_titles = {t.title for t in result}
    assert VALID_DEFAULT_TASK["title"] in result_titles
    assert VALID_TASK_EXPLICIT_PRIORITY["title"] in result_titles
    assert VALID_TASK_FULL["title"] not in result_titles

# UNI-002/014
@patch("backend.src.services.task.SessionLocal")
def test_list_tasks_by_empty_project(mock_session_local):
    """List tasks by project returns empty list when project has no tasks"""
    from backend.src.services import task as task_service
    
    mock_session = MagicMock()
    mock_session_local.return_value.__enter__.return_value = mock_session
    
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_session.execute.return_value = mock_result
    
    result = task_service.list_tasks_by_project(project_id=EMPTY_PROJECT_ID)

    mock_session.execute.assert_called_once()
    executed_stmt = mock_session.execute.call_args[0][0]
    compiled = executed_stmt.compile(dialect=sqlite.dialect(), compile_kwargs={"literal_binds": True})
    sql_text = str(compiled).lower()
    
    assert "project_id" in sql_text and f"{EMPTY_PROJECT_ID}" in sql_text, f"Project ID filter not found in SQL: {sql_text}"
    
    # Verify empty list is returned
    assert len(result) == 0
    assert result == []

# UNI-002/015
@patch("backend.src.services.task.SessionLocal")
def test_list_tasks_by_project_default_exclude_inactive(mock_session_local):
    """List tasks by project excludes inactive tasks by default"""
    from backend.src.services import task as task_service
    
    mock_session = MagicMock()
    mock_session_local.return_value.__enter__.return_value = mock_session

    mock_task_in_target_project = MagicMock()
    mock_task_in_target_project.id = VALID_TASK_EXPLICIT_PRIORITY["id"]
    mock_task_in_target_project.title = VALID_TASK_EXPLICIT_PRIORITY["title"]
    mock_task_in_target_project.project_id = VALID_TASK_EXPLICIT_PRIORITY["project_id"]
    mock_task_in_target_project.status = VALID_TASK_EXPLICIT_PRIORITY["status"]
    mock_task_in_target_project.active = True

    mock_task_other_project1 = MagicMock()
    mock_task_other_project1.id = VALID_DEFAULT_TASK["id"]
    mock_task_other_project1.title = VALID_DEFAULT_TASK["title"]
    mock_task_other_project1.project_id = VALID_DEFAULT_TASK["project_id"] 
    mock_task_other_project1.status = VALID_DEFAULT_TASK["status"]
    mock_task_other_project1.active = True

    mock_task_other_project2 = MagicMock()
    mock_task_other_project2.id = VALID_TASK_FULL["id"]
    mock_task_other_project2.title = VALID_TASK_FULL["title"]
    mock_task_other_project2.project_id = VALID_TASK_FULL["project_id"] 
    mock_task_other_project2.status = VALID_TASK_FULL["status"]
    mock_task_other_project2.active = True

    mock_inactive_task = MagicMock()
    mock_inactive_task.id = INACTIVE_TASK["id"]
    mock_inactive_task.title = INACTIVE_TASK["title"]
    mock_inactive_task.project_id = INACTIVE_TASK["project_id"] 
    mock_inactive_task.status = INACTIVE_TASK["status"]
    mock_inactive_task.active = False

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [mock_task_in_target_project]
    mock_session.execute.return_value = mock_result
    
    result = task_service.list_tasks_by_project(project_id=VALID_PROJECT_ID_INACTIVE_TASK)

    mock_session.execute.assert_called_once()
    executed_stmt = mock_session.execute.call_args[0][0]
    compiled = executed_stmt.compile(dialect=sqlite.dialect(), compile_kwargs={"literal_binds": True})
    sql_text = str(compiled).lower()
    
    assert "project_id" in sql_text and f"{VALID_PROJECT_ID_INACTIVE_TASK}" in sql_text, f"Project ID filter not found in SQL: {sql_text}"
    assert "active" in sql_text and ("true" in sql_text or "1" in sql_text), f"Active filter not found in SQL: {sql_text}"

    assert len(result) == 1
    assert result[0].active == True
    assert result[0].title == VALID_TASK_EXPLICIT_PRIORITY["title"]
    assert result[0].project_id == VALID_TASK_EXPLICIT_PRIORITY["project_id"]

# UNI-002/016
@patch("backend.src.services.task.SessionLocal")
def test_list_tasks_by_project_include_inactive(mock_session_local):
    """List tasks by project includes inactive tasks when active_only=False"""
    from backend.src.services import task as task_service
    
    mock_session = MagicMock()
    mock_session_local.return_value.__enter__.return_value = mock_session

    mock_task_in_target_project = MagicMock()
    mock_task_in_target_project.id = VALID_TASK_EXPLICIT_PRIORITY["id"]
    mock_task_in_target_project.title = VALID_TASK_EXPLICIT_PRIORITY["title"]
    mock_task_in_target_project.project_id = VALID_TASK_EXPLICIT_PRIORITY["project_id"]
    mock_task_in_target_project.status = VALID_TASK_EXPLICIT_PRIORITY["status"]
    mock_task_in_target_project.active = True

    mock_task_other_project1 = MagicMock()
    mock_task_other_project1.id = VALID_DEFAULT_TASK["id"]
    mock_task_other_project1.title = VALID_DEFAULT_TASK["title"]
    mock_task_other_project1.project_id = VALID_DEFAULT_TASK["project_id"]
    mock_task_other_project1.status = VALID_DEFAULT_TASK["status"]
    mock_task_other_project1.active = True

    mock_task_other_project2 = MagicMock()
    mock_task_other_project2.id = VALID_TASK_FULL["id"]
    mock_task_other_project2.title = VALID_TASK_FULL["title"]
    mock_task_other_project2.project_id = VALID_TASK_FULL["project_id"]
    mock_task_other_project2.status = VALID_TASK_FULL["status"]
    mock_task_other_project2.active = True

    mock_inactive_task = MagicMock()
    mock_inactive_task.id = INACTIVE_TASK["id"]
    mock_inactive_task.title = INACTIVE_TASK["title"]
    mock_inactive_task.project_id = INACTIVE_TASK["project_id"]
    mock_inactive_task.status = INACTIVE_TASK["status"]
    mock_inactive_task.active = False

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [mock_task_in_target_project, mock_inactive_task]
    mock_session.execute.return_value = mock_result
    
    result = task_service.list_tasks_by_project(project_id=VALID_PROJECT_ID_INACTIVE_TASK, active_only=False)
    
    mock_session.execute.assert_called_once()
    executed_stmt = mock_session.execute.call_args[0][0]
    compiled = executed_stmt.compile(dialect=sqlite.dialect(), compile_kwargs={"literal_binds": True})
    sql_text = str(compiled).lower()
    
    assert "project_id" in sql_text and f"{VALID_PROJECT_ID_INACTIVE_TASK}" in sql_text, f"Project ID filter not found in SQL: {sql_text}"
    assert not ("task.active is" in sql_text), f"Active filter should not be present when active_only=False: {sql_text}"
    
    assert len(result) == 2
    titles = {t.title for t in result}
    assert VALID_TASK_EXPLICIT_PRIORITY["title"] in titles
    assert INACTIVE_TASK["title"] in titles
    
    active_statuses = {t.active for t in result}
    assert True in active_statuses
    assert False in active_statuses

# UNI-002/017
@patch("backend.src.services.task.SessionLocal")
def test_get_task_by_id(mock_session_local):
    """Get task by ID returns task"""
    from backend.src.services import task as task_service
    
    mock_session = MagicMock()
    mock_session_local.return_value.__enter__.return_value = mock_session
    
    mock_task = MagicMock()
    mock_task.id = VALID_DEFAULT_TASK["id"]
    mock_task.title = VALID_DEFAULT_TASK["title"]
    mock_task.status = VALID_DEFAULT_TASK["status"]
    mock_task.priority = VALID_DEFAULT_TASK["priority"]
    mock_task.project_id = VALID_DEFAULT_TASK["project_id"]
    mock_task.active = VALID_DEFAULT_TASK["active"]
    
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_task
    mock_session.execute.return_value = mock_result
    
    result = task_service.get_task_with_subtasks(VALID_DEFAULT_TASK["id"])
    
    mock_session.execute.assert_called_once()
    executed_stmt = mock_session.execute.call_args[0][0]
    compiled = executed_stmt.compile(dialect=sqlite.dialect(), compile_kwargs={"literal_binds": True})
    sql_text = str(compiled).lower()
    
    task_id_str = str(VALID_DEFAULT_TASK["id"])
    assert "id" in sql_text and task_id_str in sql_text, f"Task ID filter not found in SQL: {sql_text}"
    
    assert result is not None
    assert result.id == VALID_DEFAULT_TASK["id"]
    assert result.title == VALID_DEFAULT_TASK["title"]
    assert result.status == VALID_DEFAULT_TASK["status"]
    assert result.priority == VALID_DEFAULT_TASK["priority"]
    assert result.project_id == VALID_DEFAULT_TASK["project_id"]
    assert result.active == VALID_DEFAULT_TASK["active"]

# UNI-002/018
@patch("backend.src.services.task.SessionLocal")
def test_get_task_by_invalid_id(mock_session_local):
    """Get task by invalid ID returns None"""
    from backend.src.services import task as task_service
    
    mock_session = MagicMock()
    mock_session_local.return_value.__enter__.return_value = mock_session
    
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result
    
    result = task_service.get_task_with_subtasks(INVALID_TASK_ID_NONEXISTENT)
    
    mock_session.execute.assert_called_once()
    executed_stmt = mock_session.execute.call_args[0][0]
    compiled = executed_stmt.compile(dialect=sqlite.dialect(), compile_kwargs={"literal_binds": True})
    sql_text = str(compiled).lower()
    
    invalid_id_str = str(INVALID_TASK_ID_NONEXISTENT)
    assert "id" in sql_text and invalid_id_str in sql_text, f"Task ID filter not found in SQL: {sql_text}"
    
    assert result is None

# UNI-002/019
@pytest.mark.parametrize("invalid_id", INVALID_TASK_ID_TYPE)
@patch("backend.src.services.task.SessionLocal")
def test_get_task_by_invalid_id_type(mock_session_local, invalid_id):
    """Get task by invalid ID type raises TypeError"""
    from backend.src.services import task as task_service
    
    mock_session = MagicMock()
    mock_session_local.return_value.__enter__.return_value = mock_session
    
    with pytest.raises(TypeError):
        task_service.get_task_with_subtasks(invalid_id)