"""
Email service for sending emails via FastMail SMTP
"""
import asyncio
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

from ..config.email_config import get_email_settings
from ..schemas.email import EmailMessage, EmailRecipient, EmailResponse, EmailType
from ..templates.email_templates import EmailTemplates


logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails via FastMail SMTP"""
    
    def __init__(self):
        self.settings = get_email_settings()
        self.templates = EmailTemplates()
    
    async def send_email(self, email_message: EmailMessage) -> EmailResponse:
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
            msg = await self._prepare_message(email_message)
            
            # Send email via SMTP
            await self._send_smtp_message(msg, email_message.recipients)
            
            logger.info(f"Email sent successfully to {len(email_message.recipients)} recipients")
            
            return EmailResponse(
                success=True,
                message="Email sent successfully",
                recipients_count=len(email_message.recipients)
            )
            
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return EmailResponse(
                success=False,
                message=f"Failed to send email: {str(e)}",
                recipients_count=0
            )
    
    async def _prepare_message(self, email_message: EmailMessage) -> MIMEMultipart:
        """Prepare email message"""
        msg = MIMEMultipart('alternative')
        
        # Set headers
        msg['From'] = f"{self.settings.fastmail_from_name} <{self.settings.fastmail_from_email}>"
        msg['To'] = ", ".join([recipient.email for recipient in email_message.recipients])
        msg['Subject'] = email_message.content.subject
        
        # Add CC if provided
        if email_message.cc:
            msg['Cc'] = ", ".join([recipient.email for recipient in email_message.cc])
        
        # Prepare content
        text_content, html_content = await self._prepare_content(email_message)
        
        # Add text part
        if text_content:
            text_part = MIMEText(text_content, 'plain', 'utf-8')
            msg.attach(text_part)
        
        # Add HTML part
        if html_content:
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
        
        return msg
    
    async def _prepare_content(self, email_message: EmailMessage) -> tuple[Optional[str], Optional[str]]:
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
    
    async def _send_smtp_message(self, msg: MIMEMultipart, recipients: List[EmailRecipient]):
        """Send message via SMTP"""
        # Collect all recipient emails
        recipient_emails = [recipient.email for recipient in recipients]
        
        # Create SMTP connection
        smtp = aiosmtplib.SMTP(
            hostname=self.settings.fastmail_smtp_host,
            port=self.settings.fastmail_smtp_port,
            use_tls=self.settings.use_tls,
            timeout=self.settings.timeout
        )
        
        try:
            # Connect and authenticate
            await smtp.connect()
            await smtp.login(self.settings.fastmail_username, self.settings.fastmail_password)
            
            # Send email
            await smtp.send_message(
                msg,
                sender=self.settings.fastmail_from_email,
                recipients=recipient_emails
            )
            
        finally:
            # Close connection
            await smtp.quit()
    
    def _validate_settings(self) -> bool:
        """Validate email settings"""
        required_settings = [
            self.settings.fastmail_smtp_host,
            self.settings.fastmail_username,
            self.settings.fastmail_password,
            self.settings.fastmail_from_email,
        ]
        
        return all(setting for setting in required_settings)
    
    async def send_task_update_notification(
        self,
        task_id: int,
        task_title: str,
        updated_by: str,
        updated_fields: List[str],
        assignee_email: str,
        assignee_name: Optional[str] = None,
        previous_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        task_url: Optional[str] = None
    ) -> EmailResponse:
        """Send task update notification email"""
        
        # Prepare template data
        template_data = {
            'task_id': task_id,
            'task_title': task_title,
            'updated_by': updated_by,
            'updated_fields': updated_fields,
            'assignee_name': assignee_name,
            'previous_values': previous_values or {},
            'new_values': new_values or {},
            'task_url': task_url or f"{self.settings.app_url}/tasks/{task_id}"
        }
        
        # Create email message
        email_message = EmailMessage(
            recipients=[EmailRecipient(email=assignee_email, name=assignee_name)],
            content={
                'subject': f"Task Updated: {task_title}",
                'template_name': 'task_updated',
                'template_data': template_data
            },
            email_type=EmailType.TASK_UPDATED
        )
        
        return await self.send_email(email_message)


# Global email service instance
email_service = EmailService()


def get_email_service() -> EmailService:
    """Get email service instance"""
    return email_service