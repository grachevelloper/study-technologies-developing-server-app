from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from app.dependencies import get_current_user, get_storage
from app.schemas import TaskCreate, TaskOut, TaskStatus, TaskStatusUpdate, UserContext
from app.storage import AppStorage

router = APIRouter(prefix="/tasks", tags=["tasks"])


def _get_owned_task_or_404(
    storage: AppStorage,
    task_id: int,
    user_id: int,
) -> dict:
    task = storage.tasks.get(task_id)
    if task is None or task["owner_id"] != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.post("", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(
    payload: TaskCreate,
    current_user: UserContext = Depends(get_current_user),
    storage: AppStorage = Depends(get_storage),
) -> dict:
    return storage.create_task({**payload.model_dump(), "owner_id": current_user.id})


@router.get("", response_model=list[TaskOut])
def list_tasks(
    status_filter: Optional[TaskStatus] = Query(default=None, alias="status"),
    min_priority: Optional[int] = Query(default=None, ge=1, le=5),
    current_user: UserContext = Depends(get_current_user),
    storage: AppStorage = Depends(get_storage),
) -> list[dict]:
    tasks = [
        task
        for task in storage.tasks.values()
        if task["owner_id"] == current_user.id
    ]
    if status_filter is not None:
        tasks = [task for task in tasks if task["status"] == status_filter]
    if min_priority is not None:
        tasks = [task for task in tasks if task["priority"] >= min_priority]
    return tasks


@router.get("/{task_id}", response_model=TaskOut)
def get_task(
    task_id: int,
    current_user: UserContext = Depends(get_current_user),
    storage: AppStorage = Depends(get_storage),
) -> dict:
    return _get_owned_task_or_404(storage, task_id, current_user.id)


@router.patch("/{task_id}/status", response_model=TaskOut)
def update_task_status(
    task_id: int,
    payload: TaskStatusUpdate,
    current_user: UserContext = Depends(get_current_user),
    storage: AppStorage = Depends(get_storage),
) -> dict:
    task = _get_owned_task_or_404(storage, task_id, current_user.id)
    task["status"] = payload.status
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    current_user: UserContext = Depends(get_current_user),
    storage: AppStorage = Depends(get_storage),
) -> Response:
    _get_owned_task_or_404(storage, task_id, current_user.id)
    storage.tasks.pop(task_id, None)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
