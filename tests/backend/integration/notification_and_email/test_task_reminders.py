
from __future__ import annotations

import pytest
from unittest.mock import patch, MagicMock
from datetime import date

from backend.src.handlers.task_handler import upcoming_task_reminder, overdue_task_reminder
from backend.src.services.email import EmailService
from backend.src.schemas.email import EmailRecipient
from backend.src.config.email_config import EmailSettings

import importlib.util
from pathlib import Path
_integrations_mock_path = Path(__file__).parents[3] / 'mock_data' / 'integration_data.py'
_spec = importlib.util.spec_from_file_location('integration_mock_data', str(_integrations_mock_path))
_integration_data = importlib.util.module_from_spec(_spec)
assert _spec and _spec.loader, f"Failed to load integration mock data: {_integrations_mock_path}"
_spec.loader.exec_module(_integration_data)


_reminder_mock_path = Path(__file__).parents[3] / 'mock_data' / 'notification_email' / 'task_reminder_data.py'
_reminder_spec = importlib.util.spec_from_file_location('reminder_mock_data', str(_reminder_mock_path))
_reminder_data = importlib.util.module_from_spec(_reminder_spec)
assert _reminder_spec and _reminder_spec.loader, f"Failed to load reminder mock data: {_reminder_mock_path}"
_reminder_spec.loader.exec_module(_reminder_data)


@pytest.fixture
def patched_email_settings_tls(monkeypatch):
    """Patch email settings to use test TLS configuration."""
    settings = EmailSettings(**_integration_data.EMAIL_SETTINGS_TLS)

    monkeypatch.setenv("FASTMAIL_SMTP_HOST", settings.fastmail_smtp_host)
    monkeypatch.setenv("FASTMAIL_SMTP_PORT", str(settings.fastmail_smtp_port))
    monkeypatch.setenv("FASTMAIL_USERNAME", settings.fastmail_username)
    monkeypatch.setenv("FASTMAIL_PASSWORD", settings.fastmail_password)
    monkeypatch.setenv("FASTMAIL_FROM_EMAIL", settings.fastmail_from_email)
    monkeypatch.setenv("FASTMAIL_FROM_NAME", settings.fastmail_from_name)
    monkeypatch.setenv("APP_NAME", settings.app_name)
    monkeypatch.setenv("APP_URL", settings.app_url)
    monkeypatch.setenv("USE_TLS", "True")
    monkeypatch.setenv("USE_SSL", "False")
    monkeypatch.setenv("TIMEOUT", str(settings.timeout))

    import backend.src.services.email as email_service_module
    new_service = EmailService()
    new_service.settings = settings
    assert new_service._validate_settings() is True
    email_service_module.email_service = new_service
    return settings


@pytest.fixture
def patched_smtp_tls():
    with patch("backend.src.services.email.smtplib.SMTP", autospec=True) as mock_smtp:
        server = MagicMock(name="SMTPServerTLS")
        mock_smtp.return_value = server
        yield server


@pytest.fixture
def recipients_two(monkeypatch):
    """Mock two recipients returned by the email service."""
    import backend.src.services.email as email_service_module
    recips = [
        EmailRecipient(email="john.doe@example.com", name="John Doe"),
        EmailRecipient(email="jane.smith@example.com", name="Jane Smith"),
    ]
    monkeypatch.setattr(email_service_module.email_service, "_get_task_notification_recipients", lambda task_id: recips)
    return recips


@pytest.fixture
def recipients_one(monkeypatch):
    """Mock single recipient returned by the email service."""
    import backend.src.services.email as email_service_module
    recips = [EmailRecipient(email="test.user@example.com", name="Test User")]
    monkeypatch.setattr(email_service_module.email_service, "_get_task_notification_recipients", lambda task_id: recips)
    return recips


