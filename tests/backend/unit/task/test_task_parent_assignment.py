# tests/backend/unit/task/test_task_attach_detach.py
import pytest
from unittest.mock import patch, MagicMock
from tests.mock_data.task.unit_data import (
    INVALID_CREATE_NONEXISTENT_PARENT,
    INVALID_PARENT_IDS,
    VALID_CREATE_PAYLOAD_MINIMAL,
    VALID_CREATE_PAYLOAD_WITH_PARENT,
    VALID_TASK_TODO,
    VALID_TASK_IN_PROGRESS,
    VALID_TASK_COMPLETED,
    VALID_DEFAULT_TASK,
    VALID_PARENT_TASK,
    INACTIVE_PARENT_TASK,
    MOCK_CHILD_TASKS,
    INVALID_TASK_ID_NONEXISTENT,
)

pytestmark = pytest.mark.unit

# UNI-048/010
@patch("backend.src.services.task.SessionLocal")
@patch("backend.src.services.task._assert_no_cycle")
def test_attach_subtasks_happy_path(mock_assert_no_cycle, mock_session_local):
    """Attach two children; parent returns both."""
    from backend.src.services import task as task_service
    
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    
    # Mock parent task
    mock_parent = MagicMock()
    mock_parent.id = VALID_PARENT_TASK["id"]
    mock_parent.active = True
    mock_session.get.return_value = mock_parent
    
    # Mock child tasks
    mock_child1 = MagicMock()
    mock_child1.id = MOCK_CHILD_TASKS[0]["id"]
    mock_child1.active = True
    mock_child2 = MagicMock()
    mock_child2.id = MOCK_CHILD_TASKS[1]["id"]
    mock_child2.active = True
    
    # Mock session.execute for subtask fetching
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [mock_child1, mock_child2]
    mock_session.execute.return_value = mock_result
    
    # Mock no existing links
    mock_empty_result = MagicMock()
    mock_empty_result.scalars.return_value.all.return_value = []
    
    # Set up multiple execute calls
    mock_session.execute.side_effect = [mock_result, mock_empty_result, mock_parent]
    
    child_ids = [MOCK_CHILD_TASKS[0]["id"], MOCK_CHILD_TASKS[1]["id"]]
    result = task_service.attach_subtasks(VALID_PARENT_TASK["id"], child_ids)
    
    # Verify parent was fetched
    mock_session.get.assert_called_once_with(task_service.Task, VALID_PARENT_TASK["id"])
    
    # Verify cycle check was called for each child
    assert mock_assert_no_cycle.call_count == 2
    
    # Verify parent assignment links were added
    assert mock_session.add.call_count >= 2  # At least the two ParentAssignment objects
    mock_session.flush.assert_called()
    
    assert result == mock_parent

# UNI-048/011
@patch("backend.src.services.task.SessionLocal")
@patch("backend.src.services.task._assert_no_cycle")
def test_attach_subtasks_idempotent(mock_assert_no_cycle, mock_session_local):
    """Re-attaching same child is a no-op (no duplicates)."""
    from backend.src.services import task as task_service
    
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    
    # Mock parent task
    mock_parent = MagicMock()
    mock_parent.id = VALID_PARENT_TASK["id"]
    mock_parent.active = True
    mock_session.get.return_value = mock_parent
    
    # Mock child task
    mock_child = MagicMock()
    mock_child.id = MOCK_CHILD_TASKS[0]["id"]
    mock_child.active = True
    
    # Mock existing link (idempotent case)
    mock_existing_link = MagicMock()
    mock_existing_link.parent_id = VALID_PARENT_TASK["id"]
    mock_existing_link.subtask_id = MOCK_CHILD_TASKS[0]["id"]
    
    # Mock session.execute calls
    mock_subtask_result = MagicMock()
    mock_subtask_result.scalars.return_value.all.return_value = [mock_child]
    
    mock_links_result = MagicMock()
    mock_links_result.scalars.return_value.all.return_value = [mock_existing_link]
    
    mock_session.execute.side_effect = [mock_subtask_result, mock_links_result, mock_parent]
    
    result = task_service.attach_subtasks(VALID_PARENT_TASK["id"], [MOCK_CHILD_TASKS[0]["id"]])
    
    # Verify no new ParentAssignment was added (idempotent)
    # Should only add existing assignments that don't already exist
    mock_session.flush.assert_called()
    assert result == mock_parent

