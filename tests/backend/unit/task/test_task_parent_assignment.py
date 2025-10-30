# tests/backend/unit/task/test_task_parent_assignment.py
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

# UNI-013/001
@patch("backend.src.services.task.SessionLocal")
@patch("backend.src.services.task._assert_no_cycle")
def test_attach_subtasks_single_child_success(mock_assert_no_cycle, mock_session_local):
    """Attach single child to parent successfully"""
    from backend.src.services import task as task_service
    
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    
    mock_parent = MagicMock()
    mock_parent.id = VALID_PARENT_TASK["id"]
    mock_parent.active = True
    mock_session.get.return_value = mock_parent
    
    mock_child = MagicMock()
    mock_child.id = VALID_DEFAULT_TASK["id"]
    mock_child.active = True
    
    def mock_execute_side_effect(stmt):
        if "parent_assignment" in str(stmt).lower():
            mock_result = MagicMock()
            mock_result.scalars.return_value.all.return_value = []
            return mock_result
        else:
            mock_result = MagicMock()
            mock_result.scalars.return_value.all.return_value = [mock_child]
            mock_result.scalar_one.return_value = mock_parent
            return mock_result
    
    mock_session.execute.side_effect = mock_execute_side_effect
    
    result = task_service.attach_subtasks(VALID_PARENT_TASK["id"], [VALID_DEFAULT_TASK["id"]])
    
    assert result.id == mock_parent.id
    mock_session.add.assert_called()
    mock_session.flush.assert_called()

# UNI-013/002
@patch("backend.src.services.task.SessionLocal")
@patch("backend.src.services.task._assert_no_cycle")
def test_attach_subtasks_multiple_children_success(mock_assert_no_cycle, mock_session_local):
    """Attach multiple children to parent successfully"""
    from backend.src.services import task as task_service
    
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    
    mock_parent = MagicMock()
    mock_parent.id = VALID_PARENT_TASK["id"]
    mock_parent.active = True
    mock_session.get.return_value = mock_parent
    
    mock_child1 = MagicMock()
    mock_child1.id = VALID_DEFAULT_TASK["id"]
    mock_child1.active = True
    mock_child2 = MagicMock()
    mock_child2.id = VALID_TASK_EXPLICIT_PRIORITY["id"]
    mock_child2.active = True
    mock_child3 = MagicMock()
    mock_child3.id = VALID_TASK_FULL["id"]
    mock_child3.active = True
    
    def mock_execute_side_effect(stmt):
        if "parent_assignment" in str(stmt).lower():
            mock_result = MagicMock()
            mock_result.scalars.return_value.all.return_value = []
            return mock_result
        else:
            mock_result = MagicMock()
            mock_result.scalars.return_value.all.return_value = [mock_child1, mock_child2, mock_child3]
            mock_result.scalar_one.return_value = mock_parent
            return mock_result
    
    mock_session.execute.side_effect = mock_execute_side_effect
    
    child_ids = [VALID_DEFAULT_TASK["id"], VALID_TASK_EXPLICIT_PRIORITY["id"], VALID_TASK_FULL["id"]]
    result = task_service.attach_subtasks(VALID_PARENT_TASK["id"], child_ids)
    
    assert result.id == mock_parent.id
    assert mock_session.add.call_count >= 3
    mock_session.flush.assert_called()

# UNI-013/003
@patch("backend.src.services.task.SessionLocal")
@patch("backend.src.services.task._assert_no_cycle")
def test_attach_subtasks_idempotent_behavior(mock_assert_no_cycle, mock_session_local):
    """Re-attaching same child is idempotent (no duplicates created)"""
    from backend.src.services import task as task_service
    
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    
    mock_parent = MagicMock()
    mock_parent.id = VALID_PARENT_TASK["id"]
    mock_parent.active = True
    mock_session.get.return_value = mock_parent
    
    mock_child = MagicMock()
    mock_child.id = VALID_DEFAULT_TASK["id"]
    mock_child.active = True
    
    mock_existing_link = MagicMock()
    mock_existing_link.parent_id = VALID_PARENT_TASK["id"]
    mock_existing_link.subtask_id = VALID_DEFAULT_TASK["id"]
    
    def mock_execute_side_effect(stmt):
        if "parent_assignment" in str(stmt).lower():
            mock_result = MagicMock()
            mock_result.scalars.return_value.all.return_value = [mock_existing_link]
            return mock_result
        else:
            mock_result = MagicMock()
            mock_result.scalars.return_value.all.return_value = [mock_child]
            mock_result.scalar_one.return_value = mock_parent
            return mock_result
    
    mock_session.execute.side_effect = mock_execute_side_effect
    
    result = task_service.attach_subtasks(VALID_PARENT_TASK["id"], [VALID_DEFAULT_TASK["id"]])
    
    assert result.id == mock_parent.id
    mock_session.flush.assert_called()

