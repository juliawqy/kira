# backend/src/handlers/comment_handler.py
import logging
from backend.src.services import task as task_service
from backend.src.services import user as user_service
from backend.src.services import comment as comment_service

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# -------- Comment Handlers -------------------------------------------------------

def add_comment(task_id: int, user_id: int, comment_text: str):
    """Add a comment to a task with user validation."""
    task = task_service.get_task_with_subtasks(task_id)
    if not task:
        raise ValueError(f"Task {task_id} not found")

    user = user_service.get_user(user_id)
    if not user:
        raise ValueError(f"User {user_id} not found")

    comment = comment_service.add_comment(task_id, user_id, comment_text)
    return comment


def list_comments(task_id: int):
    """List all comments for a task."""
    task = task_service.get_task_with_subtasks(task_id)
    if not task:
        raise ValueError(f"Task {task_id} not found")

    return comment_service.list_comments(task_id)


def get_comment(comment_id: int):
    """Get a specific comment by ID."""
    comment = comment_service.get_comment(comment_id)
    if not comment:
        raise ValueError(f"Comment {comment_id} not found")
    return comment


def update_comment(comment_id: int, updated_text: str):
    """Update a comment's text."""
    try:
        return comment_service.update_comment(comment_id, updated_text)
    except ValueError as e:
        raise ValueError(str(e))


def delete_comment(comment_id: int):
    """Delete a comment."""
    try:
        return comment_service.delete_comment(comment_id)
    except ValueError as e:
        raise ValueError(str(e))


# -------- User-Comment Integration Handlers ----------------------------------------

def list_comments_by_user(user_id: int):
    """Get all comments made by a specific user."""
    user = user_service.get_user(user_id)
    if not user:
        raise ValueError(f"User {user_id} not found")

    return comment_service.list_comments_by_user(user_id)


def get_user_comment_count(user_id: int):
    """Get the total number of comments made by a user."""
    user = user_service.get_user(user_id)
    if not user:
        raise ValueError(f"User {user_id} not found")

    return comment_service.get_user_comment_count(user_id)


def get_user_comments_with_task_info(user_id: int):
    """Get all comments by a user with additional task information."""
    user = user_service.get_user(user_id)
    if not user:
        raise ValueError(f"User {user_id} not found")

    comments = comment_service.list_comments_by_user(user_id)
    
    # Enhance comments with task information
    enhanced_comments = []
    for comment in comments:
        try:
            task = task_service.get_task_with_subtasks(comment['task_id'])
            if task:
                comment['task'] = {
                    'id': task.id,
                    'title': task.title,
                    'description': task.description,
                    'status': task.status,
                    'priority': task.priority,
                    'project_id': task.project_id,
                }
            else:
                comment['task'] = None
        except Exception as e:
            logger.warning(f"Could not load task {comment['task_id']} for comment {comment['comment_id']}: {e}")
            comment['task'] = None
        
        enhanced_comments.append(comment)
    
    return enhanced_comments


def get_recent_user_comments(user_id: int, limit: int = 10):
    """Get recent comments made by a user, limited by count."""
    user = user_service.get_user(user_id)
    if not user:
        raise ValueError(f"User {user_id} not found")

    comments = comment_service.list_comments_by_user(user_id)
    
    # Sort by timestamp descending and limit
    sorted_comments = sorted(comments, key=lambda x: x['timestamp'], reverse=True)
    return sorted_comments[:limit]


def get_user_comments_by_task(user_id: int, task_id: int):
    """Get all comments made by a specific user on a specific task."""
    user = user_service.get_user(user_id)
    if not user:
        raise ValueError(f"User {user_id} not found")

    task = task_service.get_task_with_subtasks(task_id)
    if not task:
        raise ValueError(f"Task {task_id} not found")

    # Get all comments for the task and filter by user
    all_comments = comment_service.list_comments(task_id)
    user_comments = [comment for comment in all_comments if comment['user_id'] == user_id]
    
    return user_comments