# UNI-048/012
@patch("backend.src.services.task.SessionLocal")
def test_attach_subtasks_parent_not_found(mock_session_local):
    """Missing parent -> ValueError."""
    from backend.src.services import task as task_service
    
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    
    # Mock parent not found
    mock_session.get.return_value = None
    
    with pytest.raises(ValueError, match=r"Parent task .* not found"):
        task_service.attach_subtasks(INVALID_TASK_ID_NONEXISTENT, [MOCK_CHILD_TASKS[0]["id"]])
    
    mock_session.get.assert_called_once_with(task_service.Task, INVALID_TASK_ID_NONEXISTENT)

# UNI-048/013
@patch("backend.src.services.task.SessionLocal")
def test_attach_subtasks_inactive_parent(mock_session_local):
    """Inactive parent cannot accept subtasks."""
    from backend.src.services import task as task_service
    
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    
    # Mock inactive parent
    mock_parent = MagicMock()
    mock_parent.id = INACTIVE_PARENT_TASK["id"]
    mock_parent.active = False
    mock_session.get.return_value = mock_parent
    
    with pytest.raises(ValueError, match=r"inactive"):
        task_service.attach_subtasks(INACTIVE_PARENT_TASK["id"], [MOCK_CHILD_TASKS[0]["id"]])

# UNI-048/014
@patch("backend.src.services.task.SessionLocal")
def test_attach_subtasks_missing_child(mock_session_local):
    """Unknown child id -> ValueError."""
    from backend.src.services import task as task_service
    
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    
    # Mock active parent
    mock_parent = MagicMock()
    mock_parent.id = VALID_PARENT_TASK["id"]
    mock_parent.active = True
    mock_session.get.return_value = mock_parent
    
    # Mock empty subtask result (child not found)
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_session.execute.return_value = mock_result
    
    with pytest.raises(ValueError, match=r"not found"):
        task_service.attach_subtasks(VALID_PARENT_TASK["id"], [INVALID_TASK_ID_NONEXISTENT])

# UNI-048/015
@patch("backend.src.services.task.SessionLocal")
def test_attach_subtasks_inactive_child(mock_session_local):
    """Inactive child cannot be attached."""
    from backend.src.services import task as task_service
    
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    
    # Mock active parent
    mock_parent = MagicMock()
    mock_parent.id = VALID_PARENT_TASK["id"]
    mock_parent.active = True
    mock_session.get.return_value = mock_parent
    
    # Mock inactive child
    mock_child = MagicMock()
    mock_child.id = MOCK_CHILD_TASKS[0]["id"]
    mock_child.active = False
    
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [mock_child]
    mock_session.execute.return_value = mock_result
    
    with pytest.raises(ValueError, match=r"inactive"):
        task_service.attach_subtasks(VALID_PARENT_TASK["id"], [MOCK_CHILD_TASKS[0]["id"]])

# UNI-048/016
@patch("backend.src.services.task.SessionLocal")
def test_attach_subtasks_self_link(mock_session_local):
    """Parent cannot be its own child."""
    from backend.src.services import task as task_service
    
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    
    # Mock parent task
    mock_parent = MagicMock()
    mock_parent.id = VALID_PARENT_TASK["id"]
    mock_parent.active = True
    mock_session.get.return_value = mock_parent
    
    with pytest.raises(ValueError, match=r"own parent"):
        task_service.attach_subtasks(VALID_PARENT_TASK["id"], [VALID_PARENT_TASK["id"]])

# UNI-048/017
@patch("backend.src.services.task.SessionLocal")
def test_attach_subtasks_conflict_existing_parent(mock_session_local):
    """Child already linked to another parent -> conflict."""
    from backend.src.services import task as task_service
    
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    
    # Mock parent task
    mock_parent = MagicMock()
    mock_parent.id = VALID_PARENT_TASK["id"]
    mock_parent.active = True
    mock_session.get.return_value = mock_parent
    
    # Mock child task
    mock_child = MagicMock()
    mock_child.id = MOCK_CHILD_TASKS[0]["id"]
    mock_child.active = True
    
    # Mock existing link to different parent
    mock_existing_link = MagicMock()
    mock_existing_link.parent_id = 999  # Different parent ID
    mock_existing_link.subtask_id = MOCK_CHILD_TASKS[0]["id"]
    
    # Mock session.execute calls
    mock_subtask_result = MagicMock()
    mock_subtask_result.scalars.return_value.all.return_value = [mock_child]
    
    mock_links_result = MagicMock()
    mock_links_result.scalars.return_value.all.return_value = [mock_existing_link]
    
    mock_session.execute.side_effect = [mock_subtask_result, mock_links_result]
    
    with pytest.raises(ValueError, match=r"already (has|have) a parent"):
        task_service.attach_subtasks(VALID_PARENT_TASK["id"], [MOCK_CHILD_TASKS[0]["id"]])