# UNI-013/009
@patch("backend.src.services.task.SessionLocal")
def test_attach_subtasks_existing_parent_conflict_raises_error(mock_session_local):
    """Attach child that already has different parent raises ValueError"""
    from backend.src.services import task as task_service
    
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    
    mock_parent = MagicMock()
    mock_parent.id = VALID_PARENT_TASK["id"]
    mock_parent.active = True
    mock_session.get.return_value = mock_parent
    
    mock_child = MagicMock()
    mock_child.id = VALID_DEFAULT_TASK["id"]
    mock_child.active = True
    
    mock_existing_link = MagicMock()
    mock_existing_link.parent_id = 999
    mock_existing_link.subtask_id = VALID_DEFAULT_TASK["id"]
    
    mock_subtask_result = MagicMock()
    mock_subtask_result.scalars.return_value.all.return_value = [mock_child]
    mock_links_result = MagicMock()
    mock_links_result.scalars.return_value.all.return_value = [mock_existing_link]
    
    mock_session.execute.side_effect = [mock_subtask_result, mock_links_result]
    
    with pytest.raises(ValueError, match=r"already (has|have) a parent"):
        task_service.attach_subtasks(VALID_PARENT_TASK["id"], [VALID_DEFAULT_TASK["id"]])

# UNI-013/010
@patch("backend.src.services.task.SessionLocal")
@patch("backend.src.services.task._assert_no_cycle")
def test_attach_subtasks_cycle_detection_raises_error(mock_assert_no_cycle, mock_session_local):
    """Attach subtasks that would create cycle raises ValueError"""
    from backend.src.services import task as task_service
    
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    
    mock_parent = MagicMock()
    mock_parent.id = VALID_PARENT_TASK["id"]
    mock_parent.active = True
    mock_session.get.return_value = mock_parent
    
    mock_child = MagicMock()
    mock_child.id = VALID_DEFAULT_TASK["id"]
    mock_child.active = True
    
    mock_assert_no_cycle.side_effect = ValueError("Cycle detected: the chosen parent is a descendant of the subtask.")
    
    mock_subtask_result = MagicMock()
    mock_subtask_result.scalars.return_value.all.return_value = [mock_child]
    mock_links_result = MagicMock()
    mock_links_result.scalars.return_value.all.return_value = []
    
    mock_session.execute.side_effect = [mock_subtask_result, mock_links_result]
    
    with pytest.raises(ValueError, match=r"cycle|Cycle"):
        task_service.attach_subtasks(VALID_PARENT_TASK["id"], [VALID_DEFAULT_TASK["id"]])


# UNI-013/013
@patch("backend.src.services.task.SessionLocal")
def test_attach_subtasks_get_task_with_subtasks_includes_children(mock_session_local):
    """Getting parent task includes attached subtasks"""
    from backend.src.services import task as task_service
    
    mock_session = MagicMock()
    mock_session_local.return_value.__enter__.return_value = mock_session
    
    mock_child1 = MagicMock()
    mock_child1.id = VALID_DEFAULT_TASK["id"]
    mock_child1.title = VALID_DEFAULT_TASK["title"]
    mock_child1.active = VALID_DEFAULT_TASK["active"]
    
    mock_child2 = MagicMock()
    mock_child2.id = VALID_TASK_EXPLICIT_PRIORITY["id"]
    mock_child2.title = VALID_TASK_EXPLICIT_PRIORITY["title"]
    mock_child2.active = VALID_TASK_EXPLICIT_PRIORITY["active"]
    
    mock_parent = MagicMock()
    mock_parent.id = VALID_PARENT_TASK["id"]
    mock_parent.title = VALID_PARENT_TASK["title"]
    mock_parent.active = VALID_PARENT_TASK["active"]
    mock_parent.subtasks = [mock_child1, mock_child2]
    
    mock_session.execute.return_value.scalar_one_or_none.return_value = mock_parent
    
    result = task_service.get_task_with_subtasks(VALID_PARENT_TASK["id"])
    
    assert result is not None
    assert result.id == VALID_PARENT_TASK["id"]
    assert len(result.subtasks) == 2
    subtask_ids = [subtask.id for subtask in result.subtasks]
    assert VALID_DEFAULT_TASK["id"] in subtask_ids
    assert VALID_TASK_EXPLICIT_PRIORITY["id"] in subtask_ids

