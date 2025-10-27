from __future__ import annotations
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, validator

from backend.src.schemas.task import TaskCreate, TaskUpdate, TaskRead, TaskWithSubTasks
from backend.src.schemas.user import UserRead
import backend.src.services.task as task_service
from backend.src.schemas.comment import CommentCreate, CommentRead, CommentUpdate, CommentDelete
import backend.src.services.task_assignment as assignment_service
import backend.src.handlers.task_assignment_handler as assignment_handler
import backend.src.handlers.task_handler as task_handler
import backend.src.handlers.comment_handler as comment_handler

router = APIRouter(prefix="/task", tags=["task"])

# ---------- payload model ----------
class SubtaskIds(BaseModel):
    subtask_ids: List[int] = []  # allow empty list -> idempotent no-op

# ---------- Task CRUD Handlers ----------
@router.post("/", response_model=TaskRead, status_code=201, name="create_task")
def create_task(payload: TaskCreate):
    """Create a task; return the task created."""
    try:
        return task_service.add_task(**payload.model_dump())
    except ValueError as e:
        msg = str(e).lower()
        # Treat "not found" as 404; everything else remains 400
        if "not found" in msg:
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[TaskWithSubTasks], name="list_tasks")
def list_tasks(sort_by="priority_desc"):
    """Return all top-level tasks with their subtasks."""
    tasks = task_service.list_tasks(sort_by=sort_by)
    return tasks

@router.get("/filter", response_model=List[TaskWithSubTasks], name="list_tasks_filtered_sorted")
def list_tasks_filtered_sorted(
    # checking for "?sort_by=...&filters=..." in the URL
    sort_by: str = Query("priority_desc", description="Sort criteria"),
    filters: str = Query(None, description="JSON string with filter criteria. Date ranges (deadline_range, start_date_range) can be combined. Other filters (priority_range, status) must be used separately.")
):
    """Return all top-level tasks with optional filtering and sorting. Date ranges can be combined; other filters are mutually exclusive."""
    import json
    from datetime import datetime
    
    try:
        filter_by = None
        if filters:
            
            filter_data = json.loads(filters)
            filter_by = {}
            
            # Validate filter combinations
            valid_filters = ["priority_range", "status", "deadline_range", "start_date_range"]
            active_filters = [f for f in valid_filters if f in filter_data]
            
            if len(active_filters) == 0 and filter_data:
                invalid_filters = [f for f in filter_data.keys() if f not in valid_filters]
                raise ValueError(f"Invalid filter types: {invalid_filters}")
            
            # Check for invalid combinations
            date_filters = set(filter_data.keys()) & {"deadline_range", "start_date_range"}
            non_date_filters = set(filter_data.keys()) & {"priority_range", "status"}
            
            # Date filters can be combined with each other, but not with non-date filters
            if len(non_date_filters) > 1:
                raise ValueError(f"Only one non-date filter allowed. Found: {list(non_date_filters)}")
            if len(non_date_filters) >= 1 and len(date_filters) >= 1:
                raise ValueError(f"Date filters cannot be combined with other filter types. Found date filters: {list(date_filters)}, other filters: {list(non_date_filters)}")
            
            # Process filters
            if "priority_range" in filter_data:
                filter_by["priority_range"] = filter_data["priority_range"]
            
            if "status" in filter_data:
                filter_by["status"] = filter_data["status"]
            
            if "deadline_range" in filter_data:
                date_range = filter_data["deadline_range"]
                start_date = datetime.strptime(date_range[0], "%Y-%m-%d").date()
                end_date = datetime.strptime(date_range[1], "%Y-%m-%d").date()
                filter_by["deadline_range"] = [start_date, end_date]
            
            if "start_date_range" in filter_data:
                date_range = filter_data["start_date_range"]
                start_date = datetime.strptime(date_range[0], "%Y-%m-%d").date()
                end_date = datetime.strptime(date_range[1], "%Y-%m-%d").date()
                filter_by["start_date_range"] = [start_date, end_date]

        parent_tasks = task_service.list_tasks(sort_by=sort_by, filter_by=filter_by)

        return parent_tasks
    
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
    import json
    from datetime import datetime
    
    try:
        filter_by = None
        if filters:
            
            filter_data = json.loads(filters)
            filter_by = {}
            
            # Validate filter combinations
            valid_filters = ["priority_range", "status", "deadline_range", "start_date_range"]
            active_filters = [f for f in valid_filters if f in filter_data]
            
            if len(active_filters) == 0 and filter_data:
                invalid_filters = [f for f in filter_data.keys() if f not in valid_filters]
                raise ValueError(f"Invalid filter types: {invalid_filters}")
            
            # Check for invalid combinations
            date_filters = set(filter_data.keys()) & {"deadline_range", "start_date_range"}
            non_date_filters = set(filter_data.keys()) & {"priority_range", "status"}
            
            # Date filters can be combined with each other, but not with non-date filters
            if len(non_date_filters) > 1:
                raise ValueError(f"Only one non-date filter allowed. Found: {list(non_date_filters)}")
            if len(non_date_filters) >= 1 and len(date_filters) >= 1:
                raise ValueError(f"Date filters cannot be combined with other filter types. Found date filters: {list(date_filters)}, other filters: {list(non_date_filters)}")
            
            # Process filters
            if "priority_range" in filter_data:
                filter_by["priority_range"] = filter_data["priority_range"]
            
            if "status" in filter_data:
                filter_by["status"] = filter_data["status"]
            
            if "deadline_range" in filter_data:
                date_range = filter_data["deadline_range"]
                start_date = datetime.strptime(date_range[0], "%Y-%m-%d").date()
                end_date = datetime.strptime(date_range[1], "%Y-%m-%d").date()
                filter_by["deadline_range"] = [start_date, end_date]
            
            if "start_date_range" in filter_data:
                date_range = filter_data["start_date_range"]
                start_date = datetime.strptime(date_range[0], "%Y-%m-%d").date()
                end_date = datetime.strptime(date_range[1], "%Y-%m-%d").date()
                filter_by["start_date_range"] = [start_date, end_date]

        parent_tasks = task_service.list_parent_tasks(sort_by=sort_by, filter_by=filter_by)
        return parent_tasks

    except (ValueError, json.JSONDecodeError) as e:
        raise HTTPException(status_code=400, detail=f"Invalid filter parameters: {str(e)}")

