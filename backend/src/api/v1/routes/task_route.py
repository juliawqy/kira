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

@router.get("/{task_id}", response_model=TaskWithSubTasks, name="get_task")
def get_task(task_id: int):
    """Get a task by id; return it with its subtasks."""
    task = task_service.get_task_with_subtasks(task_id)
    if not task:
        raise HTTPException(404, "Task not found")
    return task

@router.get("/", response_model=List[TaskWithSubTasks], name="list_tasks")
def list_parent_tasks():
    """Return all top-level tasks in as."""
    return task_service.list_parent_tasks()

@router.get("/filter", response_model=List[TaskWithSubTasks], name="list_tasks_filtered_sorted")
def list_tasks_filtered_sorted(
    # checking for "?sort_by=...&filter_type=...&filter_value=..." in the URL
    sort_by: str = Query("priority_desc", description="Sort criteria"),
    filter_type: str = Query(None, description="Filter type (priority, priority_range, status, etc.)"),
    filter_value: str = Query(None, description="Filter value (JSON string for complex values)")
):
    """Return all top-level tasks with optional filtering and sorting."""
    try:
        filter_by = None
        if filter_type and filter_value:
            import json

            if filter_type == "priority":
                filter_by = {"priority": int(filter_value)}
            elif filter_type == "priority_range":
                range_values = json.loads(filter_value)
                filter_by = {"priority_range": range_values}
            elif filter_type == "status":
                filter_by = {"status": filter_value}
            elif filter_type in ["created_after", "created_before", "due_after", "due_before", "start_after", "start_before"]:
                from datetime import datetime
                date_value = datetime.strptime(filter_value, "%Y-%m-%d").date()
                filter_by = {filter_type: date_value}
            else:
                raise ValueError(f"Invalid filter_type: {filter_type}")
        
        return task_service.list_parent_tasks(sort_by=sort_by, filter_by=filter_by)
    
    except (ValueError, json.JSONDecodeError) as e:
        raise HTTPException(status_code=400, detail=f"Invalid filter parameters: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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



