from __future__ import annotations

import pytest
from unittest.mock import patch, MagicMock
import os
from pathlib import Path


def _load_mock_module(file_name: str):
    import importlib.util
    mock_dir = Path(__file__).parents[3] / 'mock_data' / 'notification_email'
    file_path = mock_dir / file_name
    spec = importlib.util.spec_from_file_location(f"mock_{file_name.replace('.', '_')}", str(file_path))
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader, f"Failed to load mock module: {file_path}"
    spec.loader.exec_module(module)  # type: ignore[attr-defined]
    return module


_mock_base = Path(__file__).parents[3] / 'mock_data' / 'notification_email'
_email_config = _load_mock_module('email_config_data.py')
_email_service_data = _load_mock_module('email_service_data.py')
_email_templates_data = _load_mock_module('email_templates_data.py')
_notifications_email_templates_data = _load_mock_module('notifications_email_templates_data.py')
_notification_service_data = _load_mock_module('notification_service_data.py')


@pytest.fixture(autouse=True)
def email_env_vars():
    env = _email_config.EMAIL_ENV
    with patch.dict(os.environ, env):
        yield


@pytest.fixture
def patched_email_settings():
    from backend.src.config.email_config import EmailSettings
    settings_dict = _email_config.EMAIL_SETTINGS
    settings_obj = EmailSettings(**settings_dict)
    with patch('backend.src.services.email.get_email_settings', return_value=settings_obj):
        yield settings_obj


@pytest.fixture
def email_service_with_patches(patched_email_settings):
    from backend.src.services.email import EmailService
    return EmailService()

@pytest.fixture
def patched_smtp():
    with patch('backend.src.services.email.smtplib.SMTP', autospec=True) as mock_smtp:
        server = MagicMock(name='SMTPServer')
        mock_smtp.return_value = server
        yield server


@pytest.fixture
def patched_smtp_ssl():
    with patch('backend.src.services.email.smtplib.SMTP_SSL', autospec=True) as mock_smtp_ssl:
        server = MagicMock(name='SMTPSSLServer')
        mock_smtp_ssl.return_value = server
        yield server

@pytest.fixture
def single_recipient_list():
    return _email_service_data.SINGLE_EMAIL_RECIPIENT


@pytest.fixture
def recipients_list():
    return _email_service_data.VALID_EMAIL_RECIPIENTS


@pytest.fixture
def sample_email_message():
    from backend.src.schemas.email import EmailMessage, EmailRecipient, EmailContent, EmailType
    data = _email_service_data.VALID_EMAIL_MESSAGE_SIMPLE
    return EmailMessage(
        recipients=[EmailRecipient(**r) for r in data["recipients"]],
        content=EmailContent(**data["content"]),
        email_type=EmailType.GENERAL_NOTIFICATION,
    )


@pytest.fixture
def email_message_task_update():
    from backend.src.schemas.email import EmailMessage, EmailRecipient, EmailContent, EmailType
    data = _email_service_data.VALID_EMAIL_MESSAGE_TASK_UPDATE
    return EmailMessage(
        recipients=[EmailRecipient(**r) for r in data["recipients"]],
        content=EmailContent(**data["content"]),
        email_type=EmailType.TASK_UPDATED,
    )


@pytest.fixture
def html_only_email_message():
    from backend.src.schemas.email import EmailMessage, EmailRecipient, EmailContent, EmailType
    content = dict(_email_service_data.VALID_EMAIL_CONTENT_HTML_TEXT)
    content["text_body"] = None
    return EmailMessage(
        recipients=[EmailRecipient(**_email_service_data.SINGLE_EMAIL_RECIPIENT[0])],
        content=EmailContent(**content),
        email_type=EmailType.GENERAL_NOTIFICATION,
    )

@pytest.fixture
def text_only_email_message():
    from backend.src.schemas.email import EmailMessage, EmailRecipient, EmailContent, EmailType
    content = dict(_email_service_data.VALID_EMAIL_CONTENT_HTML_TEXT)
    content["html_body"] = None
    return EmailMessage(
        recipients=[EmailRecipient(**_email_service_data.SINGLE_EMAIL_RECIPIENT[0])],
        content=EmailContent(**content),
        email_type=EmailType.GENERAL_NOTIFICATION,
    )

@pytest.fixture
def notification_valid_update():
    return _notification_service_data.VALID_TASK_NOTIFICATION


@pytest.fixture
def notification_minimal_update():
    return _notification_service_data.MINIMAL_TASK_NOTIFICATION


@pytest.fixture
def notification_large_update():
    return _notification_service_data.LARGE_DATA_NOTIFICATION

@pytest.fixture
def notification_single_field_update():
    return _notification_service_data.SINGLE_FIELD_UPDATE_NOTIFICATION

@pytest.fixture
def notification_multiple_fields_update():
    return _notification_service_data.MULTIPLE_FIELDS_UPDATE_NOTIFICATION

@pytest.fixture
def notification_empty_updated_fields():
    return _notification_service_data.EMPTY_UPDATED_FIELDS_NOTIFICATION

@pytest.fixture
def notification_null_values():
    return _notification_service_data.NULL_VALUES_NOTIFICATION

@pytest.fixture
def notification_unicode():
    return _notification_service_data.UNICODE_NOTIFICATION_DATA

@pytest.fixture
def notification_special_chars():
    return _notification_service_data.SPECIAL_CHARACTERS_NOTIFICATION

# --- Direct notify_activity parameter fixtures ---