# UNI-048/018
@patch("backend.src.services.task.SessionLocal")
@patch("backend.src.services.task._assert_no_cycle")
def test_attach_subtasks_cycle_detection(mock_assert_no_cycle, mock_session_local):
    """Prevent cycles: A->B exists; attaching B->A should fail."""
    from backend.src.services import task as task_service
    
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    
    # Mock parent task
    mock_parent = MagicMock()
    mock_parent.id = VALID_PARENT_TASK["id"]
    mock_parent.active = True
    mock_session.get.return_value = mock_parent
    
    # Mock child task
    mock_child = MagicMock()
    mock_child.id = MOCK_CHILD_TASKS[0]["id"]
    mock_child.active = True
    
    # Mock cycle detection error
    mock_assert_no_cycle.side_effect = ValueError("Cycle detected: the chosen parent is a descendant of the subtask.")
    
    # Mock successful subtask fetch and no existing links
    mock_subtask_result = MagicMock()
    mock_subtask_result.scalars.return_value.all.return_value = [mock_child]
    
    mock_links_result = MagicMock()
    mock_links_result.scalars.return_value.all.return_value = []
    
    mock_session.execute.side_effect = [mock_subtask_result, mock_links_result]
    
    with pytest.raises(ValueError, match=r"cycle|Cycle"):
        task_service.attach_subtasks(VALID_PARENT_TASK["id"], [MOCK_CHILD_TASKS[0]["id"]])

# UNI-048/019
@patch("backend.src.services.task.SessionLocal")
def test_attach_subtasks_all_or_nothing(mock_session_local):
    """If one id is invalid, none are attached."""
    from backend.src.services import task as task_service
    
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    
    # Mock active parent
    mock_parent = MagicMock()
    mock_parent.id = VALID_PARENT_TASK["id"]
    mock_parent.active = True
    mock_session.get.return_value = mock_parent
    
    # Mock only one child found (missing the invalid ID)
    mock_child = MagicMock()
    mock_child.id = MOCK_CHILD_TASKS[0]["id"]
    mock_child.active = True
    
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [mock_child]  # Only one found
    mock_session.execute.return_value = mock_result
    
    with pytest.raises(ValueError, match=r"not found"):
        task_service.attach_subtasks(VALID_PARENT_TASK["id"], [MOCK_CHILD_TASKS[0]["id"], INVALID_TASK_ID_NONEXISTENT])

# UNI-048/020
@patch("backend.src.services.task.SessionLocal")
def test_detach_subtask_happy(mock_session_local):
    """Detach existing link -> True and link removed."""
    from backend.src.services import task as task_service
    
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    
    # Mock existing link
    mock_link = MagicMock()
    mock_link.parent_id = VALID_PARENT_TASK["id"]
    mock_link.subtask_id = MOCK_CHILD_TASKS[0]["id"]
    
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_link
    mock_session.execute.return_value = mock_result
    
    result = task_service.detach_subtask(VALID_PARENT_TASK["id"], MOCK_CHILD_TASKS[0]["id"])
    
    # Verify link was deleted
    mock_session.delete.assert_called_once_with(mock_link)
    assert result is True

# UNI-048/021
@patch("backend.src.services.task.SessionLocal")
def test_detach_subtask_missing_link(mock_session_local):
    """Missing link -> ValueError."""
    from backend.src.services import task as task_service
    
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    
    # Mock no link found
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result
    
    with pytest.raises(ValueError, match=r"Link not found|not found"):
        task_service.detach_subtask(VALID_PARENT_TASK["id"], MOCK_CHILD_TASKS[0]["id"])