@pytest.fixture
def recipients_mixed(monkeypatch):
    """Mock two recipients returned by the email service (others filtered upstream)."""
    import backend.src.services.email as email_service_module
    recips = [
        EmailRecipient(email="john.doe@example.com", name="John Doe"),
        EmailRecipient(email="bob.wilson@example.com", name="Bob Wilson"),
    ]
    monkeypatch.setattr(email_service_module.email_service, "_get_task_notification_recipients", lambda task_id: recips)
    return recips


@pytest.fixture
def recipients_empty(monkeypatch):
    """Mock no recipients configured."""
    import backend.src.services.email as email_service_module
    monkeypatch.setattr(email_service_module.email_service, "_get_task_notification_recipients", lambda task_id: [])
    return []


@pytest.fixture
def recipients_none_configured(monkeypatch):
    """Alias to recipients_empty for backward compatibility in scenarios."""
    import backend.src.services.email as email_service_module
    monkeypatch.setattr(email_service_module.email_service, "_get_task_notification_recipients", lambda task_id: [])
    return []


@pytest.fixture
def task_factory_with_kwargs(db_session):
    """Wrapper around task_factory that properly merges kwargs into default data."""
    def _create_task_with_kwargs(**kwargs):
        # Create task with merged data (kwargs override defaults)
        from backend.src.database.models.task import Task
        from backend.src.database.models.project import Project
        from backend.src.database.models.user import User
        from backend.src.enums.task_status import TaskStatus
        from tests.mock_data.notification_email.integration_data import VALID_USER, VALID_PROJECT
        import importlib.util
        from pathlib import Path
        
        mock_dir = Path(__file__).parents[3] / 'mock_data' / 'notification_email'
        file_path = mock_dir / 'integration_notification_email_data.py'
        spec = importlib.util.spec_from_file_location(f"mock_{file_path.stem}", str(file_path))
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            default_data = dict(getattr(module, 'DEFAULT_TASK_DATA', {}))
        else:
            default_data = {}
        
        default_data.setdefault("status", TaskStatus.TO_DO.value)
        default_data.update(kwargs)
        
        user = User(**VALID_USER)
        db_session.add(user)
        db_session.flush()
        project = Project(**VALID_PROJECT)
        db_session.add(project)
        db_session.flush()
        
        task = Task(**default_data)
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)
        return task
    return _create_task_with_kwargs


