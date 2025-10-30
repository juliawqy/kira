from __future__ import annotations

import logging
from typing import Iterable, Optional
from datetime import date
from datetime import datetime


from backend.src.services import task as task_service
from backend.src.services import user as user_service
from backend.src.services import project as project_service
from backend.src.services.notification import get_notification_service
from backend.src.services import task_assignment as assignment_service
from backend.src.enums.notification import NotificationType
from backend.src.enums.task_status import TaskStatus, ALLOWED_STATUSES
from backend.src.enums.task_filter import TaskFilter, ALLOWED_FILTERS
from backend.src.enums.task_sort import TaskSort, ALLOWED_SORTS
from backend.src.database.db_setup import SessionLocal
from backend.src.database.models.task import Task



logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# ---- Helpers ----------------------------------------------------------------


def _normalize_filter_dates(filter_dict: Optional[dict]) -> Optional[dict]:
    """Convert date strings in filters into datetime.date objects."""

    parsed = {}
    for key, value in filter_dict.items():
        if key in {"deadline_range", "start_date_range"}:
            start, end = value
            parsed[key] = [
                datetime.strptime(start, "%Y-%m-%d").date(),
                datetime.strptime(end, "%Y-%m-%d").date(),
            ]
        else:
            parsed[key] = value
    return parsed


# -------- Task Handlers -------------------------------------------------------


def create_task(
    title: str,
    *,
    description: Optional[str] = None,
    start_date: Optional[date] = None,
    deadline: Optional[date] = None,
    priority: int = 5,
    status: str = TaskStatus.TO_DO.value,
    recurring: Optional[int] = 0,
    tag: Optional[str] = None,
    project_id: int,
    active: bool = True,
    parent_id: Optional[int] = None,
):
    if not title or not title.strip():
        raise ValueError("Task title cannot be empty or whitespace.")
    
    if parent_id is not None:
            parent = task_service.get_task_with_subtasks(parent_id)
            if not parent:
                raise ValueError(f"Parent task {parent_id} not found.")
            
            if not parent.active:
                raise ValueError(f"Parent task {parent_id} is inactive and cannot accept subtasks.")

    task = task_service.add_task(
        title=title,
        description=description,
        start_date=start_date,
        deadline=deadline,
        priority=priority,
        status=status,
        recurring=recurring,
        tag=tag,
        project_id=project_id,
        active=active,
        parent_id=parent_id,
    )

    if parent_id is not None:
        task_service.link_subtask(parent_id, task.id)

    return task

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
        # try:
        assignees = assignment_service.list_assignees(task_id)
        recipients = [u.email for u in assignees if getattr(u, 'email', None)] or None

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

def get_task(task_id: int):
    task = task_service.get_task_with_subtasks(task_id)
    if not task:
        raise ValueError("Task not found.")

    if task.active is False:
        raise ValueError("Task not found")
    
    return task

def set_task_status(task_id: int, status: str):
    if status not in ALLOWED_STATUSES:
        raise ValueError(f"Invalid status '{status}'")

    task = task_service.get_task_with_subtasks(task_id)
    if not task:
        raise ValueError("Task not found.")

    updated_task = task_service.set_task_status(task_id, status)
    return updated_task

def list_tasks(*, 
    active_only: bool = True, 
    project_id: Optional[int] = None,
    sort_by: Optional[str] = "priority_desc",
    filter_by: Optional[dict] = None
):
    
    if filter_by: 
        invalid = [f for f in filter_by if f not in ALLOWED_FILTERS]
        if invalid:
            raise ValueError(f"Invalid filter keys: {invalid}")
        
        date_filters = set(filter_by) & {"deadline_range", "start_date_range"}
        non_date_filters = set(filter_by) & {"priority_range", "status"}

        if len(non_date_filters) > 1:
            raise ValueError(f"Only one non-date filter allowed: {list(non_date_filters)}")
        if date_filters and non_date_filters:
            raise ValueError(
                f"Date filters cannot be combined with other filter types. "
                f"Date filters: {list(date_filters)}, other: {list(non_date_filters)}"
            )

    filter_by = _normalize_filter_dates(filter_by) if filter_by else None

    if sort_by not in ALLOWED_SORTS:
        raise ValueError(f"Invalid sort_by value '{sort_by}'")

    tasks = task_service.list_tasks(
        active_only=active_only,
        project_id=project_id,
        sort_by=sort_by,
        filter_by=filter_by
    )
    return tasks

def list_parent_tasks(*, 
    active_only: bool = True, 
    project_id: Optional[int] = None,
    sort_by: Optional[str] = "priority_desc",
    filter_by: Optional[dict] = None
):

    if filter_by: 
        invalid = [f for f in filter_by if f not in ALLOWED_FILTERS]
        if invalid:
            raise ValueError(f"Invalid filter keys: {invalid}")
        
        date_filters = set(filter_by) & {"deadline_range", "start_date_range"}
        non_date_filters = set(filter_by) & {"priority_range", "status"}

        if len(non_date_filters) > 1:
            raise ValueError(f"Only one non-date filter allowed: {list(non_date_filters)}")
        if date_filters and non_date_filters:
            raise ValueError(
                f"Date filters cannot be combined with other filter types. "
                f"Date filters: {list(date_filters)}, other: {list(non_date_filters)}"
            )

    filter_by = _normalize_filter_dates(filter_by) if filter_by else None

    if sort_by not in ALLOWED_SORTS:
        raise ValueError(f"Invalid sort_by value '{sort_by}'")

    tasks = task_service.list_parent_tasks(
        active_only=active_only,
        project_id=project_id,
        sort_by=sort_by,
        filter_by=filter_by
    )
    return tasks

def delete_task(task_id: int):
    task = task_service.get_task_with_subtasks(task_id)
    if not task:
        raise ValueError("Task not found.")

    deleted = task_service.delete_task(task_id)
    return deleted


# -------- Subtask Assignment Handlers -------------------------------------------------------


def attach_subtasks(parent_id: int, subtask_ids: Iterable[int]) -> Task:

    if parent_id in subtask_ids:
        raise ValueError("A task cannot be its own parent")

    parent = task_service.get_task_with_subtasks(parent_id)
    if not parent:
        raise ValueError(f"Parent task {parent_id} not found.")

    if not parent.active:
        raise ValueError(f"Parent task {parent_id} is inactive and cannot accept subtasks.")

    ids = sorted({int(sid) for sid in subtask_ids or []})
    for subtask_id in ids:
        subtask = task_service.get_task_with_subtasks(subtask_id)
        if not subtask:
            raise ValueError(f"Subtask {subtask_id} not found.")
        if not subtask.active:
            raise ValueError(f"Subtask {subtask_id} not found.")
    
    return task_service.attach_subtasks(parent_id, ids)


def detach_subtask(parent_id: int, subtask_id: int) -> Task:

    parent = task_service.get_task_with_subtasks(parent_id)
    if not parent:
        raise ValueError(f"Parent task {parent_id} not found.")

    if subtask_id not in [t.id for t in parent.subtasks]:
        raise ValueError(f"Link not found for parent={parent_id}, subtask={subtask_id}")

    return task_service.detach_subtask(parent_id, subtask_id)


# -------- Task x Project Handlers -------------------------------------------------------


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
