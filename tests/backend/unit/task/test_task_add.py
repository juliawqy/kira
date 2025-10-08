# tests/backend/unit/task/test_task_add.py
import pytest
from unittest.mock import patch, MagicMock
from tests.mock_data.task.unit_data import (
    VALID_TASK_TODO,
    VALID_TASK_IN_PROGRESS,
    VALID_TASK_COMPLETED,
    VALID_TASK_BLOCKED,
    VALID_DEFAULT_TASK,
    VALID_TASK_EXPLICIT_PRIORITY,
    VALID_TASK_FULL,
    VALID_CREATE_PAYLOAD_MINIMAL,
    VALID_CREATE_PAYLOAD_WITH_EXPLICIT_PRIORITY,
    VALID_CREATE_PAYLOAD_FULL,
    VALID_CREATE_PAYLOAD_WITH_PARENT,
    VALID_PARENT_TASK,
    INACTIVE_PARENT_TASK,
    INVALID_CREATE_NONEXISTENT_PARENT,
    INVALID_PRIORITIES,
    INVALID_STATUSES,
    INVALID_PARENT_IDS,
)
from backend.src.enums.task_status import TaskStatus

pytestmark = pytest.mark.unit

# UNI-001/001
@patch("backend.src.services.task.SessionLocal")
def test_add_task_minimal_uses_default_priority_5(mock_session_local):
    """Create with minimal fields; verify default priority is 5."""
    from backend.src.services import task as task_service
    
    # Mock session context manager
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    
    mock_task = MagicMock()
    mock_task.id = VALID_DEFAULT_TASK["id"]
    
    with patch("backend.src.services.task.Task") as mock_task_class:
        mock_task_class.return_value = mock_task
        result = task_service.add_task(**VALID_CREATE_PAYLOAD_MINIMAL)
    
    mock_task_class.assert_called_once_with(
        title="Default Task",
        description=None,  
        start_date=None,   
        deadline=None,     
        status=TaskStatus.TO_DO.value,  # Should default to TO_DO
        priority=5,        # Should default to 5
        project_id=100,
        active=True,       # Should default to True
    )

    assert result == mock_task
    mock_session.add.assert_called_with(mock_task)
    mock_session.flush.assert_called()

# UNI-001/002
@patch("backend.src.services.task.SessionLocal")
def test_add_task_with_explicit_priority(mock_session_local):
    """Create with explicit priority; verify it's used instead of default."""
    from backend.src.services import task as task_service
    
    # Mock session context manager
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    
    mock_task = MagicMock()
    mock_task.id = VALID_TASK_EXPLICIT_PRIORITY["id"]

    with patch("backend.src.services.task.Task") as mock_task_class:
        mock_task_class.return_value = mock_task
        result = task_service.add_task(**VALID_CREATE_PAYLOAD_WITH_EXPLICIT_PRIORITY)
    
    mock_task_class.assert_called_once_with(
        title="Task with Explicit Priority",
        description=None,   
        start_date=None,    
        deadline=None,      
        status=TaskStatus.TO_DO.value,  # Should default to TO_DO
        priority=8,         # Explicit priority from payload
        project_id=100,
        active=True,        # Should default to True
    )

    assert result == mock_task

    mock_session.add.assert_called_with(mock_task)
    mock_session.flush.assert_called()

# UNI-001/003
@patch("backend.src.services.task.SessionLocal")
def test_add_task_full_fields(mock_session_local):
    """Create with all fields; round-trip values should match."""
    from backend.src.services import task as task_service
    
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session

    mock_task = MagicMock()
    mock_task.id = VALID_TASK_FULL["id"]

    with patch("backend.src.services.task.Task", return_value=mock_task) as mock_task_constructor:
        result = task_service.add_task(**VALID_CREATE_PAYLOAD_FULL)

    mock_task_constructor.assert_called_once_with(
        title=VALID_CREATE_PAYLOAD_FULL["title"],
        description=VALID_CREATE_PAYLOAD_FULL["description"],
        start_date=VALID_CREATE_PAYLOAD_FULL["start_date"],
        deadline=VALID_CREATE_PAYLOAD_FULL["deadline"],
        status=VALID_CREATE_PAYLOAD_FULL["status"],
        priority=VALID_CREATE_PAYLOAD_FULL["priority"],
        project_id=VALID_CREATE_PAYLOAD_FULL["project_id"],
        active=VALID_CREATE_PAYLOAD_FULL["active"]
    )

    assert result == mock_task

    mock_session.add.assert_called_with(mock_task)
    mock_session.flush.assert_called()







# ------------ TO FIX FROM HERE ------------

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
@pytest.mark.parametrize("bad_priority", INVALID_PRIORITIES)
def test_add_task_with_invalid_priority_raises_value_error(bad_priority: int):
    """Reject invalid priority (allowed: 1..10)."""
    from backend.src.services import task as task_service
    
    invalid_payload = {
        **VALID_CREATE_PAYLOAD_MINIMAL,
        "priority": bad_priority
    }
    
    with pytest.raises(ValueError) as exc:
        task_service.add_task(**invalid_payload)
    assert "priority" in str(exc.value) or "between 1 and 10" in str(exc.value)

# UNI-001/007
@pytest.mark.parametrize("bad_status", INVALID_STATUSES)
def test_add_task_with_invalid_status_raises_value_error(bad_status):
    """Reject invalid status (must match allowed strings exactly)."""
    from backend.src.services import task as task_service
    
    invalid_payload = {
        **VALID_CREATE_PAYLOAD_MINIMAL,
        "status": bad_status
    }
    
    with pytest.raises(ValueError) as exc:
        task_service.add_task(**invalid_payload)
    assert "Invalid status" in str(exc.value)

# UNI-001/008
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
