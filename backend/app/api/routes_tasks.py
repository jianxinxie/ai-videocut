from __future__ import annotations

import json

from fastapi import APIRouter, BackgroundTasks, File, Form, HTTPException, UploadFile, status
from pydantic import ValidationError

from app.core.logger import get_logger
from app.models.schemas import TaskConfig, TaskCreateResponse, TaskStateResponse
from app.models.task import TaskStatus
from app.services.storage_service import storage_service
from app.services.task_queue import task_queue
from app.services.task_service import task_service

router = APIRouter(prefix="/tasks", tags=["tasks"])
logger = get_logger(__name__)


@router.post("", response_model=TaskCreateResponse)
async def create_task(
    background_tasks: BackgroundTasks,
    source_video: UploadFile = File(...),
    materials: list[UploadFile] | None = File(default=None),
    config: str = Form(default="{}"),
) -> TaskCreateResponse:
    parsed_config = _parse_config(config)
    record = task_service.create_task(source_video=storage_service.upload_dir / "_pending", materials=[], config={})
    try:
        record.source_video = await storage_service.save_source_video(record.task_id, source_video)
        record.materials = await storage_service.save_materials(record.task_id, materials)
        record.config = parsed_config.model_dump()
        record.status = TaskStatus.CREATED
        record.stage = TaskStatus.CREATED.value
        record.message = "任务已创建"
        task_service.save(record)
    except Exception as exc:
        logger.exception("Failed to save uploads for task %s", record.task_id)
        task_service.fail(record.task_id, f"Upload failed: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed for task {record.task_id}",
        ) from exc

    task_queue.enqueue_video_pipeline(background_tasks, record.task_id)
    return TaskCreateResponse(task_id=record.task_id, status=record.status.value)


@router.post("/{task_id}/start", response_model=TaskStateResponse)
async def start_task(task_id: str, background_tasks: BackgroundTasks) -> TaskStateResponse:
    record = task_service.get_task(task_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Task not found")
    if record.status not in {TaskStatus.CREATED, TaskStatus.FAILED}:
        return TaskStateResponse.model_validate(record.to_response())
    record.error = None
    task_service.save(record)
    task_queue.enqueue_video_pipeline(background_tasks, task_id)
    return TaskStateResponse.model_validate(record.to_response())


@router.get("", response_model=list[TaskStateResponse])
async def list_tasks() -> list[TaskStateResponse]:
    return [TaskStateResponse.model_validate(record.to_response()) for record in task_service.list_tasks()]


@router.get("/{task_id}", response_model=TaskStateResponse)
async def get_task(task_id: str) -> TaskStateResponse:
    record = task_service.get_task(task_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskStateResponse.model_validate(record.to_response())


def _parse_config(raw_config: str) -> TaskConfig:
    try:
        parsed = json.loads(raw_config or "{}")
        return TaskConfig.model_validate(parsed)
    except (json.JSONDecodeError, ValidationError) as exc:
        raise HTTPException(status_code=400, detail=f"Invalid config: {exc}") from exc