# UNI-048/022
@patch("backend.src.services.task.SessionLocal")
@patch("backend.src.services.task._assert_no_cycle")
def test_attach_subtasks_cycle_detection_long_chain(mock_assert_no_cycle, mock_session_local):
    """A->B, B->C; attaching C->A must be rejected (deep traversal)."""
    from backend.src.services import task as task_service
    
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    
    # Mock parent task
    mock_parent = MagicMock()
    mock_parent.id = VALID_PARENT_TASK["id"]
    mock_parent.active = True
    mock_session.get.return_value = mock_parent
    
    # Mock child task
    mock_child = MagicMock()
    mock_child.id = MOCK_CHILD_TASKS[0]["id"]
    mock_child.active = True
    
    # Mock cycle detection error from deep chain
    mock_assert_no_cycle.side_effect = ValueError("Cycle detected: the chosen parent is a descendant of the subtask.")
    
    # Mock successful subtask fetch and no existing links
    mock_subtask_result = MagicMock()
    mock_subtask_result.scalars.return_value.all.return_value = [mock_child]
    
    mock_links_result = MagicMock()
    mock_links_result.scalars.return_value.all.return_value = []
    
    mock_session.execute.side_effect = [mock_subtask_result, mock_links_result]
    
    with pytest.raises(ValueError, match=r"cycle|Cycle"):
        task_service.attach_subtasks(VALID_PARENT_TASK["id"], [MOCK_CHILD_TASKS[0]["id"]])

# UNI-048/023
@patch("backend.src.services.task.SessionLocal")
def test_attach_subtasks_empty_list_returns_parent(mock_session_local):
    """Attaching empty list returns parent unchanged."""
    from backend.src.services import task as task_service
    
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    
    # Mock parent task
    mock_parent = MagicMock()
    mock_parent.id = VALID_PARENT_TASK["id"]
    mock_parent.active = True
    mock_session.get.return_value = mock_parent
    
    # Mock return for empty case
    mock_session.execute.return_value.scalar_one.return_value = mock_parent
    
    result = task_service.attach_subtasks(VALID_PARENT_TASK["id"], [])
    
    # Verify parent was fetched and returned
    mock_session.get.assert_called_once_with(task_service.Task, VALID_PARENT_TASK["id"])
    assert result == mock_parent



# UNI-004/002
@patch("backend.src.services.task.SessionLocal")
def test_delete_task_removes_parent_assignments(mock_session_local):
    """Delete task with detach_links=True removes all parent-child relationships."""
    from backend.src.services import task as task_service
    
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session

    mock_task = MagicMock()
    mock_task.id = VALID_PARENT_TASK["id"]
    mock_task.active = True
    mock_session.get.return_value = mock_task
    
    mock_query = MagicMock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    
    result = task_service.delete_task(VALID_PARENT_TASK["id"], detach_links=True)

    assert mock_session.query.call_count == 2
    mock_session.query.assert_any_call(task_service.ParentAssignment)

    assert mock_query.filter.call_count == 2
    assert mock_query.delete.call_count == 2
    assert mock_task.active is False
    assert result == mock_task






# UNI-001/003
@patch("backend.src.services.task.SessionLocal")
@patch("backend.src.services.task._assert_no_cycle")  # Mock the cycle check function
def test_add_task_with_parent_links_child_to_parent(mock_assert_no_cycle, mock_session_local):
    """Create child with parent_id; parent links child."""
    from backend.src.services import task as task_service
    
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    
    # Mock parent task exists and is active
    mock_parent = MagicMock()
    mock_parent.id = VALID_PARENT_TASK["id"]
    mock_parent.active = True
    mock_session.get.return_value = mock_parent
    
    # Mock the child task creation
    mock_child = MagicMock()
    mock_child.id = 3
    mock_child.title = VALID_CREATE_PAYLOAD_WITH_PARENT["title"]
    
    with patch("backend.src.services.task.Task", return_value=mock_child):
        with patch("backend.src.services.task.ParentAssignment") as mock_assignment_class:
            result = task_service.add_task(**VALID_CREATE_PAYLOAD_WITH_PARENT)
    
    # Verify parent was fetched
    mock_session.get.assert_called()
    
    # Verify cycle check was called
    mock_assert_no_cycle.assert_called_once()
    
    # Verify child task and assignment were added
    mock_session.add.assert_called()
    mock_session.flush.assert_called()

