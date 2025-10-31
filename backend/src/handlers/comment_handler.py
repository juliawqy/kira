import logging
from backend.src.services import task as task_service
from backend.src.services import user as user_service
from backend.src.services import comment as comment_service

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

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

