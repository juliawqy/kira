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

# UNI-29-001 
def test_upcoming_no_deadline_returns_failure(reminder_data, patch_email_settings, monkeypatch):
    from backend.src.services import task as task_service
    task_dict = reminder_data.TASK_WITHOUT_DEADLINE.copy()
    task = _TaskObj(
        task_id=123,
        title=task_dict.get('title'),
        deadline=None,
        priority=task_dict.get('priority'),
        description=task_dict.get('description'),
        project_id=task_dict.get('project_id'),
    )
    monkeypatch.setattr(task_service, 'get_task_with_subtasks', lambda _id: task)

    result = upcoming_task_reminder(123)

    
    assert result["success"] is False
    assert result["message"] == "Task does not have a deadline"
    assert result["recipients_count"] == 0

# UNI-29-002
def test_upcoming_no_recipients_configured_early_return(reminder_data, patch_email_settings, monkeypatch):
    
    from backend.src.services import task as task_service
    from backend.src.services.email import get_email_service
    task_dict = reminder_data.UPCOMING_TASK.copy()
    task = _TaskObj(
        task_id=42,
        title=task_dict.get('title'),
        deadline=date.fromisoformat(task_dict['deadline']),
        priority=task_dict.get('priority'),
        description=task_dict.get('description'),
        project_id=task_dict.get('project_id'),
    )
    monkeypatch.setattr(task_service, 'get_task_with_subtasks', lambda _id: task)
    es = get_email_service()
    monkeypatch.setattr(es, '_get_task_notification_recipients', lambda _tid: [])

    
    result = upcoming_task_reminder(42)

    
    assert result["success"] is True
    assert result["message"] == "No recipients configured for notifications"
    assert result["recipients_count"] == 0

# UNI-29-003
def test_upcoming_project_service_exception_is_silent(reminder_data, patch_email_settings, monkeypatch):
    
    from backend.src.services import task as task_service
    import backend.src.services.project as project_service
    from backend.src.services.email import get_email_service
    task_dict = reminder_data.UPCOMING_TASK.copy()
    task = _TaskObj(
        task_id=77,
        title=task_dict.get('title'),
        deadline=date.fromisoformat(task_dict['deadline']),
        priority=task_dict.get('priority'),
        description=task_dict.get('description'),
        project_id=1,
    )
    monkeypatch.setattr(task_service, 'get_task_with_subtasks', lambda _id: task)
    es = get_email_service()
    monkeypatch.setattr(es, '_get_task_notification_recipients', lambda _tid: [EmailRecipient(email='a@b.com', name='A')])
    monkeypatch.setattr(project_service, 'get_project_by_id', lambda _pid: (_ for _ in ()).throw(Exception("proj service down")))
    
    monkeypatch.setattr(es, '_send_smtp_message', lambda *args, **kwargs: 1)

    
    result = upcoming_task_reminder(77)

    
    assert result["success"] is True
    assert result["email_id"] == "1"

# UNI-29-004
def test_upcoming_send_returns_none_raises_500(reminder_data, patch_email_settings, monkeypatch):
    from backend.src.services import task as task_service
    from backend.src.services.email import get_email_service
    task_dict = reminder_data.UPCOMING_TASK.copy()
    task = _TaskObj(
        task_id=55,
        title=task_dict.get('title'),
        deadline=date.fromisoformat(task_dict['deadline']),
        priority=task_dict.get('priority'),
        description=task_dict.get('description'),
        project_id=task_dict.get('project_id'),
    )
    monkeypatch.setattr(task_service, 'get_task_with_subtasks', lambda _id: task)
    es = get_email_service()
    monkeypatch.setattr(es, '_get_task_notification_recipients', lambda _tid: [EmailRecipient(email='a@b.com')])
    monkeypatch.setattr(es, '_send_smtp_message', lambda *args, **kwargs: None)

    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc:
        upcoming_task_reminder(55)
    assert exc.value.status_code == 500

# UNI-29-005
def test_upcoming_prepare_message_raises_500(reminder_data, patch_email_settings, monkeypatch):
    from backend.src.services import task as task_service
    from backend.src.services.email import get_email_service
    task_dict = reminder_data.UPCOMING_TASK.copy()
    task = _TaskObj(
        task_id=88,
        title=task_dict.get('title'),
        deadline=date.fromisoformat(task_dict['deadline']),
        priority=task_dict.get('priority'),
        description=task_dict.get('description'),
        project_id=task_dict.get('project_id'),
    )
    monkeypatch.setattr(task_service, 'get_task_with_subtasks', lambda _id: task)
    es = get_email_service()
    monkeypatch.setattr(es, '_get_task_notification_recipients', lambda _tid: [EmailRecipient(email='a@b.com')])
    monkeypatch.setattr(es, '_prepare_message', lambda *args, **kwargs: (_ for _ in ()).throw(AttributeError('boom')))

    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc:
        upcoming_task_reminder(88)
    assert exc.value.status_code == 500