# UNI-001/004
@patch("backend.src.services.task.SessionLocal")
def test_add_task_with_inactive_parent_raises_value_error(mock_session_local):
    """Reject linking to an inactive parent."""
    from backend.src.services import task as task_service
    
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    
    # Mock inactive parent
    mock_parent = MagicMock()
    mock_parent.id = INACTIVE_PARENT_TASK["id"]
    mock_parent.active = False
    mock_session.get.return_value = mock_parent
    
    with pytest.raises(ValueError) as exc:
        task_service.add_task(**VALID_CREATE_PAYLOAD_WITH_PARENT)
    assert "inactive" in str(exc.value)

# UNI-001/005
@patch("backend.src.services.task.SessionLocal")
def test_add_task_with_nonexistent_parent_raises_value_error(mock_session_local):
    """Reject non-existent parent_id with a helpful error."""
    from backend.src.services import task as task_service
    
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    
    # Mock parent not found
    mock_session.get.return_value = None
    
    with pytest.raises(ValueError) as exc:
        task_service.add_task(**INVALID_CREATE_NONEXISTENT_PARENT)
    assert "not found" in str(exc.value)



# UNI-001/006
@pytest.mark.parametrize("bad_parent", INVALID_PARENT_IDS)
@patch("backend.src.services.task.SessionLocal")
def test_add_task_with_invalid_parent_sentinel_values_raises(mock_session_local, bad_parent: int):
    """Reject impossible parent ids (0/negative)."""
    from backend.src.services import task as task_service
    
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    
    # Mock parent not found for invalid IDs
    mock_session.get.return_value = None
    
    invalid_payload = {
        **VALID_CREATE_PAYLOAD_MINIMAL,
        "parent_id": bad_parent
    }
    
    with pytest.raises(ValueError) as exc:
        task_service.add_task(**invalid_payload)
    assert "not found" in str(exc.value)

# UNI-002/001
@patch("backend.src.services.task.SessionLocal")
def test_get_task_with_subtasks_nonexistent_returns_none(mock_session_local):
    """get_task_with_subtasks returns None for unknown id."""
    from backend.src.services import task as task_service
    
    mock_session = MagicMock()
    mock_session_local.return_value.__enter__.return_value = mock_session
    
    # Mock task not found
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result
    
    result = task_service.get_task_with_subtasks(INVALID_TASK_ID_NONEXISTENT)
    
    assert result is None
    mock_session.execute.assert_called_once()

# UNI-002/002
@patch("backend.src.services.task.SessionLocal")
def test_get_task_with_subtasks_no_children_returns_empty_list(mock_session_local):
    """A leaf task returns an empty subtasks list."""
    from backend.src.services import task as task_service
    
    mock_session = MagicMock()
    mock_session_local.return_value.__enter__.return_value = mock_session
    
    # Mock task with no subtasks
    mock_task = MagicMock()
    mock_task.id = VALID_TASK_TODO["id"]
    mock_task.title = VALID_TASK_TODO["title"]
    mock_task.subtasks = []
    
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_task
    mock_session.execute.return_value = mock_result
    
    result = task_service.get_task_with_subtasks(VALID_TASK_TODO["id"])
    
    assert result is not None
    assert result.title == VALID_TASK_TODO["title"]
    assert result.subtasks == []

# UNI-002/003
@patch("backend.src.services.task.SessionLocal")
def test_get_task_with_subtasks_direct_children_only(mock_session_local):
    """A's subtasks include only B (direct), not grandchild C."""
    from backend.src.services import task as task_service
    
    mock_session = MagicMock()
    mock_session_local.return_value.__enter__.return_value = mock_session
    
    # Mock parent task A with direct child B
    mock_child_b = MagicMock()
    mock_child_b.id = MOCK_CHILD_TASKS[0]["id"]
    mock_child_b.title = MOCK_CHILD_TASKS[0]["title"]
    
    mock_parent_a = MagicMock()
    mock_parent_a.id = VALID_PARENT_TASK["id"]
    mock_parent_a.title = VALID_PARENT_TASK["title"]
    mock_parent_a.subtasks = [mock_child_b]
    
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_parent_a
    mock_session.execute.return_value = mock_result
    
    result = task_service.get_task_with_subtasks(VALID_PARENT_TASK["id"])
    
    assert result is not None
    subtask_titles = [st.title for st in result.subtasks]
    assert subtask_titles == [MOCK_CHILD_TASKS[0]["title"]]
