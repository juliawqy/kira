import logging
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime

from backend.src.database.db_setup import SessionLocal
from .email import get_email_service
from ..schemas.email import EmailResponse, EmailMessage, EmailRecipient, EmailType
from ..enums.notification import NotificationType


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class NotificationService:
    
    def __init__(self):
        self.email_service = get_email_service()
        self.sender_display_name = "Kira Task Management"

    def notify_activity(
        self,
        *,
        user_email: str,
        task_id: int,
        task_title: str,
        type_of_alert: str,
        comment_user: Optional[str] = None,
        updated_fields: Optional[List[str]] = None,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        to_recipients: Optional[List[str]] = None,
        cc_recipients: Optional[List[str]] = None,
    ) -> EmailResponse:
        
        try:
            logger.info(
                "notify_activity called",
                extra={
                    "user_email": user_email,
                    "task_id": task_id,
                    "task_title": task_title,
                    "type_of_alert": type_of_alert,
                },
            )

            self._validate_activity_inputs(
                type_of_alert=type_of_alert,
                comment_user=comment_user,
                updated_fields=updated_fields,
            )

            recipients, cc = self._resolve_recipients(
                task_id=task_id, to_recipients=to_recipients, cc_recipients=cc_recipients
            )

            if not recipients:
                logger.info(f"No recipients resolved for activity '{type_of_alert}' on task {task_id}")
                return EmailResponse(
                    success=True,
                    message="No recipients configured for notifications",
                    recipients_count=0,
                )

            subject, text_body, html_body = self._build_activity_message(
                type_of_alert=type_of_alert,
                task_id=task_id,
                task_title=task_title,
                user_email=user_email,
                comment_user=comment_user,
                updated_fields=updated_fields or [],
                old_values=old_values or {},
                new_values=new_values or {},
            )

            email_message = EmailMessage(
                recipients=[EmailRecipient(email=e) for e in recipients],
                cc=[EmailRecipient(email=e) for e in cc] if cc else None,
                content={
                    "subject": subject,
                    "text_body": text_body,
                    "html_body": html_body,
                },
                email_type=EmailType.GENERAL_NOTIFICATION,
            )

            logger.info(
                "Dispatching activity notification",
                extra={
                    "type": type_of_alert,
                    "task_id": task_id,
                    "recipients_count": len(recipients),
                    "initiated_by": user_email,
                },
            )

            resp = self.email_service.send_email(email_message)

            if resp.success:
                logger.info(
                    f"Activity notification sent for task {task_id}, type={type_of_alert}, msgid={getattr(resp, 'email_id', None)}, recipients={resp.recipients_count}"
                )
                logger.info(f"Activity notification '{type_of_alert}' sent for task {task_id}")
            else:
                logger.error(
                    f"Activity notification FAILED for task {task_id}, type={type_of_alert}, error={resp.message}"
                )
                logger.error(f"Failed to send activity notification '{type_of_alert}': {resp.message}")

            return resp

        except Exception as e:
            msg = str(e)
            if isinstance(e, ValueError) and "Invalid type_of_alert" not in msg and "valid NotificationType" in msg:
                msg = f"Invalid type_of_alert: {type_of_alert}"
            logger.error(f"Error in notify_activity: {msg}")
            return EmailResponse(
                success=False,
                message=f"Notification service error: {msg}",
                recipients_count=0,
            )

    def _validate_activity_inputs(
        self,
        *,
        type_of_alert: str,
        comment_user: Optional[str],
        updated_fields: Optional[List[str]],
    ) -> None:
        alert = NotificationType(type_of_alert)
        

        if alert in {
            NotificationType.COMMENT_CREATE,
            NotificationType.COMMENT_MENTION,
            NotificationType.COMMENT_UPDATE,
        }:
            if not comment_user:
                raise ValueError("comment_user is required for comment-related alerts")

        if alert == NotificationType.TASK_UPDATE:
            if not updated_fields or len(updated_fields) == 0:
                logger.warning("task_update without updated_fields; proceeding anyway")

    def _resolve_recipients(
        self, *, task_id: int, to_recipients: Optional[List[str]], cc_recipients: Optional[List[str]]
    ) -> Tuple[List[str], List[str]]:
        if to_recipients:
            to_list = to_recipients
        else:
            default_recipients = self.email_service._get_task_notification_recipients(task_id)
            to_list = [r.email for r in default_recipients]

        cc_list = cc_recipients or []
        return to_list, cc_list

    def _build_activity_message(
        self,
        *,
        type_of_alert: str,
        task_id: int,
        task_title: str,
        user_email: str,
        comment_user: Optional[str],
        updated_fields: List[str],
        old_values: Dict[str, Any],
        new_values: Dict[str, Any],
    ) -> Tuple[str, str, str]:
        try:
            alert = NotificationType(type_of_alert)
        except ValueError:
            alert = None

        if alert:
            verb = alert.verb()
        else:
            verb = type_of_alert
        subject = f"[{self.sender_display_name}] {verb.title()} — {task_title} (#{task_id})"

        def fmt_val(v: Any) -> str:
            return "Yes" if isinstance(v, bool) and v else ("No" if isinstance(v, bool) else str(v))

        change_lines: List[str] = []
        for f in (updated_fields or []):
            before = old_values.get(f, "—")
            after = new_values.get(f, "—")
            change_lines.append(f"<li><strong>{f}</strong>: {fmt_val(before)} → {fmt_val(after)}</li>")

        change_text_lines: List[str] = []
        for f in (updated_fields or []):
            before = old_values.get(f, "—")
            after = new_values.get(f, "—")
            change_text_lines.append(f"- {f}: {fmt_val(before)} -> {fmt_val(after)}")

        actor_html = f"<p><em>Triggered by:</em> {comment_user or user_email}</p>"
        actor_text = f"Triggered by: {comment_user or user_email}\n"

        html_sections = [
            f"<p><strong>{verb.title()}</strong> — <em>{task_title}</em> (#{task_id})</p>",
            actor_html,
        ]
        if (alert == NotificationType.TASK_UPDATE) and change_lines:
            html_sections.append("<ul>" + "".join(change_lines) + "</ul>")
        html_body = "\n".join([s for s in html_sections if s])

        text_sections = [
            f"{verb.title()} — {task_title} (#{task_id})",
            actor_text,
        ]
        if (alert == NotificationType.TASK_UPDATE) and change_text_lines:
            text_sections.extend(change_text_lines)
        text_body = "\n".join([t for t in text_sections if t])

        return subject, text_body, html_body
    
    def notify_task_updated(
        self,
        task_id: int,
        task_title: str,
        updated_fields: List[str],
        previous_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
    ) -> EmailResponse:
        try:
            logger.info(f"Processing task update notification for task {task_id}")

            return self.notify_activity(
                user_email="system@kira.local",
                task_id=task_id,
                task_title=task_title,
                type_of_alert=NotificationType.TASK_UPDATE.value,
                updated_fields=updated_fields,
                old_values=previous_values,
                new_values=new_values,
            )

        except Exception as e:
            logger.error(f"Error in notify_task_updated: {str(e)}")
            return EmailResponse(
                success=False,
                message=f"Notification service error: {str(e)}",
                recipients_count=0,
            )
    
notification_service = NotificationService()

def get_notification_service() -> NotificationService:
    return notification_service