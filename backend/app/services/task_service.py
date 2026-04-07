from __future__ import annotations

from pathlib import Path
from threading import RLock
from time import time
from uuid import uuid4

from ..core.constants import STAGE_MESSAGES
from ..core.config import settings
from ..models.task import TaskRecord, TaskStatus
from .task_repository import JsonTaskRepository


class TaskService:
    def __init__(self, repository: JsonTaskRepository) -> None:
        self._repository = repository
        self._records: dict[str, TaskRecord] = repository.load_all()
        self._lock = RLock()

    def create_task(self, source_video: Path, materials: list[Path], config: dict) -> TaskRecord:
        task_id = f"task_{uuid4().hex[:12]}"
        record = TaskRecord(
            task_id=task_id,
            source_video=source_video,
            materials=materials,
            config=config,
        )
        with self._lock:
            self._records[task_id] = record
            self._persist()
        return record

    def get_task(self, task_id: str) -> TaskRecord | None:
        with self._lock:
            return self._records.get(task_id)

    def list_tasks(self) -> list[TaskRecord]:
        with self._lock:
            return sorted(self._records.values(), key=lambda item: item.created_at, reverse=True)

    def update(
        self,
        task_id: str,
        status: TaskStatus,
        progress: int,
        message: str | None = None,
    ) -> TaskRecord:
        with self._lock:
            record = self._require(task_id)
            record.status = status
            record.stage = status.value
            record.progress = max(0, min(100, progress))
            record.message = message or STAGE_MESSAGES.get(status.value, status.value)
            record.updated_at = time()
            self._persist()
            return record

    def save(self, record: TaskRecord) -> TaskRecord:
        with self._lock:
            record.updated_at = time()
            self._records[record.task_id] = record
            self._persist()
            return record

    def complete(self, task_id: str, result_video: Path, metadata_path: Path) -> TaskRecord:
        with self._lock:
            record = self._require(task_id)
            record.status = TaskStatus.COMPLETED
            record.stage = TaskStatus.COMPLETED.value
            record.progress = 100
            record.message = STAGE_MESSAGES[TaskStatus.COMPLETED.value]
            record.result_video = result_video
            record.metadata_path = metadata_path
            record.updated_at = time()
            self._persist()
            return record

    def fail(self, task_id: str, error: str) -> TaskRecord:
        with self._lock:
            record = self._require(task_id)
            record.status = TaskStatus.FAILED
            record.stage = TaskStatus.FAILED.value
            record.progress = 100
            record.message = STAGE_MESSAGES[TaskStatus.FAILED.value]
            record.error = error
            record.updated_at = time()
            self._persist()
            return record

    def _require(self, task_id: str) -> TaskRecord:
        record = self._records.get(task_id)
        if record is None:
            raise KeyError(task_id)
        return record

    def _persist(self) -> None:
        self._repository.save_all(list(self._records.values()))


task_service = TaskService(JsonTaskRepository(settings.task_store_path))
