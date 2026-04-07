from __future__ import annotations

import json
from pathlib import Path

from app.core.config import settings
from app.core.logger import get_logger
from app.models.schemas import MaterialInsertion, Segment, TaskConfig
from app.models.task import TaskStatus
from app.services.ffmpeg_service import FFmpegService, RenderItem
from app.services.highlight_selector import HighlightSelector
from app.services.hook_selector import HookSelector
from app.services.material_inserter import MaterialInserter
from app.services.storage_service import storage_service
from app.services.task_service import task_service
from app.services.transition_service import TransitionService
from app.services.video_analyzer import VideoAnalyzer
from app.utils.file_utils import ensure_dir

logger = get_logger(__name__)


def run_video_pipeline(task_id: str) -> None:
    record = task_service.get_task(task_id)
    if record is None:
        logger.error("Task %s not found", task_id)
        return

    try:
        config = TaskConfig.model_validate(record.config)
        output_dir = storage_service.task_output_dir(task_id)

        ffmpeg = FFmpegService()
        analyzer = VideoAnalyzer(ffmpeg)
        hook_selector = HookSelector()
        highlight_selector = HighlightSelector()
        material_inserter = MaterialInserter()
        transition_service = TransitionService()

        task_service.update(task_id, TaskStatus.QUEUED, 5)

        task_service.update(task_id, TaskStatus.ANALYZING, 15)
        segments = analyzer.analyze(record.source_video)

        task_service.update(task_id, TaskStatus.SELECTING_HOOK, 35)
        hook = hook_selector.select_hook(segments, config.hook_duration)

        task_service.update(task_id, TaskStatus.SELECTING_HIGHLIGHTS, 45)
        highlights = highlight_selector.select_highlights(
            segments=segments,
            hook=hook,
            target_duration=config.target_duration,
            hook_duration=hook.duration,
        )

        task_service.update(task_id, TaskStatus.INSERTING_MATERIALS, 55)
        insertions = material_inserter.plan_insertions(
            record.materials,
            highlights,
            config.auto_insert_materials,
            initial_offset=hook.duration,
        )

        if config.enable_comfyui:
            task_service.update(
                task_id,
                TaskStatus.ENHANCING_WITH_COMFYUI,
                65,
                "ComfyUI 集成点已启用；MVP 当前仅记录增强意图",
            )

        task_service.update(task_id, TaskStatus.APPLYING_TRANSITIONS, 70)
        transition_type = transition_service.normalize(config.transition_type)
        render_items = _build_render_items(record.source_video, hook, highlights, insertions)

        task_service.update(task_id, TaskStatus.RENDERING_FINAL_VIDEO, 82)
        result_video = ffmpeg.render_items(
            items=render_items,
            output_dir=output_dir,
            transition_type=transition_type,
            transition_duration=config.transition_duration,
        )

        metadata_path = _write_metadata(
            output_dir=output_dir,
            task_id=task_id,
            source_video=record.source_video,
            config=config,
            segments=segments,
            hook=hook,
            highlights=highlights,
            insertions=insertions,
            render_items=render_items,
            transition_type=transition_type,
            result_video=result_video,
        )
        task_service.complete(task_id, result_video=result_video, metadata_path=metadata_path)
        logger.info("Task %s completed: %s", task_id, result_video)
    except Exception as exc:
        logger.exception("Task %s failed", task_id)
        task_service.fail(task_id, str(exc))


def _write_metadata(
    output_dir: Path,
    task_id: str,
    source_video: Path,
    config: TaskConfig,
    segments,
    hook,
    highlights,
    insertions,
    render_items,
    transition_type: str,
    result_video: Path,
) -> Path:
    metadata_path = output_dir / "metadata.json"
    payload = {
        "task_id": task_id,
        "source_video": str(source_video),
        "config": config.model_dump(),
        "transition_type": transition_type,
        "segments": [segment.model_dump() for segment in segments],
        "hook": hook.model_dump(),
        "highlights": [segment.model_dump() for segment in highlights],
        "material_insertions": [insertion.model_dump() for insertion in insertions],
        "timeline": [
            {
                "kind": item.kind,
                "file": item.path.name,
                "start": item.start,
                "end": item.end,
                "duration": item.duration,
                "label": item.label,
            }
            for item in render_items
        ],
        "result_video": str(result_video),
    }
    metadata_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return metadata_path


def _build_render_items(
    source_video: Path,
    hook: Segment,
    highlights: list[Segment],
    insertions: list[MaterialInsertion],
) -> list[RenderItem]:
    items = [
        RenderItem(
            kind="source",
            path=source_video,
            start=hook.start,
            end=hook.end,
            duration=hook.duration,
            label="hook",
        )
    ]
    rendered_insertions = {
        insertion.after_segment_index: insertion
        for insertion in insertions
        if insertion.rendered and insertion.after_segment_index is not None and insertion.source_path
    }

    for index, segment in enumerate(highlights):
        items.append(
            RenderItem(
                kind="source",
                path=source_video,
                start=segment.start,
                end=segment.end,
                duration=segment.duration,
                label=f"highlight_{index:03d}",
            )
        )
        insertion = rendered_insertions.get(index)
        if insertion is None or insertion.source_path is None:
            continue
        if insertion.media_type == "image":
            kind = "material_image"
        elif insertion.media_type == "video":
            kind = "material_video"
        else:
            continue
        items.append(
            RenderItem(
                kind=kind,
                path=Path(insertion.source_path),
                start=0.0,
                end=insertion.duration,
                duration=insertion.duration,
                label=f"material_{index:03d}",
            )
        )

    return items
