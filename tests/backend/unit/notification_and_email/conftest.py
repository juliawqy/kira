# tests/backend/unit/notification&email/conftest.py
from __future__ import annotations

import pytest
from unittest.mock import Mock, patch, MagicMock
import os


@pytest.fixture
def mock_email_settings():
    """Mock email settings for testing"""
    return {
        "fastmail_smtp_host": "smtp.fastmail.com",
        "fastmail_smtp_port": 587,
        "fastmail_username": "test@fastmail.com", 
        "fastmail_password": "test_password",
        "fastmail_from_email": "test@fastmail.com",
        "fastmail_from_name": "KIRA Test App",
        "app_name": "KIRA Test System",
        "app_url": "http://localhost:8000",
        "use_tls": True,
        "use_ssl": False,
        "timeout": 60
    }


@pytest.fixture
def mock_email_recipients():
    """Mock email recipients for testing"""
    return [
        {"email": "john.doe@example.com", "name": "John Doe"},
        {"email": "jane.smith@example.com", "name": "Jane Smith"}
    ]


@pytest.fixture
def mock_task_notification_data():
    """Mock task notification data for testing"""
    return {
        "task_id": 123,
        "task_title": "Test Task Update",
        "updated_fields": ["title", "priority"],
        "previous_values": {"title": "Old Title", "priority": "Low"},
        "new_values": {"title": "New Title", "priority": "High"}
    }


@pytest.fixture
def mock_template_data():
    """Mock template rendering data for testing"""
    return {
        "app_name": "KIRA",
        "assignee_name": "Test User",
        "task_title": "Test Task",
        "task_id": 123,
        "updated_by": "Test Admin",
        "update_date": "2025-10-15",
        "updated_fields": ["title"],
        "previous_values": {"title": "Old Title"},
        "new_values": {"title": "New Title"}
    }


@pytest.fixture(autouse=True)
def mock_email_env_vars():
    """Automatically mock email environment variables for all tests"""
    test_env = {
        'FASTMAIL_SMTP_HOST': 'smtp.testmail.com',
        'FASTMAIL_SMTP_PORT': '587', 
        'FASTMAIL_USERNAME': 'test@testmail.com',
        'FASTMAIL_PASSWORD': 'test_password',
        'FASTMAIL_FROM_EMAIL': 'test@testmail.com',
        'FASTMAIL_FROM_NAME': 'Test KIRA App',
        'APP_NAME': 'KIRA Test System',
        'APP_URL': 'http://localhost:3000',
        'USE_TLS': 'True',
        'USE_SSL': 'False',
        'TIMEOUT': '60'
    }
    with patch.dict(os.environ, test_env):
        yield


@pytest.fixture
def mock_successful_email_response():
    """Mock successful email response"""
    return {
        "success": True,
        "message": "Email sent successfully", 
        "recipients_count": 1
    }


@pytest.fixture
def mock_failed_email_response():
    """Mock failed email response"""
    return {
        "success": False,
        "message": "SMTP server connection failed",
        "recipients_count": 0
    }


# --- Reusable patch fixtures (MagicMock + patch) ---

@pytest.fixture
def patched_smtp():
    """Patch smtplib.SMTP and return the MagicMock server instance.
    Usage in tests:
        def test_something(patched_smtp):
            server = patched_smtp
            ... assertions on server.starttls/login/send_message/quit
    """
    with patch('backend.src.services.email_service.smtplib.SMTP', autospec=True) as mock_smtp:
        server = MagicMock(name='SMTPServer')
        mock_smtp.return_value = server
        yield server


@pytest.fixture
def patched_smtp_ssl():
    """Patch smtplib.SMTP_SSL and return the MagicMock SSL server instance."""
    with patch('backend.src.services.email_service.smtplib.SMTP_SSL', autospec=True) as mock_smtp_ssl:
        server = MagicMock(name='SMTPSSLServer')
        mock_smtp_ssl.return_value = server
        yield server


@pytest.fixture
def patched_email_settings(mock_email_settings):
    """Patch get_email_settings to return a concrete EmailSettings object from dict.
    Provides flexibility to tweak flags (use_tls/use_ssl) per test via copy & overrides.
    """
    from backend.src.config.email_config import EmailSettings
    settings_obj = EmailSettings(**mock_email_settings)
    with patch('backend.src.services.email_service.get_email_settings', return_value=settings_obj):
        yield settings_obj


@pytest.fixture
def email_service_with_patches(patched_email_settings):
    """Construct EmailService with patched settings ready for tests."""
    from backend.src.services.email_service import EmailService
    return EmailService()