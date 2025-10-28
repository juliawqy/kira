from __future__ import annotations
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
import json

from backend.src.schemas.task import TaskCreate, TaskUpdate, TaskRead, TaskWithSubTasks, SubtaskIds
from backend.src.schemas.task_assignment import UnassignUsersPayload, AssignUsersPayload
from backend.src.schemas.user import UserRead
from backend.src.schemas.comment import CommentCreate, CommentRead, CommentUpdate, CommentDelete
import backend.src.handlers.task_assignment_handler as assignment_handler
import backend.src.handlers.task_handler as task_handler
import backend.src.handlers.comment_handler as comment_handler

router = APIRouter(prefix="/task", tags=["task"])


# ---------- Task CRUD Handlers ----------


@router.post("/", response_model=TaskRead, status_code=201, name="create_task")
def create_task(payload: TaskCreate):
    """Create a task; return the task created."""
    try:
        return task_handler.create_task(**payload.model_dump())
    except ValueError as e:
        msg = str(e).lower()
        # Treat "not found" as 404; everything else remains 400
        if "not found" in msg:
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[TaskWithSubTasks], name="list_tasks")
def list_tasks(
    sort_by: str = Query("priority_desc"),
    filters: Optional[str] = Query(None, description="JSON string with filter criteria")
):
    """Return all top-level tasks with optional filtering and sorting."""
    try:
        filter_dict = json.loads(filters) if filters else None
        return task_handler.list_tasks(sort_by=sort_by, filter_by=filter_dict)
    except (ValueError, json.JSONDecodeError) as e:
        raise HTTPException(status_code=400, detail=f"Invalid filter parameters: {str(e)}")


