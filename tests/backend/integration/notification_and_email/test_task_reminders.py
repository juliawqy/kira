
from __future__ import annotations

import pytest
from unittest.mock import patch, MagicMock
from datetime import date, datetime

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

# Load task_reminder specific mock data
_reminder_mock_path = Path(__file__).parents[3] / 'mock_data' / 'notification_email' / 'task_reminder_data.py'
_reminder_spec = importlib.util.spec_from_file_location('reminder_mock_data', str(_reminder_mock_path))
_reminder_data = importlib.util.module_from_spec(_reminder_spec)
assert _reminder_spec and _reminder_spec.loader, f"Failed to load reminder mock data: {_reminder_mock_path}"
_reminder_spec.loader.exec_module(_reminder_data)


@pytest.fixture
def patched_email_settings_tls(monkeypatch):
    """Patch email settings to use test TLS configuration."""
    settings = EmailSettings(**_integration_data.EMAIL_SETTINGS_TLS)
    
    # Set environment variables
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
    
    # Recreate email service - it will read from env vars (which we just set)
    # This matches the pattern from test_notification_email_flow.py
    import backend.src.services.email as email_service_module
    
    # Create new service instance - it will read from env vars we just set
    new_service = EmailService()
    
    # IMPORTANT: Directly patch the settings to ensure test values are used
    # This bypasses any potential .env file reading issues
    new_service.settings = settings
    
    # Verify settings are correct and validation passes
    assert new_service.settings.fastmail_username == settings.fastmail_username
    assert new_service.settings.fastmail_password == settings.fastmail_password
    assert new_service._validate_settings() == True, f"Email settings validation failed. Settings: {new_service.settings}"
    
    # Update the module-level instance that get_email_service() returns
    email_service_module.email_service = new_service
    
    return settings


@pytest.fixture
def patched_smtp_tls():
    with patch("backend.src.services.email.smtplib.SMTP", autospec=True) as mock_smtp:
        server = MagicMock(name="SMTPServerTLS")
        mock_smtp.return_value = server
        yield server


@pytest.fixture
def patched_assignees_with_emails(monkeypatch):
    """Mock assignees with valid email addresses."""
    import backend.src.services.task_assignment as assignment_service
    from backend.src.schemas.user import UserRead
    
    mock_assignees = [
        UserRead(**assignee_data) for assignee_data in _reminder_data.ASSIGNEES_WITH_EMAILS
    ]
    monkeypatch.setattr(assignment_service, "list_assignees", lambda task_id: mock_assignees)
    return mock_assignees


@pytest.fixture
def patched_single_assignee(monkeypatch):
    """Mock single assignee with email."""
    import backend.src.services.task_assignment as assignment_service
    from backend.src.schemas.user import UserRead
    
    mock_assignee = [
        UserRead(**_reminder_data.SINGLE_ASSIGNEE_WITH_EMAIL[0])
    ]
    monkeypatch.setattr(assignment_service, "list_assignees", lambda task_id: mock_assignee)
    return mock_assignee


@pytest.fixture
def patched_mixed_assignees(monkeypatch):
    """Mock mixed assignees - some with emails, some without."""
    import backend.src.services.task_assignment as assignment_service
    from backend.src.schemas.user import UserRead
    
    scenario = _reminder_data.MIXED_EMAIL_ASSIGNEES_SUCCESS
    mixed_assignees = []
    
    # Add users with emails
    for user_data in scenario["assignees_with_emails"]:
        mixed_assignees.append(_reminder_data.create_user_with_email(**user_data))
    
    # Add users without emails
    for user_data in scenario["assignees_without_emails"]:
        mixed_assignees.append(_reminder_data.create_user_without_email(**user_data))
    
    monkeypatch.setattr(assignment_service, "list_assignees", lambda task_id: mixed_assignees)
    return mixed_assignees


@pytest.fixture
def patched_empty_assignees(monkeypatch):
    """Mock empty assignees list."""
    import backend.src.services.task_assignment as assignment_service
    
    monkeypatch.setattr(assignment_service, "list_assignees", lambda task_id: [])
    return []


