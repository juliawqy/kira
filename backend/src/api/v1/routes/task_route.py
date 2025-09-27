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
        task = task_service.add_task(**payload.model_dump())
        if not task:
            raise HTTPException(500, "Task created but not found")
        return task
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

@router.post("/{task_id}/start", response_model=TaskRead, name="start_task")
def start_task(task_id: int):
    """Set status to 'In progress'; return updated task."""
    try:
        return task_service.start_task(task_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/{task_id}/complete", response_model=TaskRead, name="complete_task")
def complete_task(task_id: int):
    """Set status to 'Completed'; optionally cascade to subTasks; return updated task."""
    try:
        return task_service.complete_task(task_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{task_id}/block", response_model=TaskRead, name="block_task")
def block_task(task_id: int):
    """Set status to 'Blocked'; return updated task."""
    try:
        return task_service.block_task(task_id)
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
    """Return all top-level tasks (tasks that are not referenced as a subtask)."""
    return task_service.list_parent_tasks()

@router.post(
    "/{task_id}/archive",
    response_model=TaskRead,
    name="archive_task",
)
def archive_task(task_id: int, detach_links: bool = Query(True, description="Detach parent/subtask links while archiving")):
    """Soft-delete a task (active=False). Optionally detach all links; return updated task."""
    try:
        return task_service.archive_task(task_id, detach_links=detach_links)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{task_id}/restore", response_model=TaskRead, name="restore_task")
def restore_task(task_id: int):
    """Restore a soft-deleted task (active=True); return updated task."""
    try:
        return task_service.restore_task(task_id)
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