@router.get("/{task_id}", response_model=TaskWithSubTasks, name="get_task")
def get_task(task_id: int):
    """Get a task by id; return it with its subtasks."""
    task = task_service.get_task_with_subtasks(task_id)
    if not task:
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
        return task_service.set_task_status(task_id, new_status)
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
        return task_service.delete_task(task_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# ---------- Subtask Handlers ----------

@router.get("/{task_id}/subtasks", response_model=List[TaskRead], name="list_subtasks")
def list_subtasks(task_id: int):
    """Return direct subtasks of the given task."""
    t = task_service.get_task_with_subtasks(task_id)
    if not t or (hasattr(t, "active") and not t.active):
        raise HTTPException(404, "Task not found")
    return t.subtasks

@router.post("/{parent_id}/subtasks", response_model=TaskWithSubTasks, name="attach_subtasks")
def attach_subtasks(parent_id: int, payload: SubtaskIds):
    """
    Attach one or more subtasks to a parent (atomic).
    Returns the parent with its subtasks.
    """
    try:
        return task_service.attach_subtasks(parent_id, payload.subtask_ids)
    except ValueError as e:
        msg = str(e).lower()
        if "not found" in msg:
            raise HTTPException(status_code=404, detail=str(e))
        if "already have a parent" in msg or "cycle" in msg:
            raise HTTPException(status_code=409, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{parent_id}/subtasks/{subtask_id}", status_code=204, name="detach_subtask")
def detach_subtask(parent_id: int, subtask_id: int):
    """Detach a single subtask from the parent."""
    try:
        task_service.detach_subtask(parent_id, subtask_id)
        return
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# Task_assigment endpoints
class AssignUsersPayload(BaseModel):
    user_ids: List[int]
    
    @validator('user_ids')
    def validate_user_ids(cls, v):
        if not v or len(v) < 1:
            raise ValueError('user_ids must contain at least one user ID')
        return v

@router.get("/{task_id}/assignees", response_model=List[UserRead], name="list_assignees")
def list_assignees(task_id: int):
    """Return all users assigned to a given task."""
    try:
        return assignment_service.list_assignees(task_id)
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

class UnassignUsersPayload(BaseModel):
    user_ids: List[int]

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
        deleted = assignment_service.clear_task_assignees(task_id)
        return {"Removed": deleted}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

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