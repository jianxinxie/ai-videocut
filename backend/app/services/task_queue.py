from __future__ import annotations

from fastapi import BackgroundTasks

from ..workers.video_pipeline import run_video_pipeline


class BackgroundTaskQueue:
    name = "background_tasks"

    def enqueue_video_pipeline(self, background_tasks: BackgroundTasks, task_id: str) -> None:
        background_tasks.add_task(run_video_pipeline, task_id)


task_queue = BackgroundTaskQueue()
