from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from time import time
from typing import Any


class TaskStatus(str, Enum):
    CREATED = "created"
    QUEUED = "queued"
    ANALYZING = "analyzing"
    SELECTING_HOOK = "selecting_hook"
    SELECTING_HIGHLIGHTS = "selecting_highlights"
    INSERTING_MATERIALS = "inserting_materials"
    APPLYING_TRANSITIONS = "applying_transitions"
    ENHANCING_WITH_COMFYUI = "enhancing_with_comfyui"
    RENDERING_FINAL_VIDEO = "rendering_final_video"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class TaskRecord:
    task_id: str
    source_video: Path
    materials: list[Path]
    config: dict
    status: TaskStatus = TaskStatus.CREATED
    progress: int = 0
    stage: str = TaskStatus.CREATED.value
    message: str = "任务已创建"
    result_video: Path | None = None
    metadata_path: Path | None = None
    error: str | None = None
    created_at: float = field(default_factory=time)
    updated_at: float = field(default_factory=time)

    def to_response(self) -> dict:
        return {
            "task_id": self.task_id,
            "status": self.status.value,
            "progress": self.progress,
            "stage": self.stage,
            "message": self.message,
            "error": self.error,
            "result": {
                "video_url": f"/outputs/{self.task_id}/highlight.mp4"
                if self.result_video
                else None,
                "metadata_url": f"/outputs/{self.task_id}/metadata.json"
                if self.metadata_path
                else None,
            },
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "source_video": str(self.source_video),
            "materials": [str(material) for material in self.materials],
            "config": self.config,
            "status": self.status.value,
            "progress": self.progress,
            "stage": self.stage,
            "message": self.message,
            "result_video": str(self.result_video) if self.result_video else None,
            "metadata_path": str(self.metadata_path) if self.metadata_path else None,
            "error": self.error,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "TaskRecord":
        return cls(
            task_id=payload["task_id"],
            source_video=Path(payload["source_video"]),
            materials=[Path(material) for material in payload.get("materials", [])],
            config=payload.get("config", {}),
            status=TaskStatus(payload.get("status", TaskStatus.CREATED.value)),
            progress=int(payload.get("progress", 0)),
            stage=payload.get("stage", TaskStatus.CREATED.value),
            message=payload.get("message", "任务已创建"),
            result_video=Path(payload["result_video"]) if payload.get("result_video") else None,
            metadata_path=Path(payload["metadata_path"]) if payload.get("metadata_path") else None,
            error=payload.get("error"),
            created_at=float(payload.get("created_at", time())),
            updated_at=float(payload.get("updated_at", time())),
        )
