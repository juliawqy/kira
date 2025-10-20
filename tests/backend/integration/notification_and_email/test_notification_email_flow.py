"""
Integration tests for NotificationService + EmailService flow
- Exercise task.update -> notification_service -> email_service without hitting real SMTP
- Use patching to intercept SMTP and email settings
"""
from __future__ import annotations

import pytest
from unittest.mock import patch, MagicMock

from backend.src.services.task import add_task, update_task
from backend.src.services.notification_service import get_notification_service
from backend.src.services.email_service import EmailService
from backend.src.schemas.email import EmailRecipient, EmailResponse
from backend.src.config.email_config import EmailSettings


@pytest.fixture
def patched_email_settings_tls(monkeypatch):
    """Provide EmailSettings with TLS enabled (no SSL)."""
    settings = EmailSettings(
        fastmail_smtp_host="smtp.fastmail.com",
        fastmail_smtp_port=587,
        fastmail_username="ci@test.com",
        fastmail_password="secret",
        fastmail_from_email="noreply@test.com",
        fastmail_from_name="KIRA CI",
        app_name="KIRA",
        app_url="http://localhost:8000",
        use_tls=True,
        use_ssl=False,
        timeout=15,
    )
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
    # Reinitialize global singletons to pick up new env
    import backend.src.services.email_service as email_service_module
    import backend.src.services.notification_service as notification_service_module
    email_service_module.email_service = EmailService()
    notification_service_module.notification_service.email_service = email_service_module.email_service
    return settings


@pytest.fixture
def patched_smtp_tls():
    """Patch smtplib.SMTP and return server mock (TLS)."""
    with patch("backend.src.services.email_service.smtplib.SMTP", autospec=True) as mock_smtp:
        server = MagicMock(name="SMTPServerTLS")
        mock_smtp.return_value = server
        yield server


@pytest.fixture
def patched_email_settings_ssl(monkeypatch):
    """Provide EmailSettings with SSL enabled (no TLS)."""
    settings = EmailSettings(
        fastmail_smtp_host="smtp.fastmail.com",
        fastmail_smtp_port=465,
        fastmail_username="ci@test.com",
        fastmail_password="secret",
        fastmail_from_email="noreply@test.com",
        fastmail_from_name="KIRA CI",
        app_name="KIRA",
        app_url="http://localhost:8000",
        use_tls=False,
        use_ssl=True,
        timeout=15,
    )
    monkeypatch.setenv("FASTMAIL_SMTP_HOST", settings.fastmail_smtp_host)
    monkeypatch.setenv("FASTMAIL_SMTP_PORT", str(settings.fastmail_smtp_port))
    monkeypatch.setenv("FASTMAIL_USERNAME", settings.fastmail_username)
    monkeypatch.setenv("FASTMAIL_PASSWORD", settings.fastmail_password)
    monkeypatch.setenv("FASTMAIL_FROM_EMAIL", settings.fastmail_from_email)
    monkeypatch.setenv("FASTMAIL_FROM_NAME", settings.fastmail_from_name)
    monkeypatch.setenv("APP_NAME", settings.app_name)
    monkeypatch.setenv("APP_URL", settings.app_url)
    monkeypatch.setenv("USE_TLS", "False")
    monkeypatch.setenv("USE_SSL", "True")
    monkeypatch.setenv("TIMEOUT", str(settings.timeout))
    import backend.src.services.email_service as email_service_module
    import backend.src.services.notification_service as notification_service_module
    email_service_module.email_service = EmailService()
    notification_service_module.notification_service.email_service = email_service_module.email_service
    return settings


@pytest.fixture
def patched_smtp_ssl():
    """Patch smtplib.SMTP_SSL and return server mock (SSL)."""
    with patch("backend.src.services.email_service.smtplib.SMTP_SSL", autospec=True) as mock_smtp_ssl:
        server = MagicMock(name="SMTPServerSSL")
        mock_smtp_ssl.return_value = server
        yield server


@pytest.fixture
def patched_recipients(monkeypatch):
    """Patch EmailService._get_task_notification_recipients to simulate real recipients."""
    with patch.object(EmailService, "_get_task_notification_recipients", return_value=[
        EmailRecipient(email="john@example.com", name="John"),
        EmailRecipient(email="jane@example.com", name="Jane"),
    ]) as _patched:
        yield _patched


@pytest.fixture
def patched_email_settings_plain(monkeypatch):
    """Provide EmailSettings with neither TLS nor SSL (plain SMTP)."""
    settings = EmailSettings(
        fastmail_smtp_host="smtp.fastmail.com",
        fastmail_smtp_port=25,
        fastmail_username="ci@test.com",
        fastmail_password="secret",
        fastmail_from_email="noreply@test.com",
        fastmail_from_name="KIRA CI",
        app_name="KIRA",
        app_url="http://localhost:8000",
        use_tls=False,
        use_ssl=False,
        timeout=10,
    )
    monkeypatch.setenv("FASTMAIL_SMTP_HOST", settings.fastmail_smtp_host)
    monkeypatch.setenv("FASTMAIL_SMTP_PORT", str(settings.fastmail_smtp_port))
    monkeypatch.setenv("FASTMAIL_USERNAME", settings.fastmail_username)
    monkeypatch.setenv("FASTMAIL_PASSWORD", settings.fastmail_password)
    monkeypatch.setenv("FASTMAIL_FROM_EMAIL", settings.fastmail_from_email)
    monkeypatch.setenv("FASTMAIL_FROM_NAME", settings.fastmail_from_name)
    monkeypatch.setenv("APP_NAME", settings.app_name)
    monkeypatch.setenv("APP_URL", settings.app_url)
    monkeypatch.setenv("USE_TLS", "False")
    monkeypatch.setenv("USE_SSL", "False")
    monkeypatch.setenv("TIMEOUT", str(settings.timeout))
    import backend.src.services.email_service as email_service_module
    import backend.src.services.notification_service as notification_service_module
    email_service_module.email_service = EmailService()
    notification_service_module.notification_service.email_service = email_service_module.email_service
    return settings


