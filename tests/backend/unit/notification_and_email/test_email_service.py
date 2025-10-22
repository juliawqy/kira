import pytest
from unittest.mock import Mock, patch
import smtplib
from email.mime.multipart import MIMEMultipart

from backend.src.services.email_service import EmailService, get_email_service
from backend.src.schemas.email import EmailRecipient, EmailResponse

class TestEmailService:

    # UNI-124/001
    def test_init_email_service(self, email_service_with_patches):
        assert email_service_with_patches.settings is not None
        assert email_service_with_patches.templates is not None

    # UNI-124/002
    def test_validate_settings_success(self, email_service_with_patches):
        result = email_service_with_patches._validate_settings()
        assert result is True

    # UNI-124/003
    def test_validate_settings_failure(self, invalid_email_settings_obj):
        with patch('backend.src.services.email_service.get_email_settings', return_value=invalid_email_settings_obj):
            email_service = EmailService()
            result = email_service._validate_settings()
            assert result is False

    # UNI-124/004
    def test_send_smtp_message_success(self, patched_smtp, email_service_with_patches, single_recipient_list):
        mock_server = patched_smtp
        msg = MIMEMultipart()
        recipients = [EmailRecipient(**single_recipient_list[0])]
        
        email_service_with_patches._send_smtp_message(msg, recipients)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with(
            email_service_with_patches.settings.fastmail_username,
            email_service_with_patches.settings.fastmail_password
        )
        mock_server.send_message.assert_called_once()
        mock_server.quit.assert_called_once()

    # UNI-124/005
    def test_send_smtp_message_without_tls(self, patched_smtp, patched_email_settings, single_recipient_list):
        patched_email_settings.use_tls = False
        patched_email_settings.use_ssl = False
        patched_email_settings.fastmail_smtp_port = 25
        patched_email_settings.timeout = 30

        email_service = EmailService()
        mock_server = patched_smtp
        msg = MIMEMultipart()
        recipients = [EmailRecipient(**single_recipient_list[0])]

        email_service._send_smtp_message(msg, recipients)
        mock_server.starttls.assert_not_called()
        mock_server.login.assert_called_once()
        mock_server.send_message.assert_called_once()
        mock_server.quit.assert_called_once()

    # UNI-124/006
    def test_send_smtp_message_with_ssl(self, patched_smtp_ssl, patched_email_settings, single_recipient_list):
        patched_email_settings.use_ssl = True
        patched_email_settings.use_tls = False
        patched_email_settings.fastmail_smtp_port = 465
        patched_email_settings.timeout = 30

        email_service = EmailService()
        mock_server = patched_smtp_ssl
        msg = MIMEMultipart()
        recipients = [EmailRecipient(**single_recipient_list[0])]

        email_service._send_smtp_message(msg, recipients)
        mock_server.login.assert_called_once()
        mock_server.send_message.assert_called_once()
        mock_server.quit.assert_called_once()

    # UNI-124/007
    def test_send_smtp_message_with_tls(self, patched_smtp, patched_email_settings, single_recipient_list):
        patched_email_settings.use_ssl = False
        patched_email_settings.use_tls = True
        patched_email_settings.fastmail_smtp_port = 587
        patched_email_settings.timeout = 30

        email_service = EmailService()
        mock_server = patched_smtp
        msg = MIMEMultipart()
        recipients = [EmailRecipient(**single_recipient_list[0])]

        email_service._send_smtp_message(msg, recipients)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once()
        mock_server.send_message.assert_called_once()
        mock_server.quit.assert_called_once()

    # UNI-124/008
    def test_send_smtp_message_includes_cc_in_envelope(self, patched_smtp, patched_email_settings, single_recipient_list):
        patched_email_settings.use_ssl = False
        patched_email_settings.use_tls = True
        email_service = EmailService()
        mock_server = patched_smtp
        msg = MIMEMultipart()
        recipients = [EmailRecipient(**single_recipient_list[0])]
        cc = [EmailRecipient(email="cc1@example.com"), EmailRecipient(email="cc2@example.com")]

        email_service._send_smtp_message(msg, recipients, cc=cc)
        assert mock_server.send_message.call_count == 1
        _, kwargs = mock_server.send_message.call_args
        to_addrs = kwargs.get('to_addrs', [])
        assert cc[0].email in to_addrs
        assert all(c.email in to_addrs for c in cc)

    # UNI-124/009
    @patch('backend.src.services.email_service.smtplib.SMTP')
    def test_send_smtp_message_failure(self, mock_smtp, email_service_with_patches):
        mock_smtp.side_effect = smtplib.SMTPException("SMTP Error")
        
        msg = MIMEMultipart()
        recipients = [EmailRecipient(email="test@example.com")]
        
        with pytest.raises(smtplib.SMTPException):
            email_service_with_patches._send_smtp_message(msg, recipients)

    # UNI-124/010
    def test_prepare_message_with_html_and_text(self, email_service_with_patches, sample_email_message):
        msg = email_service_with_patches._prepare_message(sample_email_message)
        assert msg['Subject'] == sample_email_message.content.subject
        assert msg['From'] == f"{email_service_with_patches.settings.fastmail_from_name} <{email_service_with_patches.settings.fastmail_from_email}>"
        assert msg['To'] == sample_email_message.recipients[0].email
        assert msg.is_multipart()
        alt = None
        for p in msg.get_payload():
            if p.get_content_type() == 'multipart/alternative':
                alt = p
                break
        assert alt is not None
        types = [part.get_content_type() for part in alt.get_payload()]
        assert 'text/plain' in types
        assert 'text/html' in types

    # UNI-124/011
    def test_prepare_message_with_template(self, email_service_with_patches, email_message_task_update):
        msg = email_service_with_patches._prepare_message(email_message_task_update)
        assert msg['Subject'] == email_message_task_update.content.subject
        assert msg.is_multipart()

    # UNI-124/012
    def test_prepare_message_with_html_content_only(self, email_service_with_patches, html_only_email_message):
        msg = email_service_with_patches._prepare_message(html_only_email_message)
        assert msg['Subject'] == html_only_email_message.content.subject
        assert msg.is_multipart()
        parts = msg.get_payload()
        alt_parts = []
        for p in parts:
            if p.get_content_type() == 'multipart/alternative':
                alt_parts.extend(p.get_payload())
        html_parts = [part for part in alt_parts if part.get_content_type() == 'text/html']
        assert len(html_parts) == 1
        html_decoded = html_parts[0].get_payload(decode=True).decode('utf-8')
        assert html_only_email_message.content.html_body in html_decoded

    # UNI-124/013
    def test_prepare_message_with_text_only(self, email_service_with_patches, text_only_email_message):
        msg = email_service_with_patches._prepare_message(text_only_email_message)
        assert msg.is_multipart()
        alt = None
        for p in msg.get_payload():
            if p.get_content_type() == 'multipart/alternative':
                alt = p
                break
        assert alt is not None
        parts = alt.get_payload()
        assert len(parts) == 1
        assert parts[0].get_content_type() == 'text/plain'
        text_decoded = parts[0].get_payload(decode=True).decode('utf-8')
        assert text_only_email_message.content.text_body in text_decoded

    # UNI-124/014
    def test_prepare_message_cc_handling(self, email_service_with_patches, email_message_with_cc_bcc):
        msg = email_service_with_patches._prepare_message(email_message_with_cc_bcc)
        assert msg['Cc'] is not None
        assert 'cc@example.com' in msg['Cc']

    # UNI-124/015
    def test_send_smtp_message_generates_message_id_when_absent(self, patched_smtp, email_service_with_patches, single_recipient_list):
        msg = MIMEMultipart('mixed')
        recipients = [EmailRecipient(**single_recipient_list[0])]
        returned_id = email_service_with_patches._send_smtp_message(msg, recipients)
        assert msg['Message-ID'] == returned_id
        assert returned_id.startswith('kira-') and '@' in returned_id

    # UNI-124/016
    def test_send_smtp_message_uses_existing_message_id(self, patched_smtp, email_service_with_patches, single_recipient_list, custom_message_id):
        msg = MIMEMultipart('mixed')
        msg.add_header('Message-ID', custom_message_id)
        recipients = [EmailRecipient(**single_recipient_list[0])]
        returned_id = email_service_with_patches._send_smtp_message(msg, recipients)
        assert returned_id == custom_message_id

    # UNI-124/017
    def test_send_task_update_notification_with_recipients_calls_send_email(self, email_service_with_patches, monkeypatch, simple_task_id, unit_test_email):
        """Exercise happy path where recipients exist and send_email is invoked."""
        monkeypatch.setattr(EmailService, "_get_task_notification_recipients", lambda self, task_id: [EmailRecipient(email=unit_test_email)])
        called = {"count": 0}
        original = email_service_with_patches.send_email
        def spy(msg):
            called["count"] += 1
            # Return a success-like response to avoid dependency on SMTP
            return EmailResponse(success=True, message="Email sent successfully", recipients_count=len(msg.recipients))
        monkeypatch.setattr(email_service_with_patches, 'send_email', spy)
        resp = email_service_with_patches.send_task_update_notification(
            task_id=simple_task_id,
            task_title='Title',
            updated_fields=['title'],
            previous_values={'title': 'Old'},
            new_values={'title': 'New'},
        )
        assert called["count"] == 1
        assert resp.success is True

    # UNI-124/018
    @patch.object(EmailService, '_validate_settings')
    @patch.object(EmailService, '_prepare_message')
    @patch.object(EmailService, '_send_smtp_message')
    def test_send_email_success(self, mock_send_smtp, mock_prepare, mock_validate, email_service_with_patches, sample_email_message):
        mock_validate.return_value = True
        mock_prepare.return_value = Mock()
        mock_send_smtp.return_value = "kira-123@example.com"
        result = email_service_with_patches.send_email(sample_email_message)
        assert result.success is True
        assert result.message == "Email sent successfully"
        assert result.recipients_count == 1
        assert result.email_id is not None

    # UNI-124/019
    @patch.object(EmailService, '_validate_settings')
    def test_send_email_invalid_settings(self, mock_validate, email_service_with_patches, sample_email_message):
        mock_validate.return_value = False
        
        result = email_service_with_patches.send_email(sample_email_message)
        
        assert result.success is False
        assert result.message == "Email settings are not properly configured"
        assert result.recipients_count == 0

    # UNI-124/020
    @patch.object(EmailService, '_validate_settings')
    @patch.object(EmailService, '_prepare_message')
    @patch.object(EmailService, '_send_smtp_message')
    def test_send_email_smtp_failure(self, mock_send_smtp, mock_prepare, mock_validate, email_service_with_patches, sample_email_message):
        mock_validate.return_value = True
        mock_prepare.return_value = Mock()
        mock_send_smtp.side_effect = Exception("SMTP Error")
        
        result = email_service_with_patches.send_email(sample_email_message)
        
        assert result.success is False
        assert "SMTP Error" in result.message
        assert result.recipients_count == 0

    # UNI-124/021
    @patch.object(EmailService, '_validate_settings')
    @patch.object(EmailService, '_prepare_message')
    def test_send_email_prepare_failure(self, mock_prepare, mock_validate, email_service_with_patches, sample_email_message):
        mock_validate.return_value = True
        mock_prepare.side_effect = RuntimeError("template render failed")
        result = email_service_with_patches.send_email(sample_email_message)
        assert result.success is False
        assert "Failed to send email:" in result.message

    # UNI-124/022
    def test_get_task_notification_recipients_from_settings(self, email_service_with_patches):
        recipients = email_service_with_patches._get_task_notification_recipients(123)
        assert isinstance(recipients, list)
        assert len(recipients) == 1

    # UNI-124/023
    def test_get_task_notification_recipients_with_test_override(self, email_service_with_patches):
        svc = email_service_with_patches
        svc.settings.test_recipient_email = "unit+test@example.com"
        svc.settings.test_recipient_name = "Unit Test"

        recipients = svc._get_task_notification_recipients(task_id=42)

        assert isinstance(recipients, list)
        assert len(recipients) == 1
        assert recipients[0].email == "unit+test@example.com"
        assert recipients[0].name == "Unit Test"

    # UNI-124/024
    @patch.object(EmailService, '_get_task_notification_recipients')
    def test_send_task_update_notification_no_recipients(self, mock_get_recipients, email_service_with_patches):
        mock_get_recipients.return_value = []
        
        result = email_service_with_patches.send_task_update_notification(
            task_id=123,
            task_title="Test Task",
            updated_fields=["title"]
        )
        
        assert result.success is True
        assert result.message == "No recipients configured for notifications"
        assert result.recipients_count == 0

    # UNI-124/025
    @patch.object(EmailService, '_get_task_notification_recipients')
    @patch.object(EmailService, 'send_email')
    def test_send_task_update_notification_with_recipients(self, mock_send_email, mock_get_recipients, email_service_with_patches, recipients_list):
        mock_get_recipients.return_value = [EmailRecipient(**recipients_list[0])]
        mock_send_email.return_value = EmailResponse(success=True, message="Email sent", recipients_count=1)
        
        result = email_service_with_patches.send_task_update_notification(
            task_id=123,
            task_title="Test Task",
            updated_fields=["title"],
            previous_values={"title": "Old Title"},
            new_values={"title": "New Title"}
        )
        
        assert result.success is True
        assert result.recipients_count == 1
        mock_send_email.assert_called_once()

    # UNI-124/026
    def test_get_email_service_singleton(self):
        service1 = get_email_service()
        service2 = get_email_service()
        
        assert service1 is service2
        assert isinstance(service1, EmailService)


class TestEmailServiceEdgeCases:
    # UNI-124/027
    @patch('backend.src.services.email_service.get_email_settings')
    def test_email_service_init_with_exception(self, mock_get_settings):
        mock_get_settings.side_effect = Exception("Settings error")
        
        with pytest.raises(Exception):
            EmailService()

    # UNI-124/028
    def test_prepare_message_with_cc_only(self, email_message_with_cc_bcc, email_service_with_patches):
        msg = email_service_with_patches._prepare_message(email_message_with_cc_bcc)
        
        assert msg['Cc'] is not None
        assert "cc@example.com" in msg['Cc']

    # UNI-124/029
    def test_prepare_message_multiple_recipients(self, email_message_multiple_recipients, email_service_with_patches):
        msg = email_service_with_patches._prepare_message(email_message_multiple_recipients)
        
        to_header = msg['To']
        assert "john.doe@fastmail.com" in to_header
        assert "jane.smith@fastmail.com" in to_header