from __future__ import annotations

import json
from json import JSONDecodeError
from pathlib import Path
from threading import RLock

from ..core.logger import get_logger
from ..models.task import TaskRecord
from ..utils.file_utils import ensure_dir

logger = get_logger(__name__)


class JsonTaskRepository:
    def __init__(self, path: Path) -> None:
        self.path = path
        self._lock = RLock()

    def load_all(self) -> dict[str, TaskRecord]:
        with self._lock:
            if not self.path.exists():
                return {}
            try:
                raw = json.loads(self.path.read_text(encoding="utf-8") or "[]")
            except JSONDecodeError as exc:
                backup_path = self.path.with_suffix(f"{self.path.suffix}.bad")
                self.path.replace(backup_path)
                logger.error("Task store was invalid JSON and was moved to %s: %s", backup_path, exc)
                return {}
            if not isinstance(raw, list):
                backup_path = self.path.with_suffix(f"{self.path.suffix}.bad")
                self.path.replace(backup_path)
                logger.error("Task store root was not a list and was moved to %s", backup_path)
                return {}

            records: list[TaskRecord] = []
            for item in raw:
                try:
                    records.append(TaskRecord.from_dict(item))
                except (KeyError, TypeError, ValueError) as exc:
                    logger.warning("Skipping invalid task record in %s: %s", self.path, exc)
            return {record.task_id: record for record in records}

    def save_all(self, records: list[TaskRecord]) -> None:
        with self._lock:
            ensure_dir(self.path.parent)
            temp_path = self.path.with_suffix(f"{self.path.suffix}.tmp")
            payload = [record.to_dict() for record in records]
            temp_path.write_text(
                json.dumps(payload, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            temp_path.replace(self.path)
