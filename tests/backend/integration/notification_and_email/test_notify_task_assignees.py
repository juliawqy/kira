from __future__ import annotations

import pytest
from unittest.mock import patch, MagicMock

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

# Load notify_task_assignees specific mock data (following existing pattern)
_notify_assignees_mock_path = Path(__file__).parents[3] / 'mock_data' / 'notification_email' / 'notify_task_assignees_data.py'
_notify_spec = importlib.util.spec_from_file_location('notify_assignees_mock_data', str(_notify_assignees_mock_path))
_notify_assignees_data = importlib.util.module_from_spec(_notify_spec)
assert _notify_spec and _notify_spec.loader, f"Failed to load notify assignees mock data: {_notify_assignees_mock_path}"
_notify_spec.loader.exec_module(_notify_assignees_data)


@pytest.fixture
def patched_email_settings_tls(monkeypatch):
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
    import backend.src.services.notification as notification_service_module
    email_service_module.email_service = EmailService()
    notification_service_module.notification_service.email_service = email_service_module.email_service
    return settings


@pytest.fixture
def patched_smtp_tls():
    with patch("backend.src.services.email.smtplib.SMTP", autospec=True) as mock_smtp:
        server = MagicMock(name="SMTPServerTLS")
        mock_smtp.return_value = server
        yield server


@pytest.fixture
def patched_assignees_with_emails(monkeypatch):
    """Mock assignees with valid email addresses (following patched_recipients pattern)."""
    import backend.src.services.task_assignment as assignment_service
    from backend.src.schemas.user import UserRead
    
    mock_assignees = [
        UserRead(**assignee_data) for assignee_data in _notify_assignees_data.ASSIGNEES_WITH_EMAILS
    ]
    monkeypatch.setattr(assignment_service, "list_assignees", lambda task_id: mock_assignees)
    return mock_assignees


@pytest.fixture
def patched_single_assignee(monkeypatch):
    """Mock single assignee with email (following patched_recipients pattern)."""
    import backend.src.services.task_assignment as assignment_service
    from backend.src.schemas.user import UserRead
    
    mock_assignee = [
        UserRead(**_notify_assignees_data.SINGLE_ASSIGNEE_WITH_EMAIL[0])
    ]
    monkeypatch.setattr(assignment_service, "list_assignees", lambda task_id: mock_assignee)
    return mock_assignee


@pytest.fixture
def patched_mixed_assignees(monkeypatch):
    """Mock mixed assignees - some with emails, some without (following existing pattern)."""
    import backend.src.services.task_assignment as assignment_service
    
    scenario = _notify_assignees_data.MIXED_EMAIL_ASSIGNEES_SUCCESS
    mixed_assignees = []
    
    # Add users with emails
    for user_data in scenario["assignees_with_emails"]:
        mixed_assignees.append(_notify_assignees_data.create_user_with_email(**user_data))
    
    # Add users without emails
    for user_data in scenario["assignees_without_emails"]:
        mixed_assignees.append(_notify_assignees_data.create_user_without_email(**user_data))
    
    monkeypatch.setattr(assignment_service, "list_assignees", lambda task_id: mixed_assignees)
    return mixed_assignees


@pytest.fixture
def patched_empty_assignees(monkeypatch):
    """Mock empty assignees list (following existing pattern)."""
    import backend.src.services.task_assignment as assignment_service
    
    monkeypatch.setattr(assignment_service, "list_assignees", lambda task_id: [])
    return []


@pytest.fixture
def patched_assignees_without_emails(monkeypatch):
    """Mock assignees without email attributes (following existing pattern)."""
    import backend.src.services.task_assignment as assignment_service
    
    scenario = _notify_assignees_data.NO_RECIPIENTS_SCENARIO_NO_EMAILS
    mock_assignees = [
        _notify_assignees_data.create_user_without_email(**user_data) 
        for user_data in scenario["assignees"]
    ]
    
    monkeypatch.setattr(assignment_service, "list_assignees", lambda task_id: mock_assignees)
    return mock_assignees


