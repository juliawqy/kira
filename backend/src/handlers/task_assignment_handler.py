from __future__ import annotations

import logging
from typing import Iterable, List, Optional, Set

from backend.src.services import task_assignment as assignment_service
from backend.src.services import task as task_service
from backend.src.services import user as user_service
from backend.src.services.notification import get_notification_service
from backend.src.enums.notification import NotificationType


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def assign_users(
    task_id: int,
    user_ids: Iterable[int],
    **kwargs,
) -> int:
    ids: List[int] = sorted({int(uid) for uid in (user_ids or [])})
    if not ids:
        return 0

    try:
        before_assignees = assignment_service.list_assignees(task_id)
        before_ids: Set[int] = {u.user_id for u in before_assignees}
    except Exception:
        before_ids = set()

    created = assignment_service.assign_users(task_id, ids)

    if created <= 0:
        return 0

    after_assignees = assignment_service.list_assignees(task_id)
    after_ids: Set[int] = {u.user_id for u in after_assignees}
    newly_assigned_ids = sorted(after_ids - before_ids)

    recipient_emails: List[str] = []
    for uid in newly_assigned_ids:
        u = user_service.get_user(uid)
        if u and getattr(u, "email", None):
            recipient_emails.append(u.email)

    task_obj = task_service.get_task_with_subtasks(task_id)
    task_title = getattr(task_obj, "title", "") if task_obj else ""

    if recipient_emails:
        svc = get_notification_service()
        resp = svc.notify_activity(
            user_email=kwargs.get("user_email"),
            task_id=task_id,
            task_title=task_title,
            type_of_alert=NotificationType.TASK_ASSIGN.value,
            to_recipients=recipient_emails,
        )
        logger.info(
            "Notification response",
            extra={
                "task_id": task_id,
                "type": NotificationType.TASK_ASSIGN.value,
                "success": getattr(resp, "success", None),
                "resp_message": getattr(resp, "message", None),
                "recipients_count": getattr(resp, "recipients_count", None),
            },
        )

    return created


def unassign_users(
    task_id: int,
    user_ids: Iterable[int],
    **kwargs,
) -> int:
    ids: List[int] = sorted({int(uid) for uid in (user_ids or [])})
    if not ids:
        return 0

    try:
        before_assignees = assignment_service.list_assignees(task_id)
        before_ids: Set[int] = {u.user_id for u in before_assignees}
    except Exception:
        before_ids = set(ids)  

    deleted = assignment_service.unassign_users(task_id, ids)
    if deleted <= 0:
        return 0

    after_assignees = assignment_service.list_assignees(task_id)
    after_ids: Set[int] = {u.user_id for u in after_assignees}
    removed_ids = sorted(before_ids - after_ids)
    if not removed_ids:
        removed_ids = ids

    recipient_emails: List[str] = []
    for uid in removed_ids:
        u = user_service.get_user(uid)
        if u and getattr(u, "email", None):
            recipient_emails.append(u.email)

    task_obj = task_service.get_task_with_subtasks(task_id)
    task_title = getattr(task_obj, "title", "") if task_obj else ""

    if recipient_emails:
        svc = get_notification_service()
        resp = svc.notify_activity(
            user_email=kwargs.get("user_email"),
            task_id=task_id,
            task_title=task_title,
            type_of_alert=NotificationType.TASK_UNASSIGN.value,
            to_recipients=recipient_emails,
        )
        logger.info(
            "Notification response",
            extra={
                "task_id": task_id,
                "type": NotificationType.TASK_UNASSIGN.value,
                "success": getattr(resp, "success", None),
                "resp_message": getattr(resp, "message", None),
                "recipients_count": getattr(resp, "recipients_count", None),
            },
        )

    return deleted
