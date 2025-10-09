from __future__ import annotations
from typing import List

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from backend.src.schemas.task import TaskCreate, TaskUpdate, TaskRead, TaskWithSubTasks
import backend.src.services.task as task_service

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
def list_parent_tasks():
    """Return all top-level tasks in as."""
    return task_service.list_parent_tasks()

@router.get("/filter", response_model=List[TaskWithSubTasks], name="list_tasks_filtered_sorted")
def list_tasks_filtered_sorted(
    # checking for "?sort_by=...&filters=..." in the URL
    sort_by: str = Query("priority_desc", description="Sort criteria"),
    filters: str = Query(None, description="JSON string with filter criteria. Date ranges (due_date_range, start_date_range) can be combined. Other filters (priority_range, status) must be used separately.")
):
    """Return all top-level tasks with optional filtering and sorting. Date ranges can be combined; other filters are mutually exclusive."""
    try:
        filter_by = None
        if filters:
            import json
            from datetime import datetime
            
            filter_data = json.loads(filters)
            filter_by = {}
            
            # Validate filter combinations
            valid_filters = ["priority_range", "status", "due_date_range", "start_date_range"]
            active_filters = [f for f in valid_filters if f in filter_data]
            
            if len(active_filters) == 0 and filter_data:
                invalid_filters = [f for f in filter_data.keys() if f not in valid_filters]
                raise ValueError(f"Invalid filter types: {invalid_filters}")
            
            # Check for invalid combinations
            date_filters = set(filter_data.keys()) & {"due_date_range", "start_date_range"}
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
            
            if "due_date_range" in filter_data:
                date_range = filter_data["due_date_range"]
                start_date = datetime.strptime(date_range[0], "%Y-%m-%d").date()
                end_date = datetime.strptime(date_range[1], "%Y-%m-%d").date()
                filter_by["due_date_range"] = [start_date, end_date]
            
            if "start_date_range" in filter_data:
                date_range = filter_data["start_date_range"]
                start_date = datetime.strptime(date_range[0], "%Y-%m-%d").date()
                end_date = datetime.strptime(date_range[1], "%Y-%m-%d").date()
                filter_by["start_date_range"] = [start_date, end_date]
        
        return task_service.list_parent_tasks(sort_by=sort_by, filter_by=filter_by)
    
    except (ValueError, json.JSONDecodeError) as e:
        raise HTTPException(status_code=400, detail=f"Invalid filter parameters: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/project/{project_id}", response_model=List[TaskWithSubTasks], name="list_tasks_by_project")
def list_tasks_by_project(project_id: int):
    """Get all parent-level tasks for a specific project."""
    tasks = task_service.list_tasks_by_project(project_id)
    return tasks

@router.get("/{task_id}", response_model=TaskWithSubTasks, name="get_task")
def get_task(task_id: int):
    """Get a task by id; return it with its subtasks."""
    task = task_service.get_task_with_subtasks(task_id)
    if not task:
        raise HTTPException(404, "Task not found")
    return task

@router.patch("/{task_id}", response_model=TaskRead, name="update_task")
def update_task(task_id: int, payload: TaskUpdate):
    """
    Update details of a task.

    Return the updated task.

    Use start_task/complete_task/block_task for status transitions.
    """
    updated = task_service.update_task(task_id, **payload.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(404, "Task not found")
    return updated

@router.post("/{task_id}/status/{new_status}", response_model=TaskRead, name="set_task_status")
def set_task_status(task_id: int, new_status: str):
    """Set a task's status."""
    try:
        return task_service._set_status(task_id, new_status)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
@router.post(
    "/{task_id}/delete",
    response_model=TaskRead,
    name="delete_task",
)
def delete_task(task_id: int, detach_links: bool = Query(True, description="Detach parent/subtask links while deleting")):
    """Soft-delete a task (active=False). Optionally detach all links; return updated task."""
    try:
        return task_service.delete_task(task_id, detach_links=detach_links)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ---------- Subtask Handlers ----------
@router.get("/{task_id}/subtasks", response_model=List[TaskRead], name="list_subtasks")
def list_subtasks(task_id: int):
    """Return direct subtasks of the given task."""
    t = task_service.get_task_with_subtasks(task_id)
    if not t:
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
        msg = str(e).lower()
        if "not found" in msg:
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))



