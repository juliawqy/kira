from __future__ import annotations

import pytest
from datetime import date

from backend.src.handlers.task_handler import upcoming_task_reminder, overdue_task_reminder
from backend.src.schemas.email import EmailRecipient


class _TaskObj:
    def __init__(self, *, task_id: int, title: str | None, deadline: date | None, priority: int | None, description: str | None, project_id: int | None):
        self.id = task_id
        self.title = title
        self.deadline = deadline
        self.priority = priority
        self.description = description
        self.project_id = project_id


@pytest.fixture
def reminder_data():
    import importlib.util
    from pathlib import Path
    p = Path(__file__).parents[3] / 'mock_data' / 'notification_email' / 'task_reminder_data.py'
    spec = importlib.util.spec_from_file_location('reminder_mock_data_unit', str(p))
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)  
    return module


@pytest.fixture
def patch_email_settings(monkeypatch):
    monkeypatch.setenv("APP_NAME", "Kira")
    monkeypatch.setenv("APP_URL", "http://localhost:8000")
    monkeypatch.setenv("FASTMAIL_SMTP_HOST", "smtp.test.local")
    monkeypatch.setenv("FASTMAIL_SMTP_PORT", "587")
    monkeypatch.setenv("FASTMAIL_USERNAME", "user")
    monkeypatch.setenv("FASTMAIL_PASSWORD", "pass")
    monkeypatch.setenv("FASTMAIL_FROM_EMAIL", "noreply@test.local")
    monkeypatch.setenv("FASTMAIL_FROM_NAME", "Kira")
    monkeypatch.setenv("USE_TLS", "True")
    monkeypatch.setenv("USE_SSL", "False")
    monkeypatch.setenv("TIMEOUT", "5")

# UNI-029/001 
def test_upcoming_no_deadline_returns_failure(reminder_data, patch_email_settings, monkeypatch):
    from backend.src.services import task as task_service
    task_dict = reminder_data.TASK_WITHOUT_DEADLINE.copy()
    task = _TaskObj(
        task_id=task_dict["id"],
        title=task_dict.get('title'),
        deadline=None,
        priority=task_dict.get('priority'),
        description=task_dict.get('description'),
        project_id=task_dict.get('project_id'),
    )
    monkeypatch.setattr(task_service, 'get_task_with_subtasks', lambda _id: task)

    result = upcoming_task_reminder(task_dict["id"])

    
    assert result["success"] is False
    assert result["message"] == "Task does not have a deadline"
    assert result["recipients_count"] == 0

# UNI-029/002
def test_upcoming_no_recipients_configured_early_return(reminder_data, patch_email_settings, monkeypatch):
    
    from backend.src.services import task as task_service
    from backend.src.services.email import get_email_service
    task_dict = reminder_data.UPCOMING_TASK.copy()
    task = _TaskObj(
        task_id=task_dict["id"],
        title=task_dict.get('title'),
        deadline=date.fromisoformat(task_dict['deadline']),
        priority=task_dict.get('priority'),
        description=task_dict.get('description'),
        project_id=task_dict.get('project_id'),
    )
    monkeypatch.setattr(task_service, 'get_task_with_subtasks', lambda _id: task)
    es = get_email_service()
    monkeypatch.setattr(es, '_get_task_notification_recipients', lambda _tid: [])

    
    result = upcoming_task_reminder(task_dict["id"])

    
    assert result["success"] is True
    assert result["message"] == "No recipients configured for notifications"
    assert result["recipients_count"] == 0

