# backend/src/handlers/task_handler.py
from backend.src.services import task as task_service
from backend.src.services import user as user_service
from backend.src.services import comment as comment_service
from backend.src.services.notification_service import get_notification_service
import logging

logger = logging.getLogger(__name__)


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
    # Snapshot current values for diffing
    pre = task_service.get_task_with_subtasks(task_id)
    if not pre:
        # Let the service raise a consistent error message
        return task_service.update_task(task_id, **{
            k: v for k, v in {
                'title': title,
                'description': description,
                'start_date': start_date,
                'deadline': deadline,
                'priority': priority,
                'recurring': recurring,
                'tag': tag,
                'project_id': project_id,
                **kwargs,
            }.items() if v is not None
        })

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

    # Perform update via service
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

    # Determine which fields were intended to change
    candidate_fields: list[str] = []
    if title is not None:       candidate_fields.append('title')
    if description is not None: candidate_fields.append('description')
    if start_date is not None:  candidate_fields.append('start_date')
    if deadline is not None:    candidate_fields.append('deadline')
    if priority is not None:    candidate_fields.append('priority')
    if recurring is not None:   candidate_fields.append('recurring')
    if tag is not None:         candidate_fields.append('tag')
    if project_id is not None:  candidate_fields.append('project_id')

    # Build diffs
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

    # Send notification (best-effort)
    try:
        if updated_fields:
            resp = get_notification_service().notify_activity(
                user_email="system@kira.local",
                task_id=updated.id,
                task_title=updated.title or "",
                type_of_alert="task_update",
                updated_fields=updated_fields,
                old_values=old_values,
                new_values=new_values,
            )
    except Exception as _notify_err:
        logger.debug(f"Task update notification skipped due to error: {_notify_err}")

    return updated