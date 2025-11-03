from __future__ import annotations

import logging
from typing import Iterable, List, Optional, Set

from backend.src.services import task_assignment as assignment_service
from backend.src.services import task as task_service
from backend.src.services import user as user_service
from backend.src.services import team as team_service
from backend.src.services import department as department_service
from backend.src.services.notification import get_notification_service
from backend.src.schemas.user import UserRead
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

    for id in ids:
        if user_service.get_user(id) is None:
            raise ValueError("User not found")
    
    if task_service.get_task_with_subtasks(task_id) is None:
        raise ValueError("Task not found")

    try:
        before_assignees = assignment_service.list_assignees(task_id)
        before_ids: Set[int] = {u.user_id for u in before_assignees}
    except Exception:
        before_ids = set()
    
    ids = [uid for uid in ids if uid not in before_ids]

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
    
    for id in ids:
        if user_service.get_user(id) is None:
            raise ValueError("User not found")
    
    if task_service.get_task_with_subtasks(task_id) is None:
        raise ValueError("Task not found")

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


def list_assignees(task_id: int) -> list[UserRead]:
    if task_service.get_task_with_subtasks(task_id) is None:
        raise ValueError("Task not found")

    return assignment_service.list_assignees(task_id)


def clear_task_assignees(task_id: int) -> int:
    if task_service.get_task_with_subtasks(task_id) is None:
        raise ValueError("Task not found")

    return assignment_service.clear_task_assignees(task_id)


def list_user_tasks(user_id: int) -> list[int]:
    if user_service.get_user(user_id) is None:
        raise ValueError("User not found")

    return assignment_service.list_tasks_for_user(user_id)


def list_tasks_by_manager(manager_id: int) -> dict:
    """Get all tasks assigned to users managed by a specific manager."""
    manager = user_service.get_user(manager_id)
    if not manager:
        raise ValueError("Manager not found.")

    if not manager.role == 'manager':
        raise ValueError("User is not a manager.")
    
    teams = team_service.get_team_by_manager(manager_id)
    if not teams:
        return {}
    
    all_tasks = {}

    for team in teams:
        all_tasks[team.team_number] = []
        team_members = team_service.get_users_in_team(team.team_id)
        for member in team_members:
            user_tasks = assignment_service.list_tasks_for_user(member["user_id"])
            for task in user_tasks:
                if task not in all_tasks[team.team_number]:
                    all_tasks[team.team_number].append(task)
        subteams = team_service.get_subteam_by_team_number(team.team_number)
        for subteam in subteams:
            subteam_members = team_service.get_users_in_team(subteam.team_id)
            all_tasks[subteam.team_number] = []
            for member in subteam_members:
                user_tasks = assignment_service.list_tasks_for_user(member["user_id"])
                for task in user_tasks:
                    if task not in all_tasks[subteam.team_number]:
                        all_tasks[subteam.team_number].append(task)

    return all_tasks


def list_tasks_by_director(director_id: int) -> dict:
    """Get all tasks assigned to users managed by teams under a specific director."""
    director = user_service.get_user(director_id)
    if not director:
        raise ValueError("Director not found.")

    if not director.role == 'director':
        raise ValueError("User is not a director.")
    
    department = department_service.get_department_by_director(director_id)
    if not department:
        return {}

    teams = team_service.get_teams_by_department(department["department_id"])
    if not teams:
        return {}

    all_tasks = {}
    for team in teams:
        all_tasks[team.team_number] = []
        team_members = team_service.get_users_in_team(team.team_id)
        for member in team_members:
            user_tasks = assignment_service.list_tasks_for_user(member["user_id"])
            for task in user_tasks:
                if task not in all_tasks[team.team_number]:
                    all_tasks[team.team_number].append(task)
        subteams = team_service.get_subteam_by_team_number(team.team_number)
        for subteam in subteams:
            all_tasks[subteam.team_number] = []
            subteam_members = team_service.get_users_in_team(subteam.team_id)
            for member in subteam_members:
                user_tasks = assignment_service.list_tasks_for_user(member["user_id"])
                for task in user_tasks:
                    if task not in all_tasks[subteam.team_number]:
                        all_tasks[subteam.team_number].append(task)

    return all_tasks