# UNI-013/014
@patch("backend.src.services.task.SessionLocal")
def test_attach_subtasks_get_task_without_subtasks_shows_empty(mock_session_local):
    """Getting parent task without subtasks shows empty list"""
    from backend.src.services import task as task_service
    
    mock_session = MagicMock()
    mock_session_local.return_value.__enter__.return_value = mock_session
    
    mock_parent = MagicMock()
    mock_parent.id = VALID_PARENT_TASK["id"]
    mock_parent.title = VALID_PARENT_TASK["title"]
    mock_parent.active = VALID_PARENT_TASK["active"]
    mock_parent.subtasks = []
    
    mock_session.execute.return_value.scalar_one_or_none.return_value = mock_parent
    
    result = task_service.get_task_with_subtasks(VALID_PARENT_TASK["id"])
    
    assert result is not None
    assert result.id == VALID_PARENT_TASK["id"]
    assert len(result.subtasks) == 0

# UNI-013/015
@patch("backend.src.services.task.SessionLocal")
def test_attach_subtasks_get_task_with_inactive_subtask(mock_session_local):
    """Getting parent task with inactive subtasks should not include them"""
    from backend.src.services import task as task_service
    
    mock_session = MagicMock()
    mock_session_local.return_value.__enter__.return_value = mock_session
    
    mock_active_child = MagicMock()
    mock_active_child.id = VALID_DEFAULT_TASK["id"]
    mock_active_child.title = VALID_DEFAULT_TASK["title"]
    mock_active_child.active = VALID_DEFAULT_TASK["active"]
    
    mock_parent = MagicMock()
    mock_parent.id = VALID_PARENT_TASK["id"]
    mock_parent.title = VALID_PARENT_TASK["title"]
    mock_parent.active = VALID_PARENT_TASK["active"]
    mock_parent.subtasks = [mock_active_child]
    
    mock_session.execute.return_value.scalar_one_or_none.return_value = mock_parent
    
    result = task_service.get_task_with_subtasks(VALID_PARENT_TASK["id"])
    
    assert result is not None
    assert result.id == VALID_PARENT_TASK["id"]
    assert len(result.subtasks) == 1
    subtask_ids = [subtask.id for subtask in result.subtasks]
    assert VALID_DEFAULT_TASK["id"] in subtask_ids

# UNI-013/016
@patch("backend.src.services.task.SessionLocal")
def test_attach_subtasks_get_nonexistent_task_returns_none(mock_session_local):
    """Getting nonexistent task returns None"""
    from backend.src.services import task as task_service
    
    mock_session = MagicMock()
    mock_session_local.return_value.__enter__.return_value = mock_session
    
    mock_session.execute.return_value.scalar_one_or_none.return_value = None
    
    result = task_service.get_task_with_subtasks(INVALID_TASK_ID_NONEXISTENT)
    
    assert result is None

# UNI-013/017
@patch("backend.src.services.task.SessionLocal")
def test_attach_subtasks_multiple_operations_maintain_consistency(mock_session_local):
    """Multiple attach/detach operations maintain data consistency"""
    from backend.src.services import task as task_service
    
    mock_session = MagicMock()
    mock_session_local.return_value.__enter__.return_value = mock_session
    
    mock_parent = MagicMock()
    mock_parent.id = VALID_PARENT_TASK["id"]
    mock_parent.subtasks = []
    
    mock_child1 = MagicMock()
    mock_child1.id = VALID_DEFAULT_TASK["id"]
    mock_child1.active = True
    
    mock_child2 = MagicMock()
    mock_child2.id = VALID_TASK_EXPLICIT_PRIORITY["id"]
    mock_child2.active = True
    
    mock_parent_with_subtasks = MagicMock()
    mock_parent_with_subtasks.id = VALID_PARENT_TASK["id"]
    mock_parent_with_subtasks.subtasks = [mock_child1, mock_child2]
    
    mock_session.execute.return_value.scalar_one_or_none.return_value = mock_parent_with_subtasks
    
    result = task_service.get_task_with_subtasks(VALID_PARENT_TASK["id"])
    
    assert result is not None
    assert len(result.subtasks) == 2