class TestUpcomingTaskReminderIntegration:
    """Integration tests for upcoming_task_reminder endpoint."""
    
    # INT-29-001 
    def test_upcoming_reminder_comprehensive_success(self, db_session, patched_email_settings_tls, patched_smtp_tls, task_factory_with_kwargs, recipients_mixed):
        """Test comprehensive success scenario including mixed email availability."""
        from datetime import date
        
        scenario = _reminder_data.RECIPIENTS_SUCCESS_TWO
        task_data = _reminder_data.UPCOMING_TASK.copy()
        task_data["deadline"] = date.fromisoformat(task_data["deadline"])
        task = task_factory_with_kwargs(**task_data)
        
        result = upcoming_task_reminder(task.id)
        
        assert result["success"] is True
        assert result["recipients_count"] == len(recipients_mixed)
        assert "email_id" in result
        
        server = patched_smtp_tls
        server.starttls.assert_called_once()
        server.login.assert_not_called()
        server.send_message.assert_not_called()
        server.quit.assert_called_once()
    
    # INT-29-002 
    @pytest.mark.parametrize("fixture_name", ["recipients_empty", "recipients_none_configured"])
    def test_upcoming_reminder_no_recipients(self, db_session, patched_email_settings_tls, patched_smtp_tls, task_factory_with_kwargs, request, fixture_name):
        """Test early return when no assignees have email addresses."""

        request.getfixturevalue(fixture_name)
        task_data = _reminder_data.UPCOMING_TASK.copy()
        task_data["deadline"] = date.fromisoformat(task_data["deadline"])
        task = task_factory_with_kwargs(**task_data)
        
        result = upcoming_task_reminder(task.id)

        assert result["success"] is True
        assert result["message"] == "No recipients configured for notifications"
        assert result["recipients_count"] == 0

        server = patched_smtp_tls
        server.starttls.assert_not_called()
        server.login.assert_not_called()
        server.send_message.assert_not_called()
    
    # INT-29-003 
    @pytest.mark.parametrize("scenario_key", [
        "task_not_found",
        "no_deadline",
        "send_failure",
    ])
    def test_upcoming_reminder_error_scenarios(self, db_session, patched_email_settings_tls, patched_smtp_tls,
                                            task_factory_with_kwargs, monkeypatch, scenario_key):
        """Test all error scenarios."""
        import backend.src.services.task as task_service      
        from backend.src.services.email import get_email_service
        from fastapi import HTTPException

        scenario = _reminder_data.ALL_ERROR_SCENARIOS[scenario_key]

        task = None
        if scenario_key != "task_not_found":
            task_data = scenario.get("task_data", _reminder_data.UPCOMING_TASK).copy()
            if "deadline" in task_data:
                task_data["deadline"] = date.fromisoformat(task_data["deadline"])
            task = task_factory_with_kwargs(**task_data)
            task_id = task.id
        else:
            task_id = scenario["task_id"]

        if scenario_key == "task_not_found":
            monkeypatch.setattr(task_service, "get_task_with_subtasks",
                              lambda task_id: scenario["mock_task_service_return"])
        elif scenario_key == "no_deadline":
            email_service = get_email_service()
            monkeypatch.setattr(email_service, "_get_task_notification_recipients", lambda task_id: [EmailRecipient(email="a@b.com")])
        elif scenario_key == "send_failure":
            email_service = get_email_service()
            monkeypatch.setattr(email_service, "_get_task_notification_recipients", lambda task_id: [EmailRecipient(email="a@b.com")])
            monkeypatch.setattr(email_service, "_send_smtp_message", lambda *args, **kwargs: "unexpected")
        
        if "expected_response" in scenario:
            result = upcoming_task_reminder(task_id)
            assert result["success"] == scenario["expected_response"]["success"]
            assert result["recipients_count"] == scenario["expected_response"]["recipients_count"]
        else:
            with pytest.raises(HTTPException) as exc_info:
                upcoming_task_reminder(task_id)
            expected = scenario["expected_exception"]
            assert exc_info.value.status_code == expected["status_code"]
            for message_part in expected["detail_contains"]:
                assert message_part in str(exc_info.value.detail)