# UNI-029/003
def test_upcoming_project_service_exception_is_silent(reminder_data, patch_email_settings, monkeypatch):
    
    from backend.src.services import task as task_service
    import backend.src.services.project as project_service
    from backend.src.services.email import get_email_service
    task_dict = reminder_data.UPCOMING_TASK.copy()
    task = _TaskObj(
        task_id=task_dict["id"],
        title=task_dict.get('title'),
        deadline=date.fromisoformat(task_dict['deadline']),
        priority=task_dict.get('priority'),
        description=task_dict.get('description'),
        project_id=task_dict.get('project_id'),
    )
    monkeypatch.setattr(task_service, 'get_task_with_subtasks', lambda _id: task)
    es = get_email_service()
    monkeypatch.setattr(es, '_get_task_notification_recipients', lambda _tid: [EmailRecipient(email=reminder_data.SINGLE_ASSIGNEE_WITH_EMAIL[0]["email"], name=reminder_data.SINGLE_ASSIGNEE_WITH_EMAIL[0]["name"])])
    monkeypatch.setattr(project_service, 'get_project_by_id', lambda _pid: (_ for _ in ()).throw(Exception("proj service down")))
    
    monkeypatch.setattr(es, '_send_smtp_message', lambda *args, **kwargs: reminder_data.MOCK_MESSAGE_ID)

    
    result = upcoming_task_reminder(task_dict["id"])

    
    assert result["success"] is True
    assert result["email_id"] == str(reminder_data.MOCK_MESSAGE_ID)

# UNI-029/004 
def test_upcoming_task_not_found(reminder_data, patch_email_settings, monkeypatch):
    """Test upcoming reminder when task is not found."""
    from backend.src.services import task as task_service
    monkeypatch.setattr(task_service, 'get_task_with_subtasks', lambda _id: None)

    result = upcoming_task_reminder(999)

    assert result["success"] is False
    assert result["message"] == "Task not found"
    assert result["recipients_count"] == 0

# UNI-029/005 
def test_upcoming_project_found_with_name(reminder_data, patch_email_settings, monkeypatch):
    """Test upcoming reminder when project is found and has project_name."""
    from backend.src.services import task as task_service
    import backend.src.services.project as project_service
    from backend.src.services.email import get_email_service
    task_dict = reminder_data.UPCOMING_TASK.copy()
    task = _TaskObj(
        task_id=task_dict["id"],
        title=task_dict.get('title'),
        deadline=date.fromisoformat(task_dict['deadline']),
        priority=task_dict.get('priority'),
        description=task_dict.get('description'),
        project_id=task_dict.get('project_id'),
    )
    monkeypatch.setattr(task_service, 'get_task_with_subtasks', lambda _id: task)
    es = get_email_service()
    monkeypatch.setattr(es, '_get_task_notification_recipients', lambda _tid: [EmailRecipient(email=reminder_data.SINGLE_ASSIGNEE_WITH_EMAIL[0]["email"], name=reminder_data.SINGLE_ASSIGNEE_WITH_EMAIL[0]["name"])])
    monkeypatch.setattr(project_service, 'get_project_by_id', lambda _pid: {"project_name": "Test Project"})
    monkeypatch.setattr(es, '_send_smtp_message', lambda *args, **kwargs: reminder_data.MOCK_MESSAGE_ID)

    result = upcoming_task_reminder(task_dict["id"])

    assert result["success"] is True
    assert result["email_id"] == str(reminder_data.MOCK_MESSAGE_ID)


# UNI-029/006 
def test_upcoming_send_failure_message_id_not_one(reminder_data, patch_email_settings, monkeypatch):
    """Test upcoming reminder when send returns message_id != 1."""
    from backend.src.services import task as task_service
    from backend.src.services.email import get_email_service
    task_dict = reminder_data.UPCOMING_TASK.copy()
    task = _TaskObj(
        task_id=task_dict["id"],
        title=task_dict.get('title'),
        deadline=date.fromisoformat(task_dict['deadline']),
        priority=task_dict.get('priority'),
        description=task_dict.get('description'),
        project_id=task_dict.get('project_id'),
    )
    monkeypatch.setattr(task_service, 'get_task_with_subtasks', lambda _id: task)
    es = get_email_service()
    monkeypatch.setattr(es, '_get_task_notification_recipients', lambda _tid: [EmailRecipient(email=reminder_data.SINGLE_ASSIGNEE_WITH_EMAIL[0]["email"], name=reminder_data.SINGLE_ASSIGNEE_WITH_EMAIL[0]["name"])])
    monkeypatch.setattr(es, '_send_smtp_message', lambda *args, **kwargs: 999)

    result = upcoming_task_reminder(task_dict["id"])

    assert result["success"] is False
    assert result["message"] == "Error sending notification"
    assert result["recipients_count"] == 1

