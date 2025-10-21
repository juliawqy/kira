# backend/src/handlers/task_handler.py
from backend.src.services import task as task_service
from backend.src.services import user as user_service
from backend.src.services import project as project_service
from backend.src.services import comment as comment_service


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

def add_comment(task_id: int, user_id: int, comment_text: str):

    task = task_service.get_task_with_subtasks(task_id)
    if not task:
        raise ValueError(f"Task {task_id} not found")

    user = user_service.get_user(user_id)
    if not user:
        raise ValueError(f"User {user_id} not found")

    comment = comment_service.add_comment(task_id, user_id, comment_text)

    # if "@" in comment_text:
    #     mentioned_users = extract_mentions(comment_text)
    #     for u in mentioned_users:
    #         notification_service.notify_user(u, f"You were mentioned in a comment on task {task_id}")

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

def update_comment(comment_id: int, updated_text: str):

    try:
        return comment_service.update_comment(comment_id, updated_text)
    except ValueError as e:
        raise ValueError(str(e))

def delete_comment(comment_id: int):

    try:
        return comment_service.delete_comment(comment_id)
    except ValueError as e:
        raise ValueError(str(e))