class TestOverdueTaskReminderIntegration:
    """Integration tests for overdue_task_reminder endpoint."""
    
    # INT-107-001 - Comprehensive success test with multiple assignees
    def test_overdue_reminder_comprehensive_success(self, db_session, patched_email_settings_tls, patched_smtp_tls, task_factory_with_kwargs, recipients_mixed):
        """Test comprehensive success scenario including mixed email availability."""
        from datetime import date
        
        task_data = _reminder_data.OVERDUE_TASK.copy()
        task_data["deadline"] = date.fromisoformat(task_data["deadline"])
        task_data["title"] = "Overdue Task"
        task = task_factory_with_kwargs(**task_data)
        
        result = overdue_task_reminder(task.id)

        assert result["success"] is True
        assert result["recipients_count"] == len(recipients_mixed)
        assert "email_id" in result

        server = patched_smtp_tls
        server.starttls.assert_called_once()
        server.login.assert_not_called()
        server.send_message.assert_not_called()
        server.quit.assert_called_once()
    
    # INT-107-002 - No recipients scenario
    @pytest.mark.parametrize("fixture_name", ["recipients_empty", "recipients_none_configured"])
    def test_overdue_reminder_no_recipients(self, db_session, patched_email_settings_tls, patched_smtp_tls, task_factory_with_kwargs, request, fixture_name):
        """Test early return when no assignees have email addresses."""
        request.getfixturevalue(fixture_name)
        task_data = _reminder_data.OVERDUE_TASK.copy()
        task_data["deadline"] = date.fromisoformat(task_data["deadline"])
        task = task_factory_with_kwargs(**task_data)

        result = overdue_task_reminder(task.id)

        assert result["success"] is True
        assert result["message"] == "No recipients configured for notifications"
        assert result["recipients_count"] == 0

        server = patched_smtp_tls
        server.starttls.assert_not_called()
        server.login.assert_not_called()
        server.send_message.assert_not_called()
    
    # INT-107-003 - Error scenarios
    @pytest.mark.parametrize("scenario_key", [
        "task_not_found",
        "no_deadline",
        "send_failure",
    ])
    def test_overdue_reminder_error_scenarios(self, db_session, patched_email_settings_tls, patched_smtp_tls,
                                            task_factory_with_kwargs, monkeypatch, scenario_key):
        """Test all error scenarios."""
        import backend.src.services.task as task_service      
        from backend.src.services.email import get_email_service
        from fastapi import HTTPException

        scenario = _reminder_data.ALL_ERROR_SCENARIOS[scenario_key]

        task = None
        if scenario_key != "task_not_found":
            task_data = scenario.get("task_data", _reminder_data.OVERDUE_TASK).copy()
            if "deadline" in task_data:
                task_data["deadline"] = date.fromisoformat(task_data["deadline"])
            task = task_factory_with_kwargs(**task_data)
            task_id = task.id
        else:
            task_id = scenario["task_id"]

        if scenario_key == "task_not_found":
            monkeypatch.setattr(task_service, "get_task_with_subtasks",
                              lambda task_id: scenario["mock_task_service_return"])
        elif scenario_key == "no_deadline":
            email_service = get_email_service()
            monkeypatch.setattr(email_service, "_get_task_notification_recipients", lambda task_id: [EmailRecipient(email="a@b.com")])
        elif scenario_key == "send_failure":
            email_service = get_email_service()
            monkeypatch.setattr(email_service, "_get_task_notification_recipients", lambda task_id: [EmailRecipient(email="a@b.com")])
            monkeypatch.setattr(email_service, "_send_smtp_message", lambda *args, **kwargs: None)

        if "expected_response" in scenario:
            result = overdue_task_reminder(task_id)
            assert result["success"] == scenario["expected_response"]["success"]
            assert result["recipients_count"] == scenario["expected_response"]["recipients_count"]
        else:
            with pytest.raises(HTTPException) as exc_info:
                overdue_task_reminder(task_id)
            expected = scenario["expected_exception"]
            assert exc_info.value.status_code == expected["status_code"]
            for message_part in expected["detail_contains"]:
                assert message_part in str(exc_info.value.detail)


