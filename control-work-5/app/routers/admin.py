from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.dependencies import get_storage, require_admin
from app.schemas import AdminStatsResponse, UserContext
from app.storage import AppStorage

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stats", response_model=AdminStatsResponse)
def get_stats(
    _: UserContext = Depends(require_admin),
    storage: AppStorage = Depends(get_storage),
) -> dict:
    by_status = {"todo": 0, "in_progress": 0, "done": 0}
    for task in storage.tasks.values():
        by_status[task["status"]] += 1
    return {"total_tasks": len(storage.tasks), "by_status": by_status}


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_any_task(
    task_id: int,
    _: UserContext = Depends(require_admin),
    storage: AppStorage = Depends(get_storage),
) -> Response:
    if task_id not in storage.tasks:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    storage.tasks.pop(task_id, None)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