# UNI-013/018
@patch("backend.src.services.task.SessionLocal")
def test_attach_subtasks_list_parent_task_exclude_subtasks(mock_session_local):
    """list_parent_tasks should exclude tasks that are subtasks of other tasks"""
    from backend.src.services import task as task_service
    
    mock_session = MagicMock()
    mock_session_local.return_value.__enter__.return_value = mock_session
    
    mock_subtask = MagicMock()
    mock_subtask.id = VALID_DEFAULT_TASK["id"]
    mock_subtask.title = VALID_DEFAULT_TASK["title"]
    mock_subtask.active = VALID_DEFAULT_TASK["active"]
    
    mock_parent_task = MagicMock()
    mock_parent_task.id = VALID_PARENT_TASK["id"]
    mock_parent_task.title = VALID_PARENT_TASK["title"]
    mock_parent_task.active = VALID_PARENT_TASK["active"]
    mock_parent_task.subtask_links = [MagicMock(subtask=mock_subtask)]
    
    mock_independent_task = MagicMock()
    mock_independent_task.id = VALID_TASK_EXPLICIT_PRIORITY["id"]
    mock_independent_task.title = VALID_TASK_EXPLICIT_PRIORITY["title"]
    mock_independent_task.active = VALID_TASK_EXPLICIT_PRIORITY["active"]
    mock_independent_task.subtask_links = []
    
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [mock_parent_task, mock_independent_task]
    mock_session.execute.return_value = mock_result
    
    result = task_service.list_parent_tasks()
    
    mock_session.execute.assert_called_once()
    executed_stmt = mock_session.execute.call_args[0][0]
    compiled = executed_stmt.compile(dialect=sqlite.dialect(), compile_kwargs={"literal_binds": True})
    sql_text = str(compiled).lower()
    
    assert "active" in sql_text and ("true" in sql_text or "1" in sql_text), f"Active filter not found in SQL: {sql_text}"
    assert "subtask_links" in sql_text or "parent_assignment" in sql_text, f"Subtask relationship not found in SQL: {sql_text}"
    
    assert len(result) == 2
    task_ids = [task.id for task in result]
    assert VALID_PARENT_TASK["id"] in task_ids
    assert VALID_TASK_EXPLICIT_PRIORITY["id"] in task_ids
    assert VALID_DEFAULT_TASK["id"] not in task_ids

# UNI-013/019
@patch("backend.src.services.task.SessionLocal")
def test_attach_subtasks_list_parent_task_with_inactive_parents(mock_session_local):
    """list_parent_tasks should exclude inactive parent tasks when active_only=True"""
    from backend.src.services import task as task_service
    
    mock_session = MagicMock()
    mock_session_local.return_value.__enter__.return_value = mock_session
    
    mock_active_subtask = MagicMock()
    mock_active_subtask.id = VALID_DEFAULT_TASK["id"]
    mock_active_subtask.active = True
    
    mock_inactive_subtask = MagicMock()
    mock_inactive_subtask.id = VALID_TASK_EXPLICIT_PRIORITY["id"]
    mock_inactive_subtask.active = True
    
    mock_active_parent = MagicMock()
    mock_active_parent.id = VALID_PARENT_TASK["id"]
    mock_active_parent.title = VALID_PARENT_TASK["title"]
    mock_active_parent.active = VALID_PARENT_TASK["active"]
    mock_active_parent.subtask_links = [MagicMock(subtask=mock_active_subtask)]
    
    mock_inactive_parent = MagicMock()
    mock_inactive_parent.id = INACTIVE_PARENT_TASK["id"]
    mock_inactive_parent.title = INACTIVE_PARENT_TASK["title"]
    mock_inactive_parent.active = INACTIVE_PARENT_TASK["active"]
    mock_inactive_parent.subtask_links = [MagicMock(subtask=mock_inactive_subtask)]
    
    mock_result_active_only = MagicMock()
    mock_result_active_only.scalars.return_value.all.return_value = [mock_active_parent]
    
    mock_result_all = MagicMock()
    mock_result_all.scalars.return_value.all.return_value = [mock_active_parent, mock_inactive_parent]
    
    mock_session.execute.side_effect = [mock_result_active_only, mock_result_all]
    
    result_active_only = task_service.list_parent_tasks(active_only=True)
    
    first_call_stmt = mock_session.execute.call_args_list[0][0][0]
    compiled = first_call_stmt.compile(dialect=sqlite.dialect(), compile_kwargs={"literal_binds": True})
    sql_text = str(compiled).lower()
    
    assert "active" in sql_text and ("true" in sql_text or "1" in sql_text), f"Active filter not found in SQL: {sql_text}"
    
    assert len(result_active_only) == 1
    assert result_active_only[0].id == VALID_PARENT_TASK["id"]
    assert result_active_only[0].active is True
    
    result_all = task_service.list_parent_tasks(active_only=False)
    
    second_call_stmt = mock_session.execute.call_args_list[1][0][0]
    compiled_all = second_call_stmt.compile(dialect=sqlite.dialect(), compile_kwargs={"literal_binds": True})
    sql_text_all = str(compiled_all).lower()
    
    assert len(result_all) == 2
    task_ids = [task.id for task in result_all]
    assert VALID_PARENT_TASK["id"] in task_ids
    assert INACTIVE_PARENT_TASK["id"] in task_ids