class TestTaskReminderAPI:
    """Integration tests for task reminder API endpoints (routes)."""
    
    @pytest.fixture(scope="class")
    def api_client(self, test_engine_backend_integration):
        """Create a TestClient for API route testing."""
        from fastapi.testclient import TestClient
        from backend.src.main import app
        from sqlalchemy.orm import sessionmaker
        import backend.src.services.task as task_service
        
        TestingSessionLocal = sessionmaker(
            bind=test_engine_backend_integration,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )
        task_service.SessionLocal = TestingSessionLocal
        
        with TestClient(app) as client:
            yield client
    
    def test_upcoming_reminder_api_success(self, api_client, db_session, patched_email_settings_tls, patched_smtp_tls, 
                                           task_factory_with_kwargs, recipients_two):
        """Test upcoming reminder API endpoint returns 200 on success."""
        from datetime import date
        
        task_data = _reminder_data.UPCOMING_TASK.copy()
        task_data["deadline"] = date.fromisoformat(task_data["deadline"])
        task = task_factory_with_kwargs(**task_data)
        
        response = api_client.post(f"/kira/app/api/v1/task/{task.id}/notify-upcoming")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["recipients_count"] == len(recipients_two)
    
    def test_upcoming_reminder_api_valueerror_converted_to_404(self, api_client, db_session, patched_email_settings_tls, 
                                                               patched_smtp_tls, monkeypatch):
        """Test that ValueError from handler is converted to 404 by route."""
        import backend.src.handlers.task_handler as task_handler

        def mock_upcoming_reminder(task_id):
            raise ValueError("Task not found")
        
        monkeypatch.setattr(task_handler, "upcoming_task_reminder", mock_upcoming_reminder)
        
        response = api_client.post("/kira/app/api/v1/task/999/notify-upcoming")
        assert response.status_code == 404
        assert "Task not found" in response.json()["detail"]
    
    def test_upcoming_reminder_api_generic_exception_converted_to_500(self, api_client, db_session, 
                                                                       patched_email_settings_tls, patched_smtp_tls, 
                                                                       monkeypatch):
        """Test that generic Exception from handler is converted to 500 by route."""
        import backend.src.handlers.task_handler as task_handler

        def mock_upcoming_reminder(task_id):
            raise Exception("Database connection failed")
        
        monkeypatch.setattr(task_handler, "upcoming_task_reminder", mock_upcoming_reminder)
        
        response = api_client.post("/kira/app/api/v1/task/1/notify-upcoming")
        assert response.status_code == 500
        assert "Error sending notification" in response.json()["detail"]
        assert "Database connection failed" in response.json()["detail"]
    
    def test_upcoming_reminder_api_httpexception_re_raised(self, api_client, db_session, patched_email_settings_tls, 
                                                           patched_smtp_tls, monkeypatch):
        """Test that HTTPException from handler is properly re-raised by route."""
        import backend.src.handlers.task_handler as task_handler
        from fastapi import HTTPException

        def mock_upcoming_reminder(task_id):
            raise HTTPException(status_code=404, detail="Task not found")
        
        monkeypatch.setattr(task_handler, "upcoming_task_reminder", mock_upcoming_reminder)
        
        response = api_client.post("/kira/app/api/v1/task/999/notify-upcoming")
        assert response.status_code == 404
        assert response.json()["detail"] == "Task not found"
    
    def test_overdue_reminder_api_success(self, api_client, db_session, patched_email_settings_tls, patched_smtp_tls, 
                                         task_factory_with_kwargs, recipients_two):
        """Test overdue reminder API endpoint returns 200 on success."""
        from datetime import date
        
        task_data = _reminder_data.OVERDUE_TASK.copy()
        task_data["deadline"] = date.fromisoformat(task_data["deadline"])
        task_data["title"] = "Overdue Task"
        task = task_factory_with_kwargs(**task_data)
        
        response = api_client.post(f"/kira/app/api/v1/task/{task.id}/notify-overdue")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["recipients_count"] == len(recipients_two)
    
    def test_overdue_reminder_api_valueerror_converted_to_404(self, api_client, db_session, patched_email_settings_tls, 
                                                              patched_smtp_tls, monkeypatch):
        """Test that ValueError from handler is converted to 404 by route."""
        import backend.src.handlers.task_handler as task_handler

        def mock_overdue_reminder(task_id):
            raise ValueError("Task not found")
        
        monkeypatch.setattr(task_handler, "overdue_task_reminder", mock_overdue_reminder)
        
        response = api_client.post("/kira/app/api/v1/task/999/notify-overdue")
        assert response.status_code == 404
        assert "Task not found" in response.json()["detail"]
    
    def test_overdue_reminder_api_generic_exception_converted_to_500(self, api_client, db_session, 
                                                                     patched_email_settings_tls, patched_smtp_tls, 
                                                                     monkeypatch):
        """Test that generic Exception from handler is converted to 500 by route."""
        import backend.src.handlers.task_handler as task_handler

        def mock_overdue_reminder(task_id):
            raise Exception("Database connection failed")
        
        monkeypatch.setattr(task_handler, "overdue_task_reminder", mock_overdue_reminder)
        
        response = api_client.post("/kira/app/api/v1/task/1/notify-overdue")
        assert response.status_code == 500
        assert "Error sending notification" in response.json()["detail"]
        assert "Database connection failed" in response.json()["detail"]
    
    def test_overdue_reminder_api_httpexception_re_raised(self, api_client, db_session, patched_email_settings_tls, 
                                                          patched_smtp_tls, monkeypatch):
        """Test that HTTPException from handler is properly re-raised by route."""
        import backend.src.handlers.task_handler as task_handler
        from fastapi import HTTPException

        def mock_overdue_reminder(task_id):
            raise HTTPException(status_code=404, detail="Task not found")
        
        monkeypatch.setattr(task_handler, "overdue_task_reminder", mock_overdue_reminder)
        
        response = api_client.post("/kira/app/api/v1/task/999/notify-overdue")
        assert response.status_code == 404
        assert response.json()["detail"] == "Task not found"
    
    # INT-29-004 - Handler edge cases
    def test_upcoming_reminder_project_service_exception_silently_handled(self, db_session, patched_email_settings_tls, 
                                                                          patched_smtp_tls, task_factory_with_kwargs, 
                                                                          recipients_mixed, monkeypatch):
        """Test that project service exceptions are silently handled (lines 140-141)."""
        from datetime import date
        import backend.src.services.project as project_service
        
        task_data = _reminder_data.UPCOMING_TASK.copy()
        task_data["deadline"] = date.fromisoformat(task_data["deadline"])
        task = task_factory_with_kwargs(**task_data)

        monkeypatch.setattr(project_service, "get_project_by_id", lambda project_id: (_ for _ in ()).throw(Exception("Project service error")))

        result = upcoming_task_reminder(task.id)
        assert result["success"] is True
    
    def test_upcoming_reminder_email_send_returns_none(self, db_session, patched_email_settings_tls, 
                                                       patched_smtp_tls, task_factory_with_kwargs, 
                                                       recipients_one, monkeypatch):
        """Test handler when _send_smtp_message returns None."""
        from datetime import date
        from backend.src.services.email import get_email_service
        
        task_data = _reminder_data.UPCOMING_TASK.copy()
        task_data["deadline"] = date.fromisoformat(task_data["deadline"])
        task = task_factory_with_kwargs(**task_data)

        email_service = get_email_service()
        monkeypatch.setattr(email_service, "_send_smtp_message", lambda *args, **kwargs: None)
        
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            upcoming_task_reminder(task.id)
        assert exc_info.value.status_code == 500
        assert "Error sending notification" in str(exc_info.value.detail)
    
    def test_upcoming_reminder_email_send_unexpected_id(self, db_session, patched_email_settings_tls, 
                                                        patched_smtp_tls, task_factory_with_kwargs, 
                                                        recipients_one, monkeypatch):
        """Test handler when _send_smtp_message returns unexpected id."""
        from datetime import date
        from backend.src.services.email import get_email_service, EmailResponse
        
        task_data = _reminder_data.UPCOMING_TASK.copy()
        task_data["deadline"] = date.fromisoformat(task_data["deadline"])
        task = task_factory_with_kwargs(**task_data)

        email_service = get_email_service()
        monkeypatch.setattr(email_service, "_send_smtp_message", lambda *args, **kwargs: "unexpected")
        
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            upcoming_task_reminder(task.id)
        assert exc_info.value.status_code == 500
        assert "Error sending notification" in str(exc_info.value.detail)
    
    def test_upcoming_reminder_unexpected_exception_handled(self, db_session, patched_email_settings_tls, 
                                                            patched_smtp_tls, task_factory_with_kwargs, 
                                                            recipients_one, monkeypatch):
        """Test outer exception handler by forcing _prepare_message to raise."""
        from datetime import date
        from backend.src.schemas.email import EmailRecipient
        
        task_data = _reminder_data.UPCOMING_TASK.copy()
        task_data["deadline"] = date.fromisoformat(task_data["deadline"])
        task = task_factory_with_kwargs(**task_data)

        from backend.src.services.email import get_email_service
        email_service = get_email_service()
        monkeypatch.setattr(email_service, "_prepare_message", lambda *args, **kwargs: (_ for _ in ()).throw(AttributeError("Unexpected error creating email")))
        
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            upcoming_task_reminder(task.id)
        assert exc_info.value.status_code == 500
        assert "Unexpected error" in str(exc_info.value.detail)
    
    def test_overdue_reminder_project_service_exception_silently_handled(self, db_session, patched_email_settings_tls, 
                                                                         patched_smtp_tls, task_factory_with_kwargs, 
                                                                         recipients_mixed, monkeypatch):
        """Test that project service exceptions are silently handled (lines 250-251)."""
        from datetime import date
        import backend.src.services.project as project_service
        
        task_data = _reminder_data.OVERDUE_TASK.copy()
        task_data["deadline"] = date.fromisoformat(task_data["deadline"])
        task_data["title"] = "Overdue Task"
        task = task_factory_with_kwargs(**task_data)

        monkeypatch.setattr(project_service, "get_project_by_id", lambda project_id: (_ for _ in ()).throw(Exception("Project service error")))

        result = overdue_task_reminder(task.id)
        assert result["success"] is True
    
    def test_overdue_reminder_email_send_returns_none(self, db_session, patched_email_settings_tls, 
                                                      patched_smtp_tls, task_factory_with_kwargs, 
                                                      recipients_one, monkeypatch):
        """Test handler when _send_smtp_message returns None."""
        from datetime import date
        from backend.src.services.email import get_email_service
        
        task_data = _reminder_data.OVERDUE_TASK.copy()
        task_data["deadline"] = date.fromisoformat(task_data["deadline"])
        task_data["title"] = "Overdue Task"
        task = task_factory_with_kwargs(**task_data)

        email_service = get_email_service()
        monkeypatch.setattr(email_service, "_send_smtp_message", lambda *args, **kwargs: None)
        
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            overdue_task_reminder(task.id)
        assert exc_info.value.status_code == 500
        assert "Error sending notification" in str(exc_info.value.detail)
    
    def test_overdue_reminder_email_send_unexpected_id(self, db_session, patched_email_settings_tls, 
                                                       patched_smtp_tls, task_factory_with_kwargs, 
                                                       recipients_one, monkeypatch):
        """Test handler when _send_smtp_message returns unexpected id."""
        from datetime import date
        from backend.src.services.email import get_email_service, EmailResponse
        
        task_data = _reminder_data.OVERDUE_TASK.copy()
        task_data["deadline"] = date.fromisoformat(task_data["deadline"])
        task_data["title"] = "Overdue Task"
        task = task_factory_with_kwargs(**task_data)

        email_service = get_email_service()
        monkeypatch.setattr(email_service, "_send_smtp_message", lambda *args, **kwargs: "unexpected")
        
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            overdue_task_reminder(task.id)
        assert exc_info.value.status_code == 500
        assert "Error sending notification" in str(exc_info.value.detail)
    
    def test_overdue_reminder_unexpected_exception_handled(self, db_session, patched_email_settings_tls, 
                                                          patched_smtp_tls, task_factory_with_kwargs, 
                                                          recipients_one, monkeypatch):
        """Test outer exception handler by forcing _prepare_message to raise."""
        from datetime import date
        from backend.src.schemas.email import EmailRecipient
        
        task_data = _reminder_data.OVERDUE_TASK.copy()
        task_data["deadline"] = date.fromisoformat(task_data["deadline"])
        task_data["title"] = "Overdue Task"
        task = task_factory_with_kwargs(**task_data)

        from backend.src.services.email import get_email_service
        email_service = get_email_service()
        monkeypatch.setattr(email_service, "_prepare_message", lambda *args, **kwargs: (_ for _ in ()).throw(AttributeError("Unexpected error creating email")))
        
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            overdue_task_reminder(task.id)
        assert exc_info.value.status_code == 500
        assert "Unexpected error" in str(exc_info.value.detail)
