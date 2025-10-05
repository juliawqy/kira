# from __future__ import annotations
# from typing import List

# from fastapi import APIRouter, HTTPException
# from pydantic import BaseModel

# from backend.src.schemas.task import TaskCreate, TaskUpdate, TaskRead, TaskWithSubTasks
# import backend.src.services.task as task_service

# router = APIRouter(prefix="/task", tags=["task"])


# class CollaboratorsPayload(BaseModel):
#     """Body for collaborator assign/unassign."""
#     users: List[str]


# @router.post("/", response_model=TaskRead, status_code=201, name="create_task")
# def create_task(payload: TaskCreate):
#     """Create a task; return the task created."""
#     try:
#         t = task_service.add_task(**payload.model_dump())
#         if not t:
#             raise HTTPException(500, "Task created but not found")
#         return t
#     except ValueError as e:
#         raise HTTPException(status_code=400, detail=str(e))


# @router.get("/{task_id}", response_model=TaskWithSubTasks, name="get_task")
# def get_task(task_id: int):
#     """Get a task by id; return it with its subtasks."""
#     t = task_service.get_task_with_subtasks(task_id)
#     if not t:
#         raise HTTPException(404, "Task not found")
#     return t


# @router.get("/", response_model=List[TaskWithSubTasks], name="list_tasks")
# def list_tasks():
#     """List all parent tasks with subtasks."""
#     return task_service.list_parent_tasks()


# @router.patch("/{task_id}", response_model=TaskRead, name="update_task")
# def update_task(task_id: int, payload: TaskUpdate):
#     """Update a task (non-status); return the updated task."""
#     updated = task_service.update_task(task_id, **payload.model_dump(exclude_unset=True))
#     if not updated:
#         raise HTTPException(404, "Task not found")
#     return updated


# @router.delete("/{task_id}", name="delete_task")
# def delete_task(task_id: int):
#     """Delete a task; return the deleted task (pre-delete snapshot)."""
#     t = task_service.get_task_with_subtasks(task_id)
#     if not t:
#         raise HTTPException(404, "Task not found")
#     try:
#         return task_service.delete_task(task_id)
#     except ValueError as e:
#         raise HTTPException(status_code=404, detail=str(e))


# @router.post("/{task_id}/start", response_model=TaskRead, name="start_task")
# def start_task(task_id: int):
#     """Set status to 'In progress'; return updated task."""
#     try:
#         return task_service.start_task(task_id)
#     except ValueError as e:
#         raise HTTPException(status_code=404, detail=str(e))


# @router.post("/{task_id}/complete", response_model=TaskRead, name="complete_task")
# def complete_task(task_id: int):
#     """Set status to 'Completed'; return updated task."""
#     try:
#         return task_service.complete_task(task_id)
#     except ValueError as e:
#         raise HTTPException(status_code=404, detail=str(e))


# @router.post("/{task_id}/assign", response_model=TaskRead, name="assign_users")
# def assign_users(task_id: int, payload: CollaboratorsPayload):
#     """Assign collaborators; return updated task."""
#     try:
#         return task_service.assign_task(task_id, payload.users)
#     except ValueError as e:
#         raise HTTPException(status_code=404, detail=str(e))


# @router.post("/{task_id}/unassign", response_model=TaskRead, name="unassign_users")
# def unassign_users(task_id: int, payload: CollaboratorsPayload):
#     """Unassign collaborators; return updated task."""
#     try:
#         return task_service.unassign_task(task_id, payload.users)
#     except ValueError as e:
#         raise HTTPException(status_code=404, detail=str(e))


# @router.delete("/subtasks/{subtask_id}", response_model=bool, name="delete_subtask")
# def delete_subtask(subtask_id: int):
#     """Delete a subtask; return service result (True/False)."""
#     try:
#         return task_service.delete_subtask(subtask_id)
#     except ValueError as e:
#         raise HTTPException(status_code=400, detail=str(e))
