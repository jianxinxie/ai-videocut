from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.models.schemas import ResultResponse
from app.models.task import TaskStatus
from app.services.task_service import task_service

router = APIRouter(prefix="/tasks", tags=["results"])


@router.get("/{task_id}/result", response_model=ResultResponse)
async def get_result(task_id: str) -> ResultResponse:
    record = task_service.get_task(task_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Task not found")
    if record.status != TaskStatus.COMPLETED:
        return ResultResponse(task_id=task_id, status=record.status.value)
    return ResultResponse(
        task_id=task_id,
        status=record.status.value,
        video_url=f"/outputs/{task_id}/highlight.mp4" if record.result_video else None,
        metadata_url=f"/outputs/{task_id}/metadata.json" if record.metadata_path else None,
    )