@pytest.fixture
def notify_activity_success_params():
    return _notification_service_data.NOTIFY_ACTIVITY_SUCCESS_PARAMS

@pytest.fixture
def notify_activity_failure_params():
    return _notification_service_data.NOTIFY_ACTIVITY_FAILURE_PARAMS

@pytest.fixture
def notify_activity_no_recipients_params():
    return _notification_service_data.NOTIFY_ACTIVITY_NO_RECIPIENTS_PARAMS

@pytest.fixture
def notify_activity_invalid_type_params():
    return _notification_service_data.NOTIFY_ACTIVITY_INVALID_TYPE_PARAMS

@pytest.fixture
def notify_activity_comment_missing_user_params():
    return _notification_service_data.NOTIFY_ACTIVITY_COMMENT_MISSING_USER_PARAMS

@pytest.fixture
def notify_activity_comment_with_user_params():
    return _notification_service_data.NOTIFY_ACTIVITY_COMMENT_WITH_USER_PARAMS

@pytest.fixture
def custom_event_activity_params():
    return _notification_service_data.CUSTOM_EVENT_ACTIVITY_PARAMS

@pytest.fixture
def template_basic_data():
    return _email_templates_data.BASIC_TEMPLATE_DATA


@pytest.fixture
def template_text_data():
    return _email_templates_data.BASIC_TEMPLATE_DATA


@pytest.fixture
def template_null_assignee_data():
    return _email_templates_data.NULL_ASSIGNEE_TEMPLATE_DATA


@pytest.fixture
def template_empty_fields_data():
    return _email_templates_data.EMPTY_FIELDS_TEMPLATE_DATA


@pytest.fixture
def template_multi_field_data():
    return _email_templates_data.MULTIPLE_FIELD_CHANGES_DATA


@pytest.fixture
def template_special_chars_data():
    return _email_templates_data.SPECIAL_CHARS_TEMPLATE_DATA


@pytest.fixture
def template_long_content_data():
    return _email_templates_data.LONG_CONTENT_TEMPLATE_DATA
@pytest.fixture
def render_data_basic():
    return _notifications_email_templates_data.RENDER_DATA_BASIC

@pytest.fixture
def render_data_missing_assignee():
    return _notifications_email_templates_data.RENDER_DATA_MISSING_ASSIGNEE

@pytest.fixture
def render_data_empty_fields():
    return _notifications_email_templates_data.RENDER_DATA_EMPTY_FIELDS

@pytest.fixture
def render_data_multiple_changes():
    return _notifications_email_templates_data.RENDER_DATA_MULTIPLE_CHANGES

@pytest.fixture
def render_data_special_chars():
    return _notifications_email_templates_data.RENDER_DATA_SPECIAL_CHARS

@pytest.fixture
def render_data_long_content():
    return _notifications_email_templates_data.RENDER_DATA_LONG_CONTENT

@pytest.fixture
def render_data_none_values():
    return _notifications_email_templates_data.RENDER_DATA_NONE_VALUES

@pytest.fixture
def render_data_numeric_boolean():
    return _notifications_email_templates_data.RENDER_DATA_NUMERIC_BOOLEAN

@pytest.fixture
def render_data_performance():
    return _notifications_email_templates_data.RENDER_DATA_PERFORMANCE
@pytest.fixture
def invalid_email_settings_obj():
    from backend.src.config.email_config import EmailSettings
    return EmailSettings(
        fastmail_smtp_host="",
        fastmail_smtp_port=587,
        fastmail_username="",
        fastmail_password="",
        fastmail_from_email="",
        fastmail_from_name=_email_config.EMAIL_SETTINGS.get("fastmail_from_name", "Kira Test App"),
        app_name=_email_config.EMAIL_SETTINGS.get("app_name", "KIRA Test System"),
        app_url=_email_config.EMAIL_SETTINGS.get("app_url", "http://localhost:8000"),
    )


@pytest.fixture
def email_message_with_cc_bcc():
    from backend.src.schemas.email import EmailMessage, EmailRecipient, EmailContent, EmailType
    data = _email_service_data.VALID_EMAIL_MESSAGE_WITH_CC_BCC
    return EmailMessage(
        recipients=[EmailRecipient(**r) for r in data["recipients"]],
        content=EmailContent(**data["content"]),
        cc=[EmailRecipient(**r) for r in data.get("cc", [])],
        email_type=EmailType.GENERAL_NOTIFICATION,
    )


@pytest.fixture
def email_message_multiple_recipients():
    from backend.src.schemas.email import EmailMessage, EmailRecipient, EmailContent, EmailType
    recipients = [EmailRecipient(**r) for r in _email_service_data.VALID_EMAIL_RECIPIENTS]
    content = _email_service_data.VALID_EMAIL_CONTENT_HTML_TEXT
    return EmailMessage(
        recipients=recipients,
        content=EmailContent(**content),
        email_type=EmailType.GENERAL_NOTIFICATION,
    )


@pytest.fixture
def task_update_notification_data():
    return _email_service_data.VALID_TASK_UPDATE_NOTIFICATION


@pytest.fixture
def minimal_task_update_notification_data():
    return _email_service_data.MINIMAL_TASK_UPDATE_NOTIFICATION

# --- Expose common constants as fixtures ---

@pytest.fixture
def custom_message_id():
    return _email_service_data.CUSTOM_MESSAGE_ID

@pytest.fixture
def simple_task_id():
    return _email_service_data.SIMPLE_TASK_ID

@pytest.fixture
def unit_test_email():
    return _email_service_data.UNIT_TEST_EMAIL