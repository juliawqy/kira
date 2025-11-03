import logging
import threading
from backend.src.services import task as task_service
from backend.src.services import user as user_service
from backend.src.services import comment as comment_service
from backend.src.services import task_assignment as assignment_service
from backend.src.services.notification import get_notification_service
from backend.src.enums.notification import NotificationType

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def add_comment(task_id: int, user_id: int, comment_text: str, recipient_emails: list[str] = None):
    """Add a comment to a task and notify recipients."""

    task = task_service.get_task_with_subtasks(task_id)
    if not task:
        raise ValueError(f"Task {task_id} not found")

    user = user_service.get_user(user_id)
    if not user:
        raise ValueError(f"User {user_id} not found")

    comment = comment_service.add_comment(task_id, user_id, comment_text)

    recipients: set[str] = set()
    if recipient_emails:
        for email in recipient_emails:
            recipient_user = user_service.get_user(email)
            if recipient_user and getattr(recipient_user, "email", None):
                recipients.add(recipient_user.email)

    assignees = assignment_service.list_assignees(task_id)
    for u in assignees or []:
        if getattr(u, "email", None):
            recipients.add(u.email)

    task_title = getattr(task, "title", "") or ""
    commenter_email = getattr(user, "email", None) or "system@kira.local"
    commenter_name = getattr(user, "name", None) or commenter_email

    def _send_notify():
        svc = get_notification_service()
        resp = svc.notify_activity(
            user_email=commenter_email,
            task_id=task_id,
            task_title=task_title,
            type_of_alert=NotificationType.COMMENT_CREATE.value,
            comment_user=commenter_name,
            to_recipients=sorted(recipients) if recipients else None,
        )
        logger.info(
            "Comment notification dispatched",
            extra={
                "task_id": task_id,
                "type": NotificationType.COMMENT_CREATE.value,
                "success": getattr(resp, "success", None),
                "resp_message": getattr(resp, "message", None),
                "recipients_count": getattr(resp, "recipients_count", None),
            },
        )

    threading.Thread(target=_send_notify, daemon=True).start()

    return comment

def list_comments(task_id: int):

    task = task_service.get_task_with_subtasks(task_id)
    if not task:
        raise ValueError(f"Task {task_id} not found")

    return comment_service.list_comments(task_id)

def get_comment(comment_id: int):

    comment = comment_service.get_comment(comment_id)
    if not comment:
        raise ValueError(f"Comment {comment_id} not found")
    return comment

def update_comment(comment_id: int, updated_text: str, requesting_user_id: int):
    """Update a comment - only the author can update their comment."""
    
    existing_comment = comment_service.get_comment(comment_id)
    if not existing_comment:
        raise ValueError(f"Comment {comment_id} not found")

    if existing_comment["user_id"] != requesting_user_id:
        raise PermissionError("Only the comment author can update this comment")
    
    return comment_service.update_comment(comment_id, updated_text)

def delete_comment(comment_id: int, requesting_user_id: int):
    """Delete a comment - only the author can delete their comment."""
    
    existing_comment = comment_service.get_comment(comment_id)
    if not existing_comment:
        raise ValueError(f"Comment {comment_id} not found")
    
    if existing_comment["user_id"] != requesting_user_id:
        raise PermissionError("Only the comment author can delete this comment")
    
    return comment_service.delete_comment(comment_id)


def notify_comment_mentions(task_id: int, user_id: int, recipient_emails: list[str] | None):
    if not recipient_emails:
        return None

    task = task_service.get_task_with_subtasks(task_id)
    if not task:
        raise ValueError(f"Task {task_id} not found")

    user = user_service.get_user(user_id)
    if not user:
        raise ValueError(f"User {user_id} not found")

    valid_recipients: set[str] = {
        u.email
        for u in (user_service.get_user(email) for email in (recipient_emails or []))
        if u and getattr(u, "email", None)
    }

    if not valid_recipients:
        return None

    task_title = getattr(task, "title", "") or ""
    commenter_email = getattr(user, "email", None)
    commenter_name = getattr(user, "name", None) or commenter_email

    svc = get_notification_service()
    resp = svc.notify_activity(
        user_email=commenter_email,
        task_id=task_id,
        task_title=task_title,
        type_of_alert=NotificationType.COMMENT_MENTION.value,
        comment_user=commenter_name,
        to_recipients=sorted(valid_recipients),
    )
    logger.info(
        "Comment mention notification dispatched",
        extra={
            "task_id": task_id,
            "type": NotificationType.COMMENT_MENTION.value,
            "success": getattr(resp, "success", None),
            "resp_message": getattr(resp, "message", None),
            "recipients_count": getattr(resp, "recipients_count", None),
        },
    )

    return resp