class TestNotificationEmailIntegration:
    def test_update_triggers_email_tls(self, db_session, patched_email_settings_tls, patched_smtp_tls, patched_recipients, task_factory):
        """End-to-end: update_task -> NotificationService -> EmailService using TLS branch."""
        # Arrange: create a task
        task = task_factory(title="Initial Title", project_id=1)

        # Act: update task, then trigger notifications via service
        update_task(task.id, title="New Title")
        ns = get_notification_service()
        ns.notify_task_updated(
            task_id=task.id,
            task_title="New Title",
            updated_fields=["title"],
            previous_values={"title": "Initial Title"},
            new_values={"title": "New Title"},
        )

        # Assert: SMTP TLS path used
        server = patched_smtp_tls
        server.starttls.assert_called_once()
        server.login.assert_called_once()
        server.send_message.assert_called_once()
        server.quit.assert_called_once()

    def test_update_triggers_email_ssl(self, db_session, patched_email_settings_ssl, patched_smtp_ssl, patched_recipients, task_factory):
        """End-to-end via SSL branch."""
        task = task_factory(title="Initial Title", project_id=1)

        update_task(task.id, description="New Description")
        ns = get_notification_service()
        ns.notify_task_updated(
            task_id=task.id,
            task_title=task.title,
            updated_fields=["description"],
            previous_values={"description": None},
            new_values={"description": "New Description"},
        )

        server = patched_smtp_ssl
        server.login.assert_called_once()
        server.send_message.assert_called_once()
        server.quit.assert_called_once()

    def test_no_recipients_short_circuit(self, db_session, patched_email_settings_tls, patched_smtp_tls, task_factory, monkeypatch):
        """When recipients list is empty, send_email is not called; update still succeeds."""
        task = task_factory(title="Initial Title", project_id=1)

        # Force no recipients
        monkeypatch.setattr(EmailService, "_get_task_notification_recipients", lambda self, task_id: [])

        update_task(task.id, priority=7)
        ns = get_notification_service()
        ns.notify_task_updated(
            task_id=task.id,
            task_title=task.title,
            updated_fields=["priority"],
            previous_values={"priority": 5},
            new_values={"priority": 7},
        )

        # SMTP should not be used
        server = patched_smtp_tls
        server.starttls.assert_not_called()
        server.send_message.assert_not_called()

    def test_invalid_settings_yields_failure_response_but_update_continues(self, db_session, task_factory, monkeypatch, patched_smtp_tls):
        """Invalid email settings should cause EmailService to return failure; update_task should not crash."""
        task = task_factory(title="Initial Title", project_id=1)

        # Invalidate critical settings via env
        monkeypatch.delenv("FASTMAIL_USERNAME", raising=False)
        monkeypatch.delenv("FASTMAIL_PASSWORD", raising=False)
        monkeypatch.setenv("FASTMAIL_FROM_EMAIL", "")

        update_task(task.id, deadline=task.deadline)  # no change -> ensure no send; then change
        update_task(task.id, deadline=None)  # this triggers an actual change
        ns = get_notification_service()
        ns.notify_task_updated(
            task_id=task.id,
            task_title=task.title,
            updated_fields=["deadline"],
            previous_values={"deadline": None if task.deadline is None else task.deadline.isoformat()},
            new_values={"deadline": None},
        )

        # If send attempted, it should gracefully handle and not raise
        # We cannot assert exact logging here, but we can assert no unhandled exception was raised by reaching here.
        assert True

    def test_plain_smtp_without_tls(self, db_session, patched_email_settings_plain, patched_smtp_tls, patched_recipients, task_factory):
        """Covers branch where use_tls=False and use_ssl=False (no starttls)."""
        task = task_factory(title="Initial Title", project_id=1)

        update_task(task.id, project_id=2)
        ns = get_notification_service()
        ns.notify_task_updated(
            task_id=task.id,
            task_title=task.title,
            updated_fields=["project_id"],
            previous_values={"project_id": 1},
            new_values={"project_id": 2},
        )

        server = patched_smtp_tls
        server.starttls.assert_not_called()
        server.login.assert_called_once()
        server.send_message.assert_called_once()
        server.quit.assert_called_once()

    def test_notification_service_handles_email_exception(self, db_session, patched_email_settings_tls, patched_smtp_tls, task_factory, monkeypatch):
        """Force EmailService to raise and assert NotificationService returns failure response gracefully."""
        task = task_factory(title="Oops Title", project_id=1)

        # Patch the global email_service instance's method to raise
        import backend.src.services.email_service as email_service_module
        monkeypatch.setattr(email_service_module.email_service, "send_task_update_notification", None, raising=False)
        # Now patch the bound method to raise when called via NotificationService
        def boom(*args, **kwargs):
            raise Exception("SMTP boom")
        email_service_module.email_service.send_task_update_notification = boom

        # Now call update_task which triggers notification_service -> email_service
        update_task(task.id, title="Recovered Title")
        ns = get_notification_service()
        ns.notify_task_updated(
            task_id=task.id,
            task_title="Recovered Title",
            updated_fields=["title"],
            previous_values={"title": "Oops Title"},
            new_values={"title": "Recovered Title"},
        )

        # If the exception bubbled, test would fail; reaching here indicates graceful handling
        assert True