# Overdue reminder unit tests
# UNI-107-001 
def test_overdue_no_deadline_returns_failure(reminder_data, patch_email_settings, monkeypatch):
    from backend.src.services import task as task_service
    task_dict = reminder_data.TASK_WITHOUT_DEADLINE.copy()
    task = _TaskObj(
        task_id=223,
        title=task_dict.get('title'),
        deadline=None,
        priority=task_dict.get('priority'),
        description=task_dict.get('description'),
        project_id=task_dict.get('project_id'),
    )
    monkeypatch.setattr(task_service, 'get_task_with_subtasks', lambda _id: task)

    result = overdue_task_reminder(223)
    assert result["success"] is False
    assert result["message"] == "Task does not have a deadline"
    assert result["recipients_count"] == 0

# UNI-107-002
def test_overdue_no_recipients_configured_early_return(reminder_data, patch_email_settings, monkeypatch):
    from backend.src.services import task as task_service
    from backend.src.services.email import get_email_service
    task_dict = reminder_data.OVERDUE_TASK.copy()
    task = _TaskObj(
        task_id=242,
        title=task_dict.get('title'),
        deadline=date.fromisoformat(task_dict['deadline']),
        priority=task_dict.get('priority'),
        description=task_dict.get('description'),
        project_id=task_dict.get('project_id'),
    )
    monkeypatch.setattr(task_service, 'get_task_with_subtasks', lambda _id: task)
    es = get_email_service()
    monkeypatch.setattr(es, '_get_task_notification_recipients', lambda _tid: [])

    result = overdue_task_reminder(242)
    assert result["success"] is True
    assert result["message"] == "No recipients configured for notifications"
    assert result["recipients_count"] == 0

# UNI-107-003
def test_overdue_project_service_exception_is_silent(reminder_data, patch_email_settings, monkeypatch):
    from backend.src.services import task as task_service
    import backend.src.services.project as project_service
    from backend.src.services.email import get_email_service
    task_dict = reminder_data.OVERDUE_TASK.copy()
    task = _TaskObj(
        task_id=277,
        title=task_dict.get('title'),
        deadline=date.fromisoformat(task_dict['deadline']),
        priority=task_dict.get('priority'),
        description=task_dict.get('description'),
        project_id=1,
    )
    monkeypatch.setattr(task_service, 'get_task_with_subtasks', lambda _id: task)
    es = get_email_service()
    monkeypatch.setattr(es, '_get_task_notification_recipients', lambda _tid: [EmailRecipient(email='a@b.com', name='A')])
    monkeypatch.setattr(project_service, 'get_project_by_id', lambda _pid: (_ for _ in ()).throw(Exception("proj service down")))
    monkeypatch.setattr(es, '_send_smtp_message', lambda *args, **kwargs: 1)

    result = overdue_task_reminder(277)
    assert result["success"] is True
    assert result["email_id"] == "1"

# UNI-107-004
def test_overdue_send_returns_unexpected_id_raises_500(reminder_data, patch_email_settings, monkeypatch):
    from backend.src.services import task as task_service
    from backend.src.services.email import get_email_service
    task_dict = reminder_data.OVERDUE_TASK.copy()
    task = _TaskObj(
        task_id=299,
        title=task_dict.get('title'),
        deadline=date.fromisoformat(task_dict['deadline']),
        priority=task_dict.get('priority'),
        description=task_dict.get('description'),
        project_id=task_dict.get('project_id'),
    )
    monkeypatch.setattr(task_service, 'get_task_with_subtasks', lambda _id: task)
    es = get_email_service()
    monkeypatch.setattr(es, '_get_task_notification_recipients', lambda _tid: [EmailRecipient(email='a@b.com')])
    monkeypatch.setattr(es, '_send_smtp_message', lambda *args, **kwargs: "x")

    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc:
        overdue_task_reminder(299)
    assert exc.value.status_code == 500

# UNI-107-005
def test_overdue_prepare_message_raises_500(reminder_data, patch_email_settings, monkeypatch):
    from backend.src.services import task as task_service
    from backend.src.services.email import get_email_service
    task_dict = reminder_data.OVERDUE_TASK.copy()
    task = _TaskObj(
        task_id=311,
        title=task_dict.get('title'),
        deadline=date.fromisoformat(task_dict['deadline']),
        priority=task_dict.get('priority'),
        description=task_dict.get('description'),
        project_id=task_dict.get('project_id'),
    )
    monkeypatch.setattr(task_service, 'get_task_with_subtasks', lambda _id: task)
    es = get_email_service()
    monkeypatch.setattr(es, '_get_task_notification_recipients', lambda _tid: [type('R', (), {'email': 'a@b.com'})()])
    monkeypatch.setattr(es, '_prepare_message', lambda *args, **kwargs: (_ for _ in ()).throw(AttributeError('boom')))

    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc:
        overdue_task_reminder(311)
    assert exc.value.status_code == 500


