import logging
from backend.src.services import task as task_service
from backend.src.services import user as user_service
from backend.src.services import project as project_service
from backend.src.services import comment as comment_service
from backend.src.services.notification import get_notification_service
from backend.src.services import task_assignment as assignment_service
from backend.src.enums.notification import NotificationType
from fastapi import HTTPException


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# -------- Project Handlers -------------------------------------------------------

def list_tasks_by_project(project_id: int):
    project = project_service.get_project_by_id(project_id)
    if not project:
        raise ValueError(f"Project {project_id} not found")

    return task_service.list_tasks_by_project(project_id, active_only=True)

def list_project_tasks_by_user(project_id: int, user_id: int):
    project = project_service.get_project_by_id(project_id)
    if not project:
        raise ValueError(f"Project {project_id} not found")

    user = user_service.get_user(user_id)
    if not user:
        raise ValueError(f"User {user_id} not found")

    return task_service.list_project_tasks_by_user(project_id, user_id)


# -------- Comment Handlers -------------------------------------------------------


def add_comment(task_id: int, user_id: int, comment_text: str, recipient_emails: list[str] = None):
    """Add a comment to a task with recipient emails from frontend."""
    task = task_service.get_task_with_subtasks(task_id)
    if not task:
        raise ValueError(f"Task {task_id} not found")

    user = user_service.get_user(user_id)
    if not user:
        raise ValueError(f"User {user_id} not found")

    comment = comment_service.add_comment(task_id, user_id, comment_text)

    if recipient_emails:
        for email in recipient_emails:
            recipient_user = user_service.get_user(email)
            if not recipient_user:
                logger.warning(f"Recipient email {email} not found in system")
        # recipient_emails will be handled by notification_service later

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

def update_comment(comment_id: int, updated_text: str, requesting_user_id: int, recipient_emails: list[str] = None):
    """Update a comment - only the author can update their comment."""
    
    existing_comment = comment_service.get_comment(comment_id)
    if not existing_comment:
        raise ValueError(f"Comment {comment_id} not found")

    if existing_comment["user_id"] != requesting_user_id:
        raise PermissionError("Only the comment author can update this comment")
    
    comment = comment_service.update_comment(comment_id, updated_text)

    if recipient_emails:
        for email in recipient_emails:
            recipient_user = user_service.get_user(email)
            if not recipient_user:
                logger.warning(f"Recipient email {email} not found in system")
        # recipient_emails will be handled by notification_service later

    return comment

def delete_comment(comment_id: int, requesting_user_id: int):
    """Delete a comment - only the author can delete their comment."""
    
    existing_comment = comment_service.get_comment(comment_id)
    if not existing_comment:
        raise ValueError(f"Comment {comment_id} not found")
    
    if existing_comment["user_id"] != requesting_user_id:
        raise PermissionError("Only the comment author can delete this comment")
    
    return comment_service.delete_comment(comment_id)


def notify_task_assignees(
    task_id: int,
    message: str = "Task update notification",
    type_of_alert: str = "task_update",
):
    """Send email notification to all assigned users of a task.

    Returns a dict with keys: success, message, recipients_count, email_id (optional).
    """
    # Verify task exists
    task = task_service.get_task_with_subtasks(task_id)
    if not task:
        # Raise 404 directly to match original route behavior
        raise HTTPException(status_code=404, detail="Task not found")

    # Resolve recipients from assignees that have an email
    assignees = assignment_service.list_assignees(task_id)
    recipients = [u.email for u in assignees if getattr(u, 'email', None)]

    if not recipients:
        return {
            "success": True,
            "message": "No assigned users with email addresses found",
            "recipients_count": 0,
        }

    # Validate alert type against enum
    valid_alerts = [alert.value for alert in NotificationType]
    if type_of_alert not in valid_alerts:
        # Keep 400 validation behavior consistent with original route implementation
        raise HTTPException(
            status_code=400,
            detail=f"Invalid type_of_alert. Must be one of: {valid_alerts}",
        )

    # Send notification
    notification_service = get_notification_service()
    response = notification_service.notify_activity(
        user_email="system@kira.local",
        task_id=task_id,
        task_title=getattr(task, 'title', None) or "Untitled Task",
        type_of_alert=type_of_alert,
        updated_fields=["Custom Message"],
        old_values={"Custom Message": "Manual notification sent"},
        new_values={"Custom Message": message},
        to_recipients=recipients,
    )

    return {
        "success": getattr(response, 'success', None),
        "message": getattr(response, 'message', None),
        "recipients_count": getattr(response, 'recipients_count', 0),
        "email_id": getattr(response, 'email_id', None),
    }

def update_task(
    task_id: int,
    *,
    title: str | None = None,
    description: str | None = None,
    start_date=None,
    deadline=None,
    priority: int | None = None,
    recurring: int | None = None,
    tag: str | None = None,
    project_id: int | None = None,
    **kwargs,
):
    

    pre = task_service.get_task_with_subtasks(task_id)
    if not pre:
        raise ValueError(f"Task {task_id} not found")

    prev_values = {
        'title': getattr(pre, 'title', None),
        'description': getattr(pre, 'description', None),
        'start_date': getattr(pre, 'start_date', None),
        'deadline': getattr(pre, 'deadline', None),
        'priority': getattr(pre, 'priority', None),
        'recurring': getattr(pre, 'recurring', None),
        'tag': getattr(pre, 'tag', None),
        'project_id': getattr(pre, 'project_id', None),
    }

    
    updated = task_service.update_task(
        task_id,
        title=title,
        description=description,
        start_date=start_date,
        deadline=deadline,
        priority=priority,
        recurring=recurring,
        tag=tag,
        project_id=project_id,
        **kwargs,
    )

   
    candidate_fields: list[str] = []
    if title is not None:       candidate_fields.append('title')
    if description is not None: candidate_fields.append('description')
    if start_date is not None:  candidate_fields.append('start_date')
    if deadline is not None:    candidate_fields.append('deadline')
    if priority is not None:    candidate_fields.append('priority')
    if recurring is not None:   candidate_fields.append('recurring')
    if tag is not None:         candidate_fields.append('tag')
    if project_id is not None:  candidate_fields.append('project_id')

    
    updated_fields: list[str] = []
    old_values: dict = {}
    new_values: dict = {}
    for f in candidate_fields:
        before = prev_values.get(f)
        after = getattr(updated, f)
        if str(before) != str(after):
            updated_fields.append(f)
            old_values[f] = before
            new_values[f] = after

    if updated_fields:
        try:
            assignees = assignment_service.list_assignees(task_id)
            recipients = [u.email for u in assignees if getattr(u, 'email', None)] or None
        except Exception:
            recipients = None

        resp = get_notification_service().notify_activity(
            user_email=kwargs.get("user_email"),
            task_id=updated.id,
            task_title=updated.title or "",
            type_of_alert=NotificationType.TASK_UPDATE.value,
            updated_fields=updated_fields,
            old_values=old_values,
            new_values=new_values,
            to_recipients=recipients,
        )
        try:
            logger.info(
                "Notification response",
                extra={
                    "task_id": updated.id,
                    "type": NotificationType.TASK_UPDATE.value,
                    "success": getattr(resp, "success", None),
                    "message": getattr(resp, "message", None),
                    "recipients_count": getattr(resp, "recipients_count", None),
                    "email_id": getattr(resp, "email_id", None),
                },
            )
        except Exception:
            pass

    return updated