import logging
import smtplib
from backend.src.database.db_setup import SessionLocal
from datetime import datetime
from typing import List, Optional, Dict, Any
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import uuid
from ..config.email_config import get_email_settings
from ..schemas.email import EmailMessage, EmailRecipient, EmailResponse, EmailType
from ..templates.email_templates import EmailTemplates


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class EmailService:
    
    def __init__(self):
        self.settings = get_email_settings()
        self.templates = EmailTemplates()
    
    def send_email(self, email_message: EmailMessage) -> EmailResponse:
        try:
            if not self._validate_settings():
                return EmailResponse(
                    success=False,
                    message="Email settings are not properly configured",
                    recipients_count=0
                )

            msg = self._prepare_message(email_message)

            message_id = self._send_smtp_message(
                msg,
                email_message.recipients,
                email_message.cc,
            )

            to_list = [r.email for r in (email_message.recipients or [])]
            cc_list = [r.email for r in (email_message.cc or [])]
            subj = getattr(email_message.content, 'subject', None) if not isinstance(email_message.content, dict) else email_message.content.get('subject')
            logger.info(
                f"Email dispatched: msgid={message_id}, subject=\"{subj}\", to={to_list}, cc={cc_list}")
            
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
        msg = MIMEMultipart('mixed')
        
        msg['From'] = f"{self.settings.fastmail_from_name} <{self.settings.fastmail_from_email}>"
        msg['To'] = ", ".join([recipient.email for recipient in email_message.recipients])
        msg['Subject'] = email_message.content.subject
        
        if email_message.cc:
            msg['Cc'] = ", ".join([recipient.email for recipient in email_message.cc])

        alternative = MIMEMultipart('alternative')
        text_content, html_content = self._prepare_content(email_message)

        if text_content:
            text_part = MIMEText(text_content, 'plain', 'utf-8')
            alternative.attach(text_part)

        if html_content:
            html_part = MIMEText(html_content, 'html', 'utf-8')
            alternative.attach(html_part)

        msg.attach(alternative)

        return msg
    
    def _prepare_content(self, email_message: EmailMessage) -> tuple[Optional[str], Optional[str]]:
        content = email_message.content

        if content.template_name and content.template_data:
            templates = self.templates.get_template_by_type(content.template_name)

            template_data = {
                **content.template_data,
                'app_name': self.settings.app_name,
                'app_url': self.settings.app_url,
                'update_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

            text_content = self.templates.render_template(templates.get('text', ''), template_data)
            html_content = self.templates.render_template(templates.get('html', ''), template_data)

            return text_content, html_content

        return content.text_body, content.html_body
    
    def _send_smtp_message(self, msg: MIMEMultipart, recipients: List[EmailRecipient], cc: Optional[List[EmailRecipient]] = None) -> str:
        recipient_emails = [recipient.email for recipient in recipients]
        if cc:
            recipient_emails += [r.email for r in cc]

        if self.settings.use_ssl:
            smtp = smtplib.SMTP_SSL(
                host=self.settings.fastmail_smtp_host,
                port=self.settings.fastmail_smtp_port,
                timeout=self.settings.timeout
            )
        else:
            smtp = smtplib.SMTP(
                host=self.settings.fastmail_smtp_host,
                port=self.settings.fastmail_smtp_port,
                timeout=self.settings.timeout
            )

            if self.settings.use_tls:
                smtp.starttls()
        
        try:
            smtp.login(self.settings.fastmail_username, self.settings.fastmail_password)

            smtp.send_message(
                msg,
                from_addr=self.settings.fastmail_from_email,
                to_addrs=recipient_emails,
            )
            message_id = msg.get('Message-ID') or f"kira-{uuid.uuid4()}@{self.settings.fastmail_from_email.split('@')[-1]}"
            if 'Message-ID' not in msg:
                msg.add_header('Message-ID', message_id)
            return message_id
            
        finally:
            smtp.quit()
    
    def _validate_settings(self) -> bool:
        required_settings = [
            self.settings.fastmail_smtp_host,
            self.settings.fastmail_username,
            self.settings.fastmail_password,
            self.settings.fastmail_from_email,
        ]
        
        return all(setting for setting in required_settings)
    
    def _get_task_notification_recipients(self, task_id: int) -> List[EmailRecipient]:
        recipients: List[EmailRecipient] = []
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
    ) -> EmailResponse:
        recipients = self._get_task_notification_recipients(task_id)
        
        if not recipients:
            logger.info(f"No recipients found for task {task_id} notification")
            return EmailResponse(
                success=True,
                message="No recipients configured for notifications",
                recipients_count=0
            )

        template_data = {
            'task_id': task_id,
            'task_title': task_title,
            'updated_by': 'System',
            'updated_fields': updated_fields,
            'previous_values': previous_values or {},
            'new_values': new_values or {},
            'task_url': f"{self.settings.app_url}/tasks/{task_id}"
        }

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

email_service = EmailService()


def get_email_service() -> EmailService:
    return email_service