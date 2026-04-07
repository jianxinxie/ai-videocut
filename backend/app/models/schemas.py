from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class TaskConfig(BaseModel):
    target_duration: int = Field(default=180, ge=15, le=900)
    hook_duration: int = Field(default=8, ge=3, le=20)
    transition_type: Literal["cut", "fade", "crossfade"] = "fade"
    transition_duration: float = Field(default=0.6, ge=0.1, le=2.0)
    enable_comfyui: bool = False
    auto_insert_materials: bool = False


class TaskCreateResponse(BaseModel):
    task_id: str
    status: str


class TaskStateResponse(BaseModel):
    task_id: str
    status: str
    progress: int
    stage: str
    message: str
    error: str | None = None
    result: dict[str, str | None] | None = None
    created_at: float
    updated_at: float


class ResultResponse(BaseModel):
    task_id: str
    status: str
    video_url: str | None = None
    metadata_url: str | None = None


class Segment(BaseModel):
    start: float
    end: float
    score: float = 0.0
    duration: float = 0.0
    reasons: dict[str, Any] = Field(default_factory=dict)


class MaterialInsertion(BaseModel):
    type: str = "material"
    file: str
    source_path: str | None = None
    media_type: Literal["image", "video", "audio", "unsupported"] = "unsupported"
    insert_at: float
    duration: float
    after_segment_index: int | None = None
    rendered: bool = False