# UNI-029/007 
def test_upcoming_exception_caught(reminder_data, patch_email_settings, monkeypatch):
    """Test upcoming reminder when exception occurs in try block."""
    from backend.src.services import task as task_service
    monkeypatch.setattr(task_service, 'get_task_with_subtasks', lambda _id: (_ for _ in ()).throw(Exception("Task service error")))

    result = upcoming_task_reminder(1)

    assert result is None


# UNI-107/001 
def test_overdue_no_deadline_returns_failure(reminder_data, patch_email_settings, monkeypatch):
    from backend.src.services import task as task_service
    task_dict = reminder_data.TASK_WITHOUT_DEADLINE.copy()
    task = _TaskObj(
        task_id=task_dict["id"],
        title=task_dict.get('title'),
        deadline=None,
        priority=task_dict.get('priority'),
        description=task_dict.get('description'),
        project_id=task_dict.get('project_id'),
    )
    monkeypatch.setattr(task_service, 'get_task_with_subtasks', lambda _id: task)

    result = overdue_task_reminder(task_dict["id"])
    assert result["success"] is False
    assert result["message"] == "Task does not have a deadline"
    assert result["recipients_count"] == 0

# UNI-107/002
def test_overdue_no_recipients_configured_early_return(reminder_data, patch_email_settings, monkeypatch):
    from backend.src.services import task as task_service
    from backend.src.services.email import get_email_service
    task_dict = reminder_data.OVERDUE_TASK.copy()
    task = _TaskObj(
        task_id=task_dict["id"],
        title=task_dict.get('title'),
        deadline=date.fromisoformat(task_dict['deadline']),
        priority=task_dict.get('priority'),
        description=task_dict.get('description'),
        project_id=task_dict.get('project_id'),
    )
    monkeypatch.setattr(task_service, 'get_task_with_subtasks', lambda _id: task)
    es = get_email_service()
    monkeypatch.setattr(es, '_get_task_notification_recipients', lambda _tid: [])

    result = overdue_task_reminder(task_dict["id"])
    assert result["success"] is True
    assert result["message"] == "No recipients configured for notifications"
    assert result["recipients_count"] == 0

# UNI-107/003
def test_overdue_project_service_exception_is_silent(reminder_data, patch_email_settings, monkeypatch):
    from backend.src.services import task as task_service
    import backend.src.services.project as project_service
    from backend.src.services.email import get_email_service
    task_dict = reminder_data.OVERDUE_TASK.copy()
    task = _TaskObj(
        task_id=task_dict["id"],
        title=task_dict.get('title'),
        deadline=date.fromisoformat(task_dict['deadline']),
        priority=task_dict.get('priority'),
        description=task_dict.get('description'),
        project_id=task_dict.get('project_id'),
    )
    monkeypatch.setattr(task_service, 'get_task_with_subtasks', lambda _id: task)
    es = get_email_service()
    monkeypatch.setattr(es, '_get_task_notification_recipients', lambda _tid: [EmailRecipient(email=reminder_data.SINGLE_ASSIGNEE_WITH_EMAIL[0]["email"], name=reminder_data.SINGLE_ASSIGNEE_WITH_EMAIL[0]["name"])])
    monkeypatch.setattr(project_service, 'get_project_by_id', lambda _pid: (_ for _ in ()).throw(Exception("proj service down")))
    monkeypatch.setattr(es, '_send_smtp_message', lambda *args, **kwargs: reminder_data.MOCK_MESSAGE_ID)

    result = overdue_task_reminder(task_dict["id"])
    assert result["success"] is True
    assert result["email_id"] == str(reminder_data.MOCK_MESSAGE_ID)

