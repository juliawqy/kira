# tests/backend/unit/task/test_task_parent_unassignment.py
from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.dialects import sqlite

from tests.mock_data.task.unit_data import (
    VALID_DEFAULT_TASK,
    VALID_TASK_EXPLICIT_PRIORITY,
    VALID_TASK_FULL,
    INACTIVE_TASK,
    VALID_PARENT_TASK,
    INACTIVE_PARENT_TASK,
    INVALID_TASK_ID_NONEXISTENT,
)

pytestmark = pytest.mark.unit

# UNI-023/001
@patch("backend.src.services.task.SessionLocal")
def test_detach_subtask_single_child_success(mock_session_local):
    """Detach single child from parent successfully"""
    from backend.src.services import task as task_service
    
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    
    mock_link = MagicMock()
    mock_link.parent_id = VALID_PARENT_TASK["id"]
    mock_link.subtask_id = VALID_DEFAULT_TASK["id"]
    
    mock_session.execute.return_value.scalar_one_or_none.return_value = mock_link
    
    result = task_service.detach_subtask(VALID_PARENT_TASK["id"], VALID_DEFAULT_TASK["id"])
    
    assert result is True
    mock_session.delete.assert_called_once_with(mock_link)

# UNI-023/002
@patch("backend.src.services.task.SessionLocal")
def test_detach_subtasks_multiple_children_success(mock_session_local):
    """Detach multiple children from parent successfully"""
    from backend.src.services import task as task_service
    
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    
    mock_link1 = MagicMock()
    mock_link1.parent_id = VALID_PARENT_TASK["id"]
    mock_link1.subtask_id = VALID_DEFAULT_TASK["id"]
    
    mock_link2 = MagicMock()
    mock_link2.parent_id = VALID_PARENT_TASK["id"]
    mock_link2.subtask_id = VALID_TASK_EXPLICIT_PRIORITY["id"]
    
    mock_link3 = MagicMock()
    mock_link3.parent_id = VALID_PARENT_TASK["id"]
    mock_link3.subtask_id = VALID_TASK_FULL["id"]
    
    mock_session.execute.return_value.scalar_one_or_none.side_effect = [mock_link1, mock_link2, mock_link3]
    
    child_ids = [VALID_DEFAULT_TASK["id"], VALID_TASK_EXPLICIT_PRIORITY["id"], VALID_TASK_FULL["id"]]
    results = []
    for child_id in child_ids:
        result = task_service.detach_subtask(VALID_PARENT_TASK["id"], child_id)
        results.append(result)
    
    assert all(results)
    assert mock_session.delete.call_count == 3

# UNI-023/003
@patch("backend.src.services.task.SessionLocal")
def test_delete_parent_task_with_detach_links_preserves_children(mock_session_local):
    """Delete parent task with detach_links=True removes relationships but preserves child tasks"""
    from backend.src.services import task as task_service
    
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    
    mock_parent_task = MagicMock()
    mock_parent_task.id = VALID_PARENT_TASK["id"]
    mock_parent_task.active = True
    
    mock_session.get.return_value = mock_parent_task
    
    mock_query = MagicMock()
    mock_query.filter.return_value = mock_query
    mock_session.query.return_value = mock_query
    
    result = task_service.delete_task(VALID_PARENT_TASK["id"])
    
    assert mock_session.query.call_count == 2
    assert mock_query.filter.call_count == 2
    assert mock_query.delete.call_count == 2
    assert mock_parent_task.active is False
    assert result == mock_parent_task
    mock_session.add.assert_called_once_with(mock_parent_task)
    mock_session.flush.assert_called_once()

# UNI-023/004
@patch("backend.src.services.task.SessionLocal")
def test_detach_subtask_sql_query_validation(mock_session_local):
    """Verify SQL query structure for detach operation"""
    from backend.src.services import task as task_service
    
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    
    mock_link = MagicMock()
    mock_link.parent_id = VALID_PARENT_TASK["id"]
    mock_link.subtask_id = VALID_DEFAULT_TASK["id"]
    
    mock_session.execute.return_value.scalar_one_or_none.return_value = mock_link
    
    result = task_service.detach_subtask(VALID_PARENT_TASK["id"], VALID_DEFAULT_TASK["id"])
    
    mock_session.execute.assert_called_once()
    executed_stmt = mock_session.execute.call_args[0][0]
    compiled = executed_stmt.compile(dialect=sqlite.dialect(), compile_kwargs={"literal_binds": True})
    sql_text = str(compiled).lower()
    
    assert "parent_assignment" in sql_text
    assert "parent_id" in sql_text
    assert "subtask_id" in sql_text
    assert str(VALID_PARENT_TASK["id"]) in sql_text
    assert str(VALID_DEFAULT_TASK["id"]) in sql_text
    assert result is True