@router.get("/project/{project_id}", response_model=List[TaskWithSubTasks], name="list_tasks_by_project")
def list_tasks_by_project(project_id: int):
    """Get all parent-level tasks for a specific project with their subtasks."""
    try: 
        parent_tasks = task_handler.list_tasks_by_project(project_id)
        return parent_tasks
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/user/{user_id}", response_model=List[TaskWithSubTasks], name="list_tasks_by_user")
def list_tasks_by_user(user_id: int):
    """Get all tasks assigned to a specific user."""
    try:
        return assignment_handler.list_user_tasks(user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/project-user/{project_id}/{user_id}", response_model=List[TaskWithSubTasks], name="list_project_tasks_by_user")
def list_project_tasks_by_user(project_id: int, user_id: int):

    try:
        tasks = task_handler.list_project_tasks_by_user(project_id, user_id)
        return tasks
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/parents", response_model=List[TaskRead], name="list_parent_tasks")
def list_parent_tasks(
    # checking for "?sort_by=...&filters=..." in the URL
    sort_by: str = Query("priority_desc", description="Sort criteria"),
    filters: str = Query(None, description="JSON string with filter criteria. Date ranges (deadline_range, start_date_range) can be combined. Other filters (priority_range, status) must be used separately.")
):
    """Return all parent-level tasks without their subtasks."""
    """Return all top-level tasks with optional filtering and sorting. Date ranges can be combined; other filters are mutually exclusive."""
    
    try:
        filter_dict = json.loads(filters) if filters else None
        return task_handler.list_parent_tasks(sort_by=sort_by, filter_by=filter_dict)
    except (ValueError, json.JSONDecodeError) as e:
        raise HTTPException(status_code=400, detail=f"Invalid filter parameters: {str(e)}")


@router.get("/{task_id}", response_model=TaskWithSubTasks, name="get_task")
def get_task(task_id: int):
    """Get a task by id; return it with its subtasks."""
    try:
        task = task_handler.get_task(task_id)
    except ValueError:
        raise HTTPException(404, "Task not found")
    return task


@router.patch("/{task_id}", response_model=TaskRead, name="update_task")
def update_task(task_id: int, payload: TaskUpdate):

    try:
        updated = task_handler.update_task(task_id, **payload.model_dump(exclude_unset=True))
        return updated
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{task_id}/status/{new_status}", response_model=TaskRead, name="set_task_status")
def set_task_status(task_id: int, new_status: str):
    """Set a task's status."""
    try:
        return task_handler.set_task_status(task_id, new_status)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post(
    "/{task_id}/delete",
    response_model=TaskRead,
    name="delete_task",
)
def delete_task(task_id: int):
    """Soft-delete a task (active=False). Optionally detach all links; return updated task."""
    try:
        return task_handler.delete_task(task_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ---------- Subtask Handlers ----------


@router.get("/{task_id}/subtasks", response_model=List[TaskRead], name="list_subtasks")
def list_subtasks(task_id: int):
    """Return direct subtasks of the given task."""
    try:
        t = task_handler.get_task(task_id)
        return t.subtasks
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{parent_id}/subtasks", response_model=TaskWithSubTasks, name="attach_subtasks")
def attach_subtasks(parent_id: int, payload: SubtaskIds):
    """
    Attach one or more subtasks to a parent (atomic).
    Returns the parent with its subtasks.
    """
    try:
        return task_handler.attach_subtasks(parent_id, payload.subtask_ids)
    except ValueError as e:
        msg = str(e).lower()
        if "not found" in msg:
            raise HTTPException(status_code=404, detail=str(e))
        if "already have a parent" in msg or "cycle" in msg:
            raise HTTPException(status_code=409, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{parent_id}/subtasks/{subtask_id}", status_code=204, name="detach_subtask")
def detach_subtasks(parent_id: int, subtask_id: int):
    """Detach a single subtask from the parent."""
    try:
        task_handler.detach_subtask(parent_id, subtask_id)
        return
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{task_id}/assignees", response_model=List[UserRead], name="list_assignees")
def list_assignees(task_id: int):
    """Return all users assigned to a given task."""
    try:
        return assignment_handler.list_assignees(task_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{task_id}/assignees", name="assign_users")
def assign_users(task_id: int, payload: AssignUsersPayload):
    """Assign one or more users to a task (idempotent)."""
    try:
        created = assignment_handler.assign_users(task_id, payload.user_ids)
        return {"created": created}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{task_id}/assignees", name="unassign_users")
def unassign_users(task_id: int, payload: UnassignUsersPayload):
    """Unassign users from a task."""
    try:
        deleted = assignment_handler.unassign_users(task_id, payload.user_ids)
        return {"Removed": deleted}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{task_id}/assignees/all", name="clear_task_assignees")
def clear_task_assignees(task_id: int):
    """Remove all users assigned to a task."""
    try:
        deleted = assignment_handler.clear_task_assignees(task_id)
        return {"Removed": deleted}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))



@router.post("/{task_id}/notify-assignees", name="notify_task_assignees")
def notify_task_assignees(
    task_id: int, 
    message: str = "Task update notification",
    type_of_alert: str = "task_update"
):
    """
    Send email notification to all assigned users of a task.
    
    Args:
        task_id: ID of the task
        message: Optional custom message for the notification
        type_of_alert: Type of alert (task_update, comment_create, task_assgn, etc.)
        
    Returns:
        Email response with success status and recipient count
    """
    try:
        # Get the task to verify it exists
        task = task_service.get_task_with_subtasks(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Get assigned users
        assignees = assignment_service.list_assignees(task_id)
        recipients = [u.email for u in assignees if getattr(u, 'email', None)]
        
        if not recipients:
            return {
                "success": True,
                "message": "No assigned users with email addresses found",
                "recipients_count": 0
            }
        
        # Import notification service
        from backend.src.services.notification import get_notification_service
        from backend.src.enums.notification import NotificationType
        
        # Validate alert type
        valid_alerts = [alert.value for alert in NotificationType]
        if type_of_alert not in valid_alerts:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid type_of_alert. Must be one of: {valid_alerts}"
            )
        
        # Send notification to all assigned users
        notification_service = get_notification_service()
        response = notification_service.notify_activity(
            user_email="system@kira.local",
            task_id=task_id,
            task_title=task.title or "Untitled Task",
            type_of_alert=type_of_alert,
            updated_fields=["Custom Message"],
            old_values={"Custom Message": "Manual notification sent"},
            new_values={"Custom Message": message},
            to_recipients=recipients,
        )
        
        return {
            "success": response.success,
            "message": response.message,
            "recipients_count": response.recipients_count,
            "email_id": getattr(response, 'email_id', None)
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending notification: {str(e)}")

# ------------------ Comments ------------------

@router.post("/{task_id}/comment", response_model=CommentRead, name="add_comment")
def add_comment(task_id: int, payload: CommentCreate):
    try:
        return comment_handler.add_comment(task_id, payload.user_id, payload.comment, payload.recipient_emails)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{task_id}/comment", response_model=List[CommentRead], name="list_comments")
def list_comments(task_id: int):
    try:
        return comment_handler.list_comments(task_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/comment/{comment_id}", response_model=CommentRead, name="get_comment")
def get_comment(comment_id: int):
    try:
        return comment_handler.get_comment(comment_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/comment/{comment_id}", response_model=CommentRead, name="update_comment")
def update_comment(comment_id: int, payload: CommentUpdate):
    try:
        return comment_handler.update_comment(comment_id, payload.comment, payload.requesting_user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.delete("/comment/{comment_id}", response_model=bool, name="delete_comment")
def delete_comment(comment_id: int, payload: CommentDelete):
    try:
        return comment_handler.delete_comment(comment_id, payload.requesting_user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))