# UNI-107/004 
def test_overdue_task_not_found(reminder_data, patch_email_settings, monkeypatch):
    """Test overdue reminder when task is not found."""
    from backend.src.services import task as task_service
    monkeypatch.setattr(task_service, 'get_task_with_subtasks', lambda _id: None)

    result = overdue_task_reminder(999)

    assert result["success"] is False
    assert result["message"] == "Task not found"
    assert result["recipients_count"] == 0

# UNI-107/005 
def test_overdue_project_found_with_name(reminder_data, patch_email_settings, monkeypatch):
    """Test overdue reminder when project is found and has project_name."""
    from backend.src.services import task as task_service
    import backend.src.services.project as project_service
    from backend.src.services.email import get_email_service
    task_dict = reminder_data.OVERDUE_TASK.copy()
    task = _TaskObj(
        task_id=task_dict["id"],
        title=task_dict.get('title'),
        deadline=date.fromisoformat(task_dict['deadline']),
        priority=task_dict.get('priority'),
        description=task_dict.get('description'),
        project_id=task_dict.get('project_id'),
    )
    monkeypatch.setattr(task_service, 'get_task_with_subtasks', lambda _id: task)
    es = get_email_service()
    monkeypatch.setattr(es, '_get_task_notification_recipients', lambda _tid: [EmailRecipient(email=reminder_data.SINGLE_ASSIGNEE_WITH_EMAIL[0]["email"], name=reminder_data.SINGLE_ASSIGNEE_WITH_EMAIL[0]["name"])])
    monkeypatch.setattr(project_service, 'get_project_by_id', lambda _pid: {"project_name": "Test Project"})
    monkeypatch.setattr(es, '_send_smtp_message', lambda *args, **kwargs: reminder_data.MOCK_MESSAGE_ID)

    result = overdue_task_reminder(task_dict["id"])

    assert result["success"] is True
    assert result["email_id"] == str(reminder_data.MOCK_MESSAGE_ID)


# UNI-107/006 
def test_overdue_send_failure_message_id_not_one(reminder_data, patch_email_settings, monkeypatch):
    """Test overdue reminder when send returns message_id != 1."""
    from backend.src.services import task as task_service
    from backend.src.services.email import get_email_service
    task_dict = reminder_data.OVERDUE_TASK.copy()
    task = _TaskObj(
        task_id=task_dict["id"],
        title=task_dict.get('title'),
        deadline=date.fromisoformat(task_dict['deadline']),
        priority=task_dict.get('priority'),
        description=task_dict.get('description'),
        project_id=task_dict.get('project_id'),
    )
    monkeypatch.setattr(task_service, 'get_task_with_subtasks', lambda _id: task)
    es = get_email_service()
    monkeypatch.setattr(es, '_get_task_notification_recipients', lambda _tid: [EmailRecipient(email=reminder_data.SINGLE_ASSIGNEE_WITH_EMAIL[0]["email"], name=reminder_data.SINGLE_ASSIGNEE_WITH_EMAIL[0]["name"])])
    monkeypatch.setattr(es, '_send_smtp_message', lambda *args, **kwargs: 999)

    result = overdue_task_reminder(task_dict["id"])

    assert result["success"] is False
    assert result["message"] == "Error sending notification"
    assert result["recipients_count"] == 1

# UNI-107/007 
def test_overdue_exception_caught(reminder_data, patch_email_settings, monkeypatch):
    """Test overdue reminder when exception occurs in try block."""
    from backend.src.services import task as task_service
    monkeypatch.setattr(task_service, 'get_task_with_subtasks', lambda _id: (_ for _ in ()).throw(Exception("Task service error")))

    result = overdue_task_reminder(1)

    assert result is None

