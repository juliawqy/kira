import logging
import smtplib
from datetime import datetime
from typing import List, Optional, Dict, Any
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import uuid

from ..config.email_config import get_email_settings
from ..schemas.email import EmailMessage, EmailRecipient, EmailResponse, EmailType
from ..templates.email_templates import EmailTemplates


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class EmailService:
    """Service for sending emails via FastMail SMTP"""
    
    def __init__(self):
        self.settings = get_email_settings()
        self.templates = EmailTemplates()
    
    def send_email(self, email_message: EmailMessage) -> EmailResponse:
        """Send an email message"""
        try:
            # Validate email settings
            if not self._validate_settings():
                return EmailResponse(
                    success=False,
                    message="Email settings are not properly configured",
                    recipients_count=0
                )
            
            # Prepare email content
            msg = self._prepare_message(email_message)
            
            # Send email via SMTP
            message_id = self._send_smtp_message(msg, email_message.recipients, email_message.cc, email_message.bcc)

            # Emit an explicit audit log with Message-ID and addressing for quick verification
            to_list = [r.email for r in (email_message.recipients or [])]
            cc_list = [r.email for r in (email_message.cc or [])]
            bcc_list = [r.email for r in (email_message.bcc or [])]
            subj = getattr(email_message.content, 'subject', None) if not isinstance(email_message.content, dict) else email_message.content.get('subject')
            logger.info(
                f"Email dispatched: msgid={message_id}, subject=\"{subj}\", to={to_list}, cc={cc_list}, bcc={bcc_list}")
            
            return EmailResponse(
                success=True,
                message="Email sent successfully",
                recipients_count=len(email_message.recipients),
                email_id=message_id,
            )
            
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return EmailResponse(
                success=False,
                message=f"Failed to send email: {str(e)}",
                recipients_count=0
            )
    
    def _prepare_message(self, email_message: EmailMessage) -> MIMEMultipart:
        """Prepare email message"""
        msg = MIMEMultipart('mixed')
        
        # Set headers
        # Always send from Fastmail configured address
        msg['From'] = f"{self.settings.fastmail_from_name} <{self.settings.fastmail_from_email}>"
        msg['To'] = ", ".join([recipient.email for recipient in email_message.recipients])
        msg['Subject'] = email_message.content.subject
        
        # Add CC if provided
        if email_message.cc:
            msg['Cc'] = ", ".join([recipient.email for recipient in email_message.cc])
        if email_message.bcc:
            # BCC is handled at SMTP send; not included in header for recipients
            pass
        
        # Prepare content into an 'alternative' part
        alternative = MIMEMultipart('alternative')
        text_content, html_content = self._prepare_content(email_message)
        
        # Add text part
        if text_content:
            text_part = MIMEText(text_content, 'plain', 'utf-8')
            alternative.attach(text_part)
        
        # Add HTML part
        if html_content:
            html_part = MIMEText(html_content, 'html', 'utf-8')
            alternative.attach(html_part)

        msg.attach(alternative)

        # Attachments support (optional)
        attachments = getattr(email_message, 'attachments', None)
        if attachments:
            for att in attachments:
                try:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(att['content'])
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', f"attachment; filename=\"{att.get('filename','attachment')}\"")
                    msg.attach(part)
                except Exception as e:
                    logger.warning(f"Failed to attach file {att}: {e}")
        
        return msg
    
    def _prepare_content(self, email_message: EmailMessage) -> tuple[Optional[str], Optional[str]]:
        """Prepare email content (text and HTML)"""
        content = email_message.content
        
        # If template is specified, render it
        if content.template_name and content.template_data:
            templates = self.templates.get_template_by_type(content.template_name)
            
            # Add common template data
            template_data = {
                **content.template_data,
                'app_name': self.settings.app_name,
                'app_url': self.settings.app_url,
                'update_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            text_content = self.templates.render_template(templates.get('text', ''), template_data)
            html_content = self.templates.render_template(templates.get('html', ''), template_data)
            
            return text_content, html_content
        
        # Use direct content
        return content.text_body, content.html_body
    
    def _send_smtp_message(self, msg: MIMEMultipart, recipients: List[EmailRecipient], cc: Optional[List[EmailRecipient]] = None, bcc: Optional[List[EmailRecipient]] = None) -> str:
        """Send message via SMTP and return a message id"""
        # Collect all recipient emails
        recipient_emails = [recipient.email for recipient in recipients]
        if cc:
            recipient_emails += [r.email for r in cc]
        if bcc:
            recipient_emails += [r.email for r in bcc]
        
        # Create SMTP connection
        if self.settings.use_ssl:
            # Use SSL directly (typically port 465)
            smtp = smtplib.SMTP_SSL(
                host=self.settings.fastmail_smtp_host,
                port=self.settings.fastmail_smtp_port,
                timeout=self.settings.timeout
            )
        else:
            # Use regular SMTP connection
            smtp = smtplib.SMTP(
                host=self.settings.fastmail_smtp_host,
                port=self.settings.fastmail_smtp_port,
                timeout=self.settings.timeout
            )
            
            # Start TLS if enabled (typically port 587)
            if self.settings.use_tls:
                smtp.starttls()
        
        try:
            # Authenticate
            smtp.login(self.settings.fastmail_username, self.settings.fastmail_password)
            
            # Send email
            smtp.send_message(
                msg,
                from_addr=self.settings.fastmail_from_email,
                to_addrs=recipient_emails,
            )
            # Construct a tracking id (if server didn't provide)
            message_id = msg.get('Message-ID') or f"kira-{uuid.uuid4()}@{self.settings.fastmail_from_email.split('@')[-1]}"
            if 'Message-ID' not in msg:
                msg.add_header('Message-ID', message_id)
            return message_id
            
        finally:
            # Close connection
            smtp.quit()
    
    def _validate_settings(self) -> bool:
        """Validate email settings"""
        required_settings = [
            self.settings.fastmail_smtp_host,
            self.settings.fastmail_username,
            self.settings.fastmail_password,
            self.settings.fastmail_from_email,
        ]
        
        return all(setting for setting in required_settings)
    
    def _get_task_notification_recipients(self, task_id: int) -> List[EmailRecipient]:
        """Get default notification recipients for a task (stub implementation)"""
        recipients: List[EmailRecipient] = []
        # Dev/test convenience: if explicitly configured, use the test recipient
        if getattr(self.settings, 'test_recipient_email', None):
            recipients.append(
                EmailRecipient(
                    email=self.settings.test_recipient_email, 
                    name=self.settings.test_recipient_name or "Test Recipient"
                )
            )
        return recipients
    
    def send_task_update_notification(
        self,
        task_id: int,
        task_title: str,
        updated_fields: List[str],
        previous_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        task_url: Optional[str] = None
    ) -> EmailResponse:
        """Send task update notification email to all stakeholders"""
        
        # TODO: In a real implementation, we would fetch task stakeholders from the database
        # For now, we'll use a default notification approach
        
        # Get default notification recipients (this would typically come from task assignees, project members, etc.)
        recipients = self._get_task_notification_recipients(task_id)
        
        if not recipients:
            logger.info(f"No recipients found for task {task_id} notification")
            return EmailResponse(
                success=True,
                message="No recipients configured for notifications",
                recipients_count=0
            )
        
        # Prepare template data
        template_data = {
            'task_id': task_id,
            'task_title': task_title,
            'updated_by': 'System',  # Default value since we don't have user context
            'updated_fields': updated_fields,
            'previous_values': previous_values or {},
            'new_values': new_values or {},
            'task_url': task_url or f"{self.settings.app_url}/tasks/{task_id}"
        }
        
        # Create email message
        email_message = EmailMessage(
            recipients=recipients,
            content={
                'subject': f"Task Updated: {task_title}",
                'template_name': 'task_updated',
                'template_data': template_data
            },
            email_type=EmailType.TASK_UPDATED
        )
        
        return self.send_email(email_message)


# Global email service instance
email_service = EmailService()


def get_email_service() -> EmailService:
    """Get email service instance"""
    return email_service