@pytest.fixture
def patched_assignees_without_emails(monkeypatch):
    """Mock assignees without email attributes."""
    import backend.src.services.task_assignment as assignment_service
    
    scenario = _reminder_data.NO_RECIPIENTS_SCENARIO_NO_EMAILS
    mock_assignees = [
        _reminder_data.create_user_without_email(**user_data) 
        for user_data in scenario["assignees"]
    ]
    
    monkeypatch.setattr(assignment_service, "list_assignees", lambda task_id: mock_assignees)
    return mock_assignees


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
        
        # Load the mock module to get DEFAULT_TASK_DATA (same logic as conftest)
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
        # Merge kwargs into default_data (kwargs override defaults)
        default_data.update(kwargs)
        
        # Create user and project
        user = User(**VALID_USER)
        db_session.add(user)
        db_session.flush()
        project = Project(**VALID_PROJECT)
        db_session.add(project)
        db_session.flush()
        
        # Create task with merged data
        task = Task(**default_data)
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)
        return task
    return _create_task_with_kwargs


class TestUpcomingTaskReminderIntegration:
    """Integration tests for upcoming_task_reminder endpoint."""
    
    # INT-REM-001 - Comprehensive success test with mixed email availability  
    def test_upcoming_reminder_comprehensive_success(self, db_session, patched_email_settings_tls, patched_smtp_tls, task_factory_with_kwargs, patched_mixed_assignees):
        """Test comprehensive success scenario including mixed email availability."""
        from datetime import date
        
        # Create task using mock data
        scenario = _reminder_data.MIXED_EMAIL_ASSIGNEES_SUCCESS
        task_data = scenario["task_data"].copy()
        task_data["deadline"] = date.fromisoformat(task_data["deadline"])
        task = task_factory_with_kwargs(**task_data)
        
        # Call the function
        result = upcoming_task_reminder(task.id)
        
        # Verify response
        assert result["success"] == scenario["expected_response"]["success"]
        assert result["recipients_count"] == scenario["expected_response"]["recipients_count"]
        assert "email_id" in result
        
        # Verify SMTP was called
        server = patched_smtp_tls
        server.starttls.assert_called_once()
        server.login.assert_called_once()
        server.send_message.assert_called_once()
        server.quit.assert_called_once()
    
    # INT-REM-002 - No recipients scenario
    @pytest.mark.parametrize("scenario_key", ["empty_assignees", "no_email_addresses"])
    def test_upcoming_reminder_no_recipients(self, db_session, patched_email_settings_tls, patched_smtp_tls, task_factory_with_kwargs, monkeypatch, scenario_key):
        """Test early return when no assignees have email addresses."""
        import backend.src.services.task_assignment as assignment_service
        
        # Get scenario from mock data
        scenario = _reminder_data.ALL_NO_RECIPIENTS_SCENARIOS[scenario_key]
        
        # Create task using mock data
        from datetime import date
        task_data = scenario["task_data"].copy()
        task_data["deadline"] = date.fromisoformat(task_data["deadline"])
        task = task_factory_with_kwargs(**task_data)
        
        # Setup mock based on scenario
        if scenario["assignees"] == []:
            monkeypatch.setattr(assignment_service, "list_assignees", lambda task_id: [])
        else:
            mock_assignees = [
                _reminder_data.create_user_without_email(**user_data)
                for user_data in scenario["assignees"]        
            ]
            monkeypatch.setattr(assignment_service, "list_assignees", lambda task_id: mock_assignees)
        
        # Call the function
        result = upcoming_task_reminder(task.id)
        
        # Verify early return response
        assert result["success"] == scenario["expected_response"]["success"]
        assert result["message"] == scenario["expected_response"]["message"]
        assert result["recipients_count"] == scenario["expected_response"]["recipients_count"]
        
        # Verify SMTP was not called
        server = patched_smtp_tls
        server.starttls.assert_not_called()
        server.login.assert_not_called()
        server.send_message.assert_not_called()
    
    # INT-REM-003 - Error scenarios
    @pytest.mark.parametrize("scenario_key", [
        "task_not_found",
        "no_deadline",
        "assignment_service_error",
        "email_service_error",
    ])
    def test_upcoming_reminder_error_scenarios(self, db_session, patched_email_settings_tls, patched_smtp_tls,
                                            task_factory_with_kwargs, monkeypatch, scenario_key):
        """Test all error scenarios."""
        import backend.src.services.task_assignment as assignment_service
        import backend.src.services.task as task_service      
        from backend.src.services.email import get_email_service
        from backend.src.schemas.user import UserRead
        from fastapi import HTTPException
        from datetime import date
        
        # Get scenario from mock data
        scenario = _reminder_data.ALL_ERROR_SCENARIOS[scenario_key]
        
        # Create task (for scenarios that need it)
        task = None
        if scenario_key != "task_not_found":
            task_data = scenario.get("task_data", _reminder_data.UPCOMING_TASK).copy()
            # Only parse deadline if it exists in task_data   
            if "deadline" in task_data:
                task_data["deadline"] = date.fromisoformat(task_data["deadline"])
            task = task_factory_with_kwargs(**task_data)
            task_id = task.id
        else:
            task_id = scenario["task_id"]
        
        # Setup mocks based on scenario
        if scenario_key == "task_not_found":
            monkeypatch.setattr(task_service, "get_task_with_subtasks",
                              lambda task_id: scenario["mock_task_service_return"])
        
        elif scenario_key == "no_deadline":
            mock_assignees = [UserRead(**user_data) for user_data in scenario["assignees"]]
            monkeypatch.setattr(assignment_service, "list_assignees", lambda task_id: mock_assignees)
        
        elif scenario_key == "assignment_service_error":      
            error = scenario["assignment_service_error"]      
            monkeypatch.setattr(assignment_service, "list_assignees",
                              lambda task_id: (_ for _ in ()).throw(error))
        
        elif scenario_key == "email_service_error":
            mock_assignees = [UserRead(**user_data) for user_data in scenario["assignees"]]
            monkeypatch.setattr(assignment_service, "list_assignees", lambda task_id: mock_assignees)
            email_service = get_email_service()
            error = scenario["email_service_error"]
            monkeypatch.setattr(email_service, "send_email",  
                              lambda *args, **kwargs: (_ for _
 in ()).throw(error))
        
        # Execute test based on expected behavior
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
    
    # INT-REM-004 - Comprehensive success test with multiple assignees
    def test_overdue_reminder_comprehensive_success(self, db_session, patched_email_settings_tls, patched_smtp_tls, task_factory_with_kwargs, patched_mixed_assignees):
        """Test comprehensive success scenario including mixed email availability."""
        from datetime import date
        
        # Create task using mock data
        scenario = _reminder_data.MIXED_EMAIL_ASSIGNEES_SUCCESS
        task_data = scenario["task_data"].copy()
        task_data["deadline"] = date.fromisoformat(task_data["deadline"])
        task_data["title"] = "Overdue Task"  # Change title for overdue
        task = task_factory_with_kwargs(**task_data)
        
        # Call the function
        result = overdue_task_reminder(task.id)
        
        # Verify response
        assert result["success"] == scenario["expected_response"]["success"]
        assert result["recipients_count"] == scenario["expected_response"]["recipients_count"]
        assert "email_id" in result
        
        # Verify SMTP was called
        server = patched_smtp_tls
        server.starttls.assert_called_once()
        server.login.assert_called_once()
        server.send_message.assert_called_once()
        server.quit.assert_called_once()
    
    # INT-REM-005 - No recipients scenario
    @pytest.mark.parametrize("scenario_key", ["empty_assignees", "no_email_addresses"])
    def test_overdue_reminder_no_recipients(self, db_session, patched_email_settings_tls, patched_smtp_tls, task_factory_with_kwargs, monkeypatch, scenario_key):
        """Test early return when no assignees have email addresses."""
        import backend.src.services.task_assignment as assignment_service
        from datetime import date
        
        # Get scenario from mock data
        scenario = _reminder_data.ALL_NO_RECIPIENTS_SCENARIOS[scenario_key]
        
        # Create task using mock data
        task_data = scenario["task_data"].copy()
        task_data["deadline"] = date.fromisoformat(task_data["deadline"])
        task = task_factory_with_kwargs(**task_data)
        
        # Setup mock based on scenario
        if scenario["assignees"] == []:
            monkeypatch.setattr(assignment_service, "list_assignees", lambda task_id: [])
        else:
            mock_assignees = [
                _reminder_data.create_user_without_email(**user_data)
                for user_data in scenario["assignees"]        
            ]
            monkeypatch.setattr(assignment_service, "list_assignees", lambda task_id: mock_assignees)
        
        # Call the function
        result = overdue_task_reminder(task.id)
        
        # Verify early return response
        assert result["success"] == scenario["expected_response"]["success"]
        assert result["message"] == scenario["expected_response"]["message"]
        assert result["recipients_count"] == scenario["expected_response"]["recipients_count"]
        
        # Verify SMTP was not called
        server = patched_smtp_tls
        server.starttls.assert_not_called()
        server.login.assert_not_called()
        server.send_message.assert_not_called()
    
    # INT-REM-006 - Error scenarios
    @pytest.mark.parametrize("scenario_key", [
        "task_not_found",
        "no_deadline",
        "assignment_service_error",
        "email_service_error",
    ])
    def test_overdue_reminder_error_scenarios(self, db_session, patched_email_settings_tls, patched_smtp_tls,
                                            task_factory_with_kwargs, monkeypatch, scenario_key):
        """Test all error scenarios."""
        import backend.src.services.task_assignment as assignment_service
        import backend.src.services.task as task_service      
        from backend.src.services.email import get_email_service
        from backend.src.schemas.user import UserRead
        from fastapi import HTTPException
        from datetime import date
        
        # Get scenario from mock data
        scenario = _reminder_data.ALL_ERROR_SCENARIOS[scenario_key]
        
        # Create task (for scenarios that need it)
        task = None
        if scenario_key != "task_not_found":
            task_data = scenario.get("task_data", _reminder_data.OVERDUE_TASK).copy()
            # Only parse deadline if it exists in task_data   
            if "deadline" in task_data:
                task_data["deadline"] = date.fromisoformat(task_data["deadline"])
            task = task_factory_with_kwargs(**task_data)
            task_id = task.id
        else:
            task_id = scenario["task_id"]
        
        # Setup mocks based on scenario
        if scenario_key == "task_not_found":
            monkeypatch.setattr(task_service, "get_task_with_subtasks",
                              lambda task_id: scenario["mock_task_service_return"])
        
        elif scenario_key == "no_deadline":
            mock_assignees = [UserRead(**user_data) for user_data in scenario["assignees"]]
            monkeypatch.setattr(assignment_service, "list_assignees", lambda task_id: mock_assignees)
        
        elif scenario_key == "assignment_service_error":      
            error = scenario["assignment_service_error"]      
            monkeypatch.setattr(assignment_service, "list_assignees",
                              lambda task_id: (_ for _ in ()).throw(error))
        
        elif scenario_key == "email_service_error":
            mock_assignees = [UserRead(**user_data) for user_data in scenario["assignees"]]
            monkeypatch.setattr(assignment_service, "list_assignees", lambda task_id: mock_assignees)
            email_service = get_email_service()
            error = scenario["email_service_error"]
            monkeypatch.setattr(email_service, "send_email",  
                              lambda *args, **kwargs: (_ for _
 in ()).throw(error))
        
        # Execute test based on expected behavior
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
        import backend.src.services.task_assignment as assignment_service
        
        TestingSessionLocal = sessionmaker(
            bind=test_engine_backend_integration,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )
        task_service.SessionLocal = TestingSessionLocal
        assignment_service.SessionLocal = TestingSessionLocal
        
        with TestClient(app) as client:
            yield client
    
    def test_upcoming_reminder_api_success(self, api_client, db_session, patched_email_settings_tls, patched_smtp_tls, 
                                           task_factory_with_kwargs, patched_mixed_assignees):
        """Test upcoming reminder API endpoint returns 200 on success."""
        from datetime import date
        
        scenario = _reminder_data.MIXED_EMAIL_ASSIGNEES_SUCCESS
        task_data = scenario["task_data"].copy()
        task_data["deadline"] = date.fromisoformat(task_data["deadline"])
        task = task_factory_with_kwargs(**task_data)
        
        response = api_client.post(f"/kira/app/api/v1/task/{task.id}/notify-upcoming")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["recipients_count"] == scenario["expected_response"]["recipients_count"]
    
    def test_upcoming_reminder_api_valueerror_converted_to_404(self, api_client, db_session, patched_email_settings_tls, 
                                                               patched_smtp_tls, monkeypatch):
        """Test that ValueError from handler is converted to 404 by route."""
        import backend.src.handlers.task_handler as task_handler
        
        # Mock handler to raise ValueError
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
        
        # Mock handler to raise generic Exception
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
        
        # Mock handler to raise HTTPException
        def mock_upcoming_reminder(task_id):
            raise HTTPException(status_code=404, detail="Task not found")
        
        monkeypatch.setattr(task_handler, "upcoming_task_reminder", mock_upcoming_reminder)
        
        response = api_client.post("/kira/app/api/v1/task/999/notify-upcoming")
        assert response.status_code == 404
        assert response.json()["detail"] == "Task not found"
    
    def test_overdue_reminder_api_success(self, api_client, db_session, patched_email_settings_tls, patched_smtp_tls, 
                                         task_factory_with_kwargs, patched_mixed_assignees):
        """Test overdue reminder API endpoint returns 200 on success."""
        from datetime import date
        
        scenario = _reminder_data.MIXED_EMAIL_ASSIGNEES_SUCCESS
        task_data = scenario["task_data"].copy()
        task_data["deadline"] = date.fromisoformat(task_data["deadline"])
        task_data["title"] = "Overdue Task"
        task = task_factory_with_kwargs(**task_data)
        
        response = api_client.post(f"/kira/app/api/v1/task/{task.id}/notify-overdue")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["recipients_count"] == scenario["expected_response"]["recipients_count"]
    
    def test_overdue_reminder_api_valueerror_converted_to_404(self, api_client, db_session, patched_email_settings_tls, 
                                                              patched_smtp_tls, monkeypatch):
        """Test that ValueError from handler is converted to 404 by route."""
        import backend.src.handlers.task_handler as task_handler
        
        # Mock handler to raise ValueError
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
        
        # Mock handler to raise generic Exception
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
        
        # Mock handler to raise HTTPException
        def mock_overdue_reminder(task_id):
            raise HTTPException(status_code=404, detail="Task not found")
        
        monkeypatch.setattr(task_handler, "overdue_task_reminder", mock_overdue_reminder)
        
        response = api_client.post("/kira/app/api/v1/task/999/notify-overdue")
        assert response.status_code == 404
        assert response.json()["detail"] == "Task not found"
    
    # INT-REM-007 - Handler edge cases
    def test_upcoming_reminder_project_service_exception_silently_handled(self, db_session, patched_email_settings_tls, 
                                                                          patched_smtp_tls, task_factory_with_kwargs, 
                                                                          patched_mixed_assignees, monkeypatch):
        """Test that project service exceptions are silently handled (lines 140-141)."""
        from datetime import date
        import backend.src.services.project as project_service
        
        scenario = _reminder_data.MIXED_EMAIL_ASSIGNEES_SUCCESS
        task_data = scenario["task_data"].copy()
        task_data["deadline"] = date.fromisoformat(task_data["deadline"])
        task = task_factory_with_kwargs(**task_data)
        
        # Mock project service to raise exception
        monkeypatch.setattr(project_service, "get_project_by_id", lambda project_id: (_ for _ in ()).throw(Exception("Project service error")))
        
        # Should still succeed despite project service error
        result = upcoming_task_reminder(task.id)
        assert result["success"] is True
    
    def test_upcoming_reminder_email_service_returns_none(self, db_session, patched_email_settings_tls, 
                                                          patched_smtp_tls, task_factory_with_kwargs, 
                                                          patched_mixed_assignees, monkeypatch):
        """Test handler when email service returns None (line 181)."""
        from datetime import date
        from backend.src.services.email import get_email_service
        
        scenario = _reminder_data.MIXED_EMAIL_ASSIGNEES_SUCCESS
        task_data = scenario["task_data"].copy()
        task_data["deadline"] = date.fromisoformat(task_data["deadline"])
        task = task_factory_with_kwargs(**task_data)
        
        # Mock email service to return None
        email_service = get_email_service()
        monkeypatch.setattr(email_service, "send_email", lambda *args, **kwargs: None)
        
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            upcoming_task_reminder(task.id)
        assert exc_info.value.status_code == 500
        assert "Email service returned no response" in str(exc_info.value.detail)
    
    def test_upcoming_reminder_email_service_returns_failure(self, db_session, patched_email_settings_tls, 
                                                             patched_smtp_tls, task_factory_with_kwargs, 
                                                             patched_mixed_assignees, monkeypatch):
        """Test handler when email service returns success=False (lines 187-188)."""
        from datetime import date
        from backend.src.services.email import get_email_service, EmailResponse
        
        scenario = _reminder_data.MIXED_EMAIL_ASSIGNEES_SUCCESS
        task_data = scenario["task_data"].copy()
        task_data["deadline"] = date.fromisoformat(task_data["deadline"])
        task = task_factory_with_kwargs(**task_data)
        
        # Mock email service to return failure response
        email_service = get_email_service()
        monkeypatch.setattr(email_service, "send_email", lambda *args, **kwargs: EmailResponse(
            success=False,
            message="Email validation failed",
            recipients_count=0
        ))
        
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            upcoming_task_reminder(task.id)
        assert exc_info.value.status_code == 500
        assert "Error sending notification" in str(exc_info.value.detail)
        assert "Email validation failed" in str(exc_info.value.detail)
    
    def test_upcoming_reminder_unexpected_exception_handled(self, db_session, patched_email_settings_tls, 
                                                            patched_smtp_tls, task_factory_with_kwargs, 
                                                            patched_mixed_assignees, monkeypatch):
        """Test outer exception handler (lines 199-200)."""
        from datetime import date
        from backend.src.schemas.email import EmailRecipient
        
        scenario = _reminder_data.MIXED_EMAIL_ASSIGNEES_SUCCESS
        task_data = scenario["task_data"].copy()
        task_data["deadline"] = date.fromisoformat(task_data["deadline"])
        task = task_factory_with_kwargs(**task_data)
        
        # Mock EmailRecipient to raise an unexpected exception when creating recipients
        # This happens at line 159, outside inner try-except blocks
        original_email_recipient = EmailRecipient
        def mock_email_recipient(*args, **kwargs):
            raise AttributeError("Unexpected error creating email recipient")
        monkeypatch.setattr("backend.src.handlers.task_handler.EmailRecipient", mock_email_recipient)
        
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            upcoming_task_reminder(task.id)
        assert exc_info.value.status_code == 500
        assert "Unexpected error" in str(exc_info.value.detail)
    
    def test_overdue_reminder_project_service_exception_silently_handled(self, db_session, patched_email_settings_tls, 
                                                                         patched_smtp_tls, task_factory_with_kwargs, 
                                                                         patched_mixed_assignees, monkeypatch):
        """Test that project service exceptions are silently handled (lines 250-251)."""
        from datetime import date
        import backend.src.services.project as project_service
        
        scenario = _reminder_data.MIXED_EMAIL_ASSIGNEES_SUCCESS
        task_data = scenario["task_data"].copy()
        task_data["deadline"] = date.fromisoformat(task_data["deadline"])
        task_data["title"] = "Overdue Task"
        task = task_factory_with_kwargs(**task_data)
        
        # Mock project service to raise exception
        monkeypatch.setattr(project_service, "get_project_by_id", lambda project_id: (_ for _ in ()).throw(Exception("Project service error")))
        
        # Should still succeed despite project service error
        result = overdue_task_reminder(task.id)
        assert result["success"] is True
    
    def test_overdue_reminder_email_service_returns_none(self, db_session, patched_email_settings_tls, 
                                                         patched_smtp_tls, task_factory_with_kwargs, 
                                                         patched_mixed_assignees, monkeypatch):
        """Test handler when email service returns None (line 291)."""
        from datetime import date
        from backend.src.services.email import get_email_service
        
        scenario = _reminder_data.MIXED_EMAIL_ASSIGNEES_SUCCESS
        task_data = scenario["task_data"].copy()
        task_data["deadline"] = date.fromisoformat(task_data["deadline"])
        task_data["title"] = "Overdue Task"
        task = task_factory_with_kwargs(**task_data)
        
        # Mock email service to return None
        email_service = get_email_service()
        monkeypatch.setattr(email_service, "send_email", lambda *args, **kwargs: None)
        
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            overdue_task_reminder(task.id)
        assert exc_info.value.status_code == 500
        assert "Email service returned no response" in str(exc_info.value.detail)
    
    def test_overdue_reminder_email_service_returns_failure(self, db_session, patched_email_settings_tls, 
                                                            patched_smtp_tls, task_factory_with_kwargs, 
                                                            patched_mixed_assignees, monkeypatch):
        """Test handler when email service returns success=False (lines 297-298)."""
        from datetime import date
        from backend.src.services.email import get_email_service, EmailResponse
        
        scenario = _reminder_data.MIXED_EMAIL_ASSIGNEES_SUCCESS
        task_data = scenario["task_data"].copy()
        task_data["deadline"] = date.fromisoformat(task_data["deadline"])
        task_data["title"] = "Overdue Task"
        task = task_factory_with_kwargs(**task_data)
        
        # Mock email service to return failure response
        email_service = get_email_service()
        monkeypatch.setattr(email_service, "send_email", lambda *args, **kwargs: EmailResponse(
            success=False,
            message="Email validation failed",
            recipients_count=0
        ))
        
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            overdue_task_reminder(task.id)
        assert exc_info.value.status_code == 500
        assert "Error sending notification" in str(exc_info.value.detail)
        assert "Email validation failed" in str(exc_info.value.detail)
    
    def test_overdue_reminder_unexpected_exception_handled(self, db_session, patched_email_settings_tls, 
                                                          patched_smtp_tls, task_factory_with_kwargs, 
                                                          patched_mixed_assignees, monkeypatch):
        """Test outer exception handler (lines 309-310)."""
        from datetime import date
        from backend.src.schemas.email import EmailRecipient
        
        scenario = _reminder_data.MIXED_EMAIL_ASSIGNEES_SUCCESS
        task_data = scenario["task_data"].copy()
        task_data["deadline"] = date.fromisoformat(task_data["deadline"])
        task_data["title"] = "Overdue Task"
        task = task_factory_with_kwargs(**task_data)
        
        # Mock EmailRecipient to raise an unexpected exception when creating recipients
        # This happens at line 259, outside inner try-except blocks
        original_email_recipient = EmailRecipient
        def mock_email_recipient(*args, **kwargs):
            raise AttributeError("Unexpected error creating email recipient")
        monkeypatch.setattr("backend.src.handlers.task_handler.EmailRecipient", mock_email_recipient)
        
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            overdue_task_reminder(task.id)
        assert exc_info.value.status_code == 500
        assert "Unexpected error" in str(exc_info.value.detail)
