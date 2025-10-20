"""
Unit tests for EmailService
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import smtplib
from email.mime.multipart import MIMEMultipart

from backend.src.services.email_service import EmailService, get_email_service
from backend.src.schemas.email import EmailMessage, EmailRecipient, EmailResponse, EmailType, EmailContent
from backend.src.config.email_config import EmailSettings


class TestEmailService:
    """Test cases for EmailService class"""

    # Use shared fixtures from conftest: email_service_with_patches, patched_smtp, patched_smtp_ssl, patched_email_settings

    @pytest.fixture
    def sample_email_message(self):
        """Sample email message for testing"""
        return EmailMessage(
            recipients=[EmailRecipient(email="test@example.com", name="Test User")],
            content=EmailContent(
                subject="Test Subject",
                html_body="<p>Test HTML body</p>",
                text_body="Test text body"
            ),
            email_type=EmailType.GENERAL_NOTIFICATION
        )

    def test_init_email_service(self, email_service_with_patches):
        """Test EmailService initialization"""
        assert email_service_with_patches.settings is not None
        assert email_service_with_patches.templates is not None

    def test_validate_settings_success(self, email_service_with_patches):
        """Test settings validation with valid settings"""
        result = email_service_with_patches._validate_settings()
        assert result is True

    def test_validate_settings_failure(self):
        """Test settings validation with invalid settings"""
        mock_settings = EmailSettings(
            fastmail_smtp_host="",
            fastmail_smtp_port=587,
            fastmail_username="",
            fastmail_password="",
            fastmail_from_email="",
            fastmail_from_name="Test App",
            app_name="Test System",
            app_url="http://localhost:8000"
        )
        
        with patch('backend.src.services.email_service.get_email_settings', return_value=mock_settings):
            email_service = EmailService()
            result = email_service._validate_settings()
            assert result is False

    def test_send_smtp_message_success(self, patched_smtp, email_service_with_patches):
        """Test successful SMTP message sending"""
        # Setup mocks (server instance provided by fixture)
        mock_server = patched_smtp

        msg = MIMEMultipart()
        recipients = [EmailRecipient(email="test@example.com", name="Test User")]
        
        # Test the method
        email_service_with_patches._send_smtp_message(msg, recipients)
        
        # Verify SMTP calls
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with(
            email_service_with_patches.settings.fastmail_username,
            email_service_with_patches.settings.fastmail_password
        )
        mock_server.send_message.assert_called_once()
        mock_server.quit.assert_called_once()

    def test_send_smtp_message_without_tls(self, patched_smtp, patched_email_settings):
        """Test SMTP message sending without TLS to cover both TLS branches"""
        # Toggle TLS off on patched settings and create a fresh service
        patched_email_settings.use_tls = False
        patched_email_settings.use_ssl = False
        patched_email_settings.fastmail_smtp_port = 25
        patched_email_settings.timeout = 30

        email_service = EmailService()

        mock_server = patched_smtp

        msg = MIMEMultipart()
        recipients = [EmailRecipient(email="test@example.com", name="Test User")]

        # Test the method
        email_service._send_smtp_message(msg, recipients)

        # Verify SMTP calls
        mock_server.starttls.assert_not_called()
        mock_server.login.assert_called_once()
        mock_server.send_message.assert_called_once()
        mock_server.quit.assert_called_once()

    def test_send_smtp_message_with_ssl(self, patched_smtp_ssl, patched_email_settings):
        """Test SMTP message sending with SSL to cover SSL connection branch"""
        # Configure patched settings for SSL
        patched_email_settings.use_ssl = True
        patched_email_settings.use_tls = False
        patched_email_settings.fastmail_smtp_port = 465
        patched_email_settings.timeout = 30

        email_service = EmailService()
        mock_server = patched_smtp_ssl
        
        msg = MIMEMultipart()
        recipients = [EmailRecipient(email="test@example.com")]
        
        # Test the method
        email_service._send_smtp_message(msg, recipients)
        
        # Verify SSL SMTP interactions
        mock_server.login.assert_called_once()
        mock_server.send_message.assert_called_once()
        mock_server.quit.assert_called_once()

    def test_send_smtp_message_with_tls(self, patched_smtp, patched_email_settings):
        """Test SMTP message sending with TLS to cover TLS branch"""
        # Configure patched settings for TLS
        patched_email_settings.use_ssl = False
        patched_email_settings.use_tls = True
        patched_email_settings.fastmail_smtp_port = 587
        patched_email_settings.timeout = 30

        email_service = EmailService()
        mock_server = patched_smtp
        
        msg = MIMEMultipart()
        recipients = [EmailRecipient(email="test@example.com")]
        
        # Test the method
        email_service._send_smtp_message(msg, recipients)
        
        # Verify TLS was called
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once()
        mock_server.send_message.assert_called_once()
        mock_server.quit.assert_called_once()

    @patch('backend.src.services.email_service.smtplib.SMTP')
    def test_send_smtp_message_failure(self, mock_smtp, email_service_with_patches):
        """Test SMTP message sending failure"""
        # Setup mock to raise exception
        mock_smtp.side_effect = smtplib.SMTPException("SMTP Error")
        
        msg = MIMEMultipart()
        recipients = [EmailRecipient(email="test@example.com")]
        
        # Test that exception is raised
        with pytest.raises(smtplib.SMTPException):
            email_service_with_patches._send_smtp_message(msg, recipients)

    def test_prepare_message_with_html_and_text(self, email_service_with_patches, sample_email_message):
        """Test message preparation with both HTML and text content"""
        msg = email_service_with_patches._prepare_message(sample_email_message)
        
        assert msg['Subject'] == "Test Subject"
        assert msg['From'] == f"{email_service_with_patches.settings.fastmail_from_name} <{email_service_with_patches.settings.fastmail_from_email}>"
        assert msg['To'] == "test@example.com"
        assert msg.is_multipart()

    def test_prepare_message_with_template(self, email_service_with_patches):
        """Test message preparation with template"""
        email_message = EmailMessage(
            recipients=[EmailRecipient(email="test@example.com", name="Test User")],
            content=EmailContent(
                subject="Test Subject",
                template_name="task_updated",
                template_data={
                    "task_id": 123,
                    "task_title": "Test Task",
                    "updated_by": "Test User",
                    "updated_fields": ["title"],
                    "assignee_name": "Test User"
                }
            ),
            email_type=EmailType.TASK_UPDATED
        )
        
        msg = email_service_with_patches._prepare_message(email_message)
        
        assert msg['Subject'] == "Test Subject"
        assert msg.is_multipart()

    def test_prepare_message_with_html_content_only(self, email_service_with_patches):
        """Test message preparation with only HTML content to cover HTML attachment lines"""
        email_message = EmailMessage(
            recipients=[EmailRecipient(email="test@example.com")],
            content=EmailContent(
                subject="HTML Only Test",
                html_body="<h1>HTML Content</h1><p>This is HTML only</p>"
                # No text_body - this will test the html_content branch
            ),
            email_type=EmailType.GENERAL_NOTIFICATION
        )
        
        msg = email_service_with_patches._prepare_message(email_message)
        
        assert msg['Subject'] == "HTML Only Test"
        assert msg.is_multipart()

        # Verify HTML part was attached
        parts = msg.get_payload()
        html_parts = [part for part in parts if part.get_content_type() == 'text/html']
        assert len(html_parts) == 1
        # Decode base64 payload before assertion
        html_decoded = html_parts[0].get_payload(decode=True).decode('utf-8')
        assert "<h1>HTML Content</h1>" in html_decoded

    @patch.object(EmailService, '_validate_settings')
    @patch.object(EmailService, '_prepare_message')
    @patch.object(EmailService, '_send_smtp_message')
    def test_send_email_success(self, mock_send_smtp, mock_prepare, mock_validate, email_service_with_patches, sample_email_message):
        """Test successful email sending"""
        # Setup mocks
        mock_validate.return_value = True
        mock_prepare.return_value = Mock()
        mock_send_smtp.return_value = None
        
        result = email_service_with_patches.send_email(sample_email_message)
        
        assert result.success is True
        assert result.message == "Email sent successfully"
        assert result.recipients_count == 1

    @patch.object(EmailService, '_validate_settings')
    def test_send_email_invalid_settings(self, mock_validate, email_service_with_patches, sample_email_message):
        """Test email sending with invalid settings"""
        mock_validate.return_value = False
        
        result = email_service_with_patches.send_email(sample_email_message)
        
        assert result.success is False
        assert result.message == "Email settings are not properly configured"
        assert result.recipients_count == 0

    @patch.object(EmailService, '_validate_settings')
    @patch.object(EmailService, '_prepare_message')
    @patch.object(EmailService, '_send_smtp_message')
    def test_send_email_smtp_failure(self, mock_send_smtp, mock_prepare, mock_validate, email_service_with_patches, sample_email_message):
        """Test email sending with SMTP failure"""
        # Setup mocks
        mock_validate.return_value = True
        mock_prepare.return_value = Mock()
        mock_send_smtp.side_effect = Exception("SMTP Error")
        
        result = email_service_with_patches.send_email(sample_email_message)
        
        assert result.success is False
        assert "SMTP Error" in result.message
        assert result.recipients_count == 0

    def test_get_task_notification_recipients_default(self, email_service_with_patches):
        """Test getting task notification recipients with default implementation"""
        recipients = email_service_with_patches._get_task_notification_recipients(123)
        
        # Should return empty list by default (as per current implementation)
        assert isinstance(recipients, list)
        assert len(recipients) == 0

    def test_get_task_notification_recipients_with_test_override(self, email_service_with_patches):
        """When test_recipient_email is configured, service returns one default recipient (covers append branch)."""
        svc = email_service_with_patches
        # Configure test recipient on the existing settings to hit the append path
        svc.settings.test_recipient_email = "unit+test@example.com"
        svc.settings.test_recipient_name = "Unit Test"

        recipients = svc._get_task_notification_recipients(task_id=42)

        assert isinstance(recipients, list)
        assert len(recipients) == 1
        assert recipients[0].email == "unit+test@example.com"
        assert recipients[0].name == "Unit Test"

    @patch.object(EmailService, '_get_task_notification_recipients')
    def test_send_task_update_notification_no_recipients(self, mock_get_recipients, email_service_with_patches):
        """Test task update notification with no recipients"""
        mock_get_recipients.return_value = []
        
        result = email_service_with_patches.send_task_update_notification(
            task_id=123,
            task_title="Test Task",
            updated_fields=["title"]
        )
        
        assert result.success is True
        assert result.message == "No recipients configured for notifications"
        assert result.recipients_count == 0

    @patch.object(EmailService, '_get_task_notification_recipients')
    @patch.object(EmailService, 'send_email')
    def test_send_task_update_notification_with_recipients(self, mock_send_email, mock_get_recipients, email_service_with_patches):
        """Test task update notification with recipients"""
        # Setup mocks
        mock_get_recipients.return_value = [EmailRecipient(email="test@example.com", name="Test User")]
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

    def test_get_email_service_singleton(self):
        """Test that get_email_service returns the same instance"""
        service1 = get_email_service()
        service2 = get_email_service()
        
        assert service1 is service2
        assert isinstance(service1, EmailService)


class TestEmailServiceEdgeCases:
    """Test edge cases and error conditions for EmailService"""

    @patch('backend.src.services.email_service.get_email_settings')
    def test_email_service_init_with_exception(self, mock_get_settings):
        """Test EmailService initialization when settings fail to load"""
        mock_get_settings.side_effect = Exception("Settings error")
        
        with pytest.raises(Exception):
            EmailService()

    def test_prepare_message_with_cc_bcc(self):
        """Test message preparation with CC and BCC recipients"""
        mock_settings = EmailSettings(
            fastmail_smtp_host="smtp.test.com",
            fastmail_smtp_port=587,
            fastmail_username="test@test.com",
            fastmail_password="password",
            fastmail_from_email="test@test.com",
            fastmail_from_name="Test App",
            app_name="Test System",
            app_url="http://localhost:8000"
        )
        
        with patch('backend.src.services.email_service.get_email_settings', return_value=mock_settings):
            email_service = EmailService()
            
            email_message = EmailMessage(
                recipients=[EmailRecipient(email="to@example.com")],
                content=EmailContent(subject="Test", text_body="Test body"),
                cc=[EmailRecipient(email="cc@example.com")],
                bcc=[EmailRecipient(email="bcc@example.com")]
            )
            
            msg = email_service._prepare_message(email_message)
            
            # CC should be in headers
            assert msg['Cc'] is not None
            assert "cc@example.com" in msg['Cc']
            
            # BCC should NOT be in headers (that's the point of BCC - blind carbon copy)
            # So we don't check for BCC in the message headers

    def test_prepare_message_multiple_recipients(self):
        """Test message preparation with multiple recipients"""
        mock_settings = EmailSettings(
            fastmail_smtp_host="smtp.test.com",
            fastmail_smtp_port=587,
            fastmail_username="test@test.com",
            fastmail_password="password",
            fastmail_from_email="test@test.com",
            fastmail_from_name="Test App",
            app_name="Test System",
            app_url="http://localhost:8000"
        )
        
        with patch('backend.src.services.email_service.get_email_settings', return_value=mock_settings):
            email_service = EmailService()
            
            email_message = EmailMessage(
                recipients=[
                    EmailRecipient(email="user1@example.com", name="User One"),
                    EmailRecipient(email="user2@example.com", name="User Two")
                ],
                content=EmailContent(subject="Test", text_body="Test body")
            )
            
            msg = email_service._prepare_message(email_message)
            
            # Should contain both recipients
            to_header = msg['To']
            assert "user1@example.com" in to_header
            assert "user2@example.com" in to_header