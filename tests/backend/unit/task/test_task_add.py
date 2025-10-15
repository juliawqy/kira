# tests/backend/unit/task/test_task_add.py
import pytest
from unittest.mock import patch, MagicMock
from tests.mock_data.task.unit_data import (
    VALID_DEFAULT_TASK,
    VALID_TASK_EXPLICIT_PRIORITY,
    VALID_TASK_FULL,
    VALID_CREATE_PAYLOAD_MINIMAL,
    VALID_CREATE_PAYLOAD_WITH_EXPLICIT_PRIORITY,
    VALID_CREATE_PAYLOAD_FULL,
    INVALID_PRIORITIES,
    INVALID_PRIORITY_VALUES,
    INVALID_PRIORITY_TYPES,
    INVALID_STATUSES,
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
        recurring=0,
        project_id=VALID_CREATE_PAYLOAD_MINIMAL["project_id"],
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
        status=TaskStatus.TO_DO.value,
        priority=8,  
        recurring=0,       
        project_id=VALID_CREATE_PAYLOAD_WITH_EXPLICIT_PRIORITY["project_id"],
        active=True,        
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
        recurring=VALID_CREATE_PAYLOAD_FULL["recurring"],
        project_id=VALID_CREATE_PAYLOAD_FULL["project_id"],
        active=VALID_CREATE_PAYLOAD_FULL["active"]
    )

    assert result == mock_task

    mock_session.add.assert_called_with(mock_task)
    mock_session.flush.assert_called()

# UNI-001/004
@pytest.mark.parametrize("bad_priority", INVALID_PRIORITY_VALUES)
def test_add_task_with_invalid_priority_value_raises_value_error(bad_priority: int):
    """Reject invalid priority values (allowed: 1..10, but wrong values like -1, 0, 11, 999)."""
    from backend.src.services import task as task_service
    
    invalid_payload = {
        **VALID_CREATE_PAYLOAD_MINIMAL,
        "priority": bad_priority
    }
    
    with pytest.raises(ValueError) as exc:
        task_service.add_task(**invalid_payload)
    assert "priority must be between 1 and 10" in str(exc.value)

# UNI-001/005
@pytest.mark.parametrize("bad_priority", INVALID_PRIORITY_TYPES)
def test_add_task_with_invalid_priority_type_raises_type_error(bad_priority):
    """Reject invalid priority types (strings, None, floats, lists, etc.)."""
    from backend.src.services import task as task_service
    
    invalid_payload = {
        **VALID_CREATE_PAYLOAD_MINIMAL,
        "priority": bad_priority
    }
    
    with pytest.raises(TypeError) as exc:
        task_service.add_task(**invalid_payload)
    assert "priority must be an integer" in str(exc.value)

# UNI-001/006
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