class TestNotifyTaskAssigneesIntegration:
    """Minimal integration tests for notify_task_assignees endpoint - 100% coverage with fewest tests."""
    
    # INT-125/001 - Comprehensive success test with mixed email availability  
    def test_notify_assignees_comprehensive_success(self, db_session, patched_email_settings_tls, patched_smtp_tls, task_factory, patched_mixed_assignees):
        """Test comprehensive success scenario including mixed email availability and default parameters."""
        from backend.src.api.v1.routes.task_route import notify_task_assignees
        
        # Create task using mock data (following existing pattern)
        scenario = _notify_assignees_data.MIXED_EMAIL_ASSIGNEES_SUCCESS
        task = task_factory(**scenario["task_data"])
        
        # Test 1: Custom message and alert type
        result = notify_task_assignees(task.id, "Mixed email test", "task_assgn")
        
        # Verify response using mock expectations (following existing pattern)
        assert result["success"] == scenario["expected_response"]["success"]
        assert result["recipients_count"] == scenario["expected_response"]["recipients_count"]
        assert "email_id" in result
        
        # Verify SMTP was called (following existing SMTP verification pattern)
        server = patched_smtp_tls
        server.starttls.assert_called_once()
        server.login.assert_called_once()
        server.send_message.assert_called_once()
        server.quit.assert_called_once()
        
        # Reset mock for second test
        server.reset_mock()
        
        # Test 2: Default parameters (covers default parameter path)
        default_scenario = _notify_assignees_data.SUCCESS_SCENARIO_DEFAULT_PARAMETERS
        result2 = notify_task_assignees(task.id)  # Uses defaults
        
        # Verify defaults work
        assert result2["success"] == default_scenario["expected_response"]["success"]
        assert result2["recipients_count"] == scenario["expected_response"]["recipients_count"]  # Same assignees
        assert "email_id" in result2
        
        # Verify SMTP was called again (following existing pattern)
        for call_method in default_scenario["expected_smtp_calls"]:
            getattr(server, call_method).assert_called_once()
    
    # INT-125/002 - No recipients scenario (following existing no recipients pattern)
    def test_notify_assignees_no_recipients(self, db_session, patched_email_settings_tls, patched_smtp_tls, task_factory, monkeypatch):
        """Test early return when no assignees have email addresses."""
        from backend.src.api.v1.routes.task_route import notify_task_assignees
        import backend.src.services.task_assignment as assignment_service
        
        # Test scenarios from mock data (following existing pattern)
        test_scenarios = [
            _notify_assignees_data.NO_RECIPIENTS_SCENARIO_EMPTY,
            _notify_assignees_data.NO_RECIPIENTS_SCENARIO_NO_EMAILS,
        ]
        
        for scenario in test_scenarios:
            # Create task using mock data
            task = task_factory(**scenario["task_data"])
            
            # Setup mock based on scenario
            if scenario["assignees"] == []:
                # Empty assignees
                monkeypatch.setattr(assignment_service, "list_assignees", lambda task_id: [])
            else:
                # Assignees without emails
                mock_assignees = [
                    _notify_assignees_data.create_user_without_email(**user_data) 
                    for user_data in scenario["assignees"]
                ]
                monkeypatch.setattr(assignment_service, "list_assignees", lambda task_id: mock_assignees)
            
            # Call the function
            result = notify_task_assignees(task.id, "Test message")
            
            # Verify early return response using mock expectations (following existing pattern)
            assert result["success"] == scenario["expected_response"]["success"]
            assert result["message"] == scenario["expected_response"]["message"]
            assert result["recipients_count"] == scenario["expected_response"]["recipients_count"]
            
            # Verify SMTP was not called (following existing verification pattern)
            server = patched_smtp_tls
            server.starttls.assert_not_called()
            server.login.assert_not_called()
            server.send_message.assert_not_called()
    
    # INT-125/003 - All error scenarios using mock data (following existing parametrized pattern)
    @pytest.mark.parametrize("scenario_key", [
        "task_not_found",
        "invalid_alert_type", 
        "assignment_service_error",
        "notification_service_error",
        "comment_validation_error",
    ])
    def test_notify_assignees_error_scenarios(self, db_session, patched_email_settings_tls, patched_smtp_tls, 
                                            task_factory, monkeypatch, scenario_key):
        """Test all error scenarios using centralized mock data (following existing pattern)."""
        from backend.src.api.v1.routes.task_route import notify_task_assignees
        import backend.src.services.task_assignment as assignment_service
        import backend.src.services.task as task_service
        from backend.src.services.notification import get_notification_service
        from backend.src.schemas.user import UserRead
        from fastapi import HTTPException
        
        # Get scenario from mock data (following existing pattern)
        scenario = _notify_assignees_data.ALL_ERROR_SCENARIOS[scenario_key]
        
        # Create task (for scenarios that need it) using mock data
        task = None
        if scenario_key != "task_not_found":
            task_data = scenario.get("task_data", _notify_assignees_data.NOTIFY_ASSIGNEES_TASK_INITIAL)
            task = task_factory(**task_data)
            task_id = task.id
        else:
            task_id = scenario["task_id"]
        
        # Setup mocks based on scenario (following existing setup patterns)
        if scenario_key == "task_not_found":
            # Mock task service to return None
            monkeypatch.setattr(task_service, "get_task_with_subtasks", 
                              lambda task_id: scenario["mock_task_service_return"])
            
        elif scenario_key == "invalid_alert_type":
            # Valid assignees, invalid alert type
            mock_assignees = [UserRead(**user_data) for user_data in scenario["assignees"]]
            monkeypatch.setattr(assignment_service, "list_assignees", lambda task_id: mock_assignees)
            
        elif scenario_key == "assignment_service_error":
            # Mock assignment service to raise error
            error = scenario["assignment_service_error"]
            monkeypatch.setattr(assignment_service, "list_assignees", 
                              lambda task_id: (_ for _ in ()).throw(error))
            
        elif scenario_key == "notification_service_error":
            # Valid assignees, but notification service fails
            mock_assignees = [UserRead(**user_data) for user_data in scenario["assignees"]]
            monkeypatch.setattr(assignment_service, "list_assignees", lambda task_id: mock_assignees)
            
            # Mock notification service to raise exception
            notification_service = get_notification_service()
            error = scenario["notification_service_error"]
            monkeypatch.setattr(notification_service, "notify_activity", 
                              lambda *args, **kwargs: (_ for _ in ()).throw(error))
            
        elif scenario_key == "comment_validation_error":
            # Valid assignees, comment alert type (should fail validation gracefully)
            mock_assignees = [UserRead(**user_data) for user_data in scenario["assignees"]]
            monkeypatch.setattr(assignment_service, "list_assignees", lambda task_id: mock_assignees)
        
        # Execute test based on expected behavior (following existing pattern)
        if "expected_response" in scenario:
            # Validation error - returns response, doesn't raise exception
            result = notify_task_assignees(task_id, scenario["message"], scenario["alert_type"])
            assert result["success"] == scenario["expected_response"]["success"]
            assert result["recipients_count"] == scenario["expected_response"]["recipients_count"]
            for message_part in scenario["expected_response"]["message_contains"]:
                assert message_part in result["message"]
        else:
            # All other scenarios raise HTTPException
            with pytest.raises(HTTPException) as exc_info:
                notify_task_assignees(task_id, scenario["message"], scenario.get("alert_type", "task_update"))
            
            # Verify error details using mock expectations (following existing pattern)
            expected = scenario["expected_exception"]
            assert exc_info.value.status_code == expected["status_code"]
            for message_part in expected["detail_contains"]:
                assert message_part in str(exc_info.value.detail)
