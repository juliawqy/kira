import logging
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime

from .email_service import get_email_service
from ..schemas.email import EmailResponse, EmailMessage, EmailRecipient, EmailType


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class NotificationService:
    """Service for managing notifications across different channels"""
    
    def __init__(self):
        self.email_service = get_email_service()
        self.sender_display_name = "Kira Task Management"

    # ---------------------- New centralized entry point ----------------------
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
        task_url: Optional[str] = None,
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

            # Validate inputs based on alert type
            self._validate_activity_inputs(
                type_of_alert=type_of_alert,
                comment_user=comment_user,
                updated_fields=updated_fields,
            )

            # Determine recipients
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

            # Build subject and message bodies
            subject, text_body, html_body = self._build_activity_message(
                type_of_alert=type_of_alert,
                task_id=task_id,
                task_title=task_title,
                user_email=user_email,
                comment_user=comment_user,
                updated_fields=updated_fields or [],
                old_values=old_values or {},
                new_values=new_values or {},
                task_url=task_url,
            )

            # Construct EmailMessage
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

            # Audit log
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
            else:
                logger.error(
                    f"Activity notification FAILED for task {task_id}, type={type_of_alert}, error={resp.message}"
                )

            return resp

        except Exception as e:
            logger.error(f"Error in notify_activity: {str(e)}")
            return EmailResponse(
                success=False,
                message=f"Notification service error: {str(e)}",
                recipients_count=0,
            )

    # ------------------------------ Helpers ---------------------------------
    def _validate_activity_inputs(
        self,
        *,
        type_of_alert: str,
        comment_user: Optional[str],
        updated_fields: Optional[List[str]],
    ) -> None:
        valid_types = {
            "task_create",
            "task_update",
            "task_assgn",
            "task_unassgn",
            "comment_create",
            "comment_mention",
            "comment_update",
            "delete_task",
            "delete_comment",
        }
        if type_of_alert not in valid_types:
            raise ValueError(f"Invalid type_of_alert: {type_of_alert}")

        # Per-type minimal validations
        if type_of_alert.startswith("comment_"):
            if not comment_user:
                raise ValueError("comment_user is required for comment-related alerts")

        if type_of_alert == "task_update":
            if not updated_fields or len(updated_fields) == 0:
                # Allow empty but warn
                logger.warning("task_update without updated_fields; proceeding anyway")

    def _resolve_recipients(
        self, *, task_id: int, to_recipients: Optional[List[str]], cc_recipients: Optional[List[str]]
    ) -> Tuple[List[str], List[str]]:
        if to_recipients:
            to_list = to_recipients
        else:
            # Fallback to default recipients resolution via EmailService helper
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
        task_url: Optional[str],
    ) -> Tuple[str, str, str]:
        # Subject line
        verb_map = {
            "task_create": "created",
            "task_update": "updated",
            "task_assgn": "assigned",
            "task_unassgn": "unassigned",
            "comment_create": "commented",
            "comment_mention": "mentioned",
            "comment_update": "updated comment",
            "delete_task": "deleted task",
            "delete_comment": "deleted comment",
        }
        verb = verb_map.get(type_of_alert, type_of_alert)
        subject = f"[{self.sender_display_name}] {verb.title()} — {task_title} (#{task_id})"

        # Change lines for updates
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

        # Common fragments
        link_html = f'<p><a href="{task_url}">View Task</a></p>' if task_url else ""
        link_text = f"\nView Task: {task_url}\n" if task_url else "\n"
        actor_html = f"<p><em>Triggered by:</em> {comment_user or user_email}</p>"
        actor_text = f"Triggered by: {comment_user or user_email}\n"

        # Assemble HTML
        html_sections = [
            f"<p><strong>{verb.title()}</strong> — <em>{task_title}</em> (#{task_id})</p>",
            actor_html,
        ]
        if type_of_alert == "task_update" and change_lines:
            html_sections.append("<ul>" + "".join(change_lines) + "</ul>")
        html_sections.append(link_html)
        html_body = "\n".join([s for s in html_sections if s])

        # Assemble Text
        text_sections = [
            f"{verb.title()} — {task_title} (#{task_id})",
            actor_text,
        ]
        if type_of_alert == "task_update" and change_text_lines:
            text_sections.extend(change_text_lines)
        text_sections.append(link_text)
        text_body = "\n".join([t for t in text_sections if t])

        return subject, text_body, html_body
    
    def notify_task_updated(
        self,
        task_id: int,
        task_title: str,
        updated_fields: List[str],
        previous_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        task_url: Optional[str] = None
    ) -> EmailResponse:
        """Backward-compatible wrapper. Prefer notify_activity()."""
        try:
            logger.info(f"Processing task update notification for task {task_id}")

            # Prefer the centralized path to build consistent content
            return self.notify_activity(
                user_email="system@kira.local",
                task_id=task_id,
                task_title=task_title,
                type_of_alert="task_update",
                updated_fields=updated_fields,
                old_values=previous_values,
                new_values=new_values,
                task_url=task_url,
            )

        except Exception as e:
            logger.error(f"Error in notify_task_updated: {str(e)}")
            return EmailResponse(
                success=False,
                message=f"Notification service error: {str(e)}",
                recipients_count=0,
            )
    


# Global notification service instance
notification_service = NotificationService()


def get_notification_service() -> NotificationService:
    """Get notification service instance"""
    return notification_service