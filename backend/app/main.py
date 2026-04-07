from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from app.api import routes_comfyui, routes_result, routes_tasks, routes_upload
    from app.core.config import settings
    from app.core.logger import configure_logging
    from app.services.task_service import task_service
    from app.services.storage_service import storage_service
    from app.utils.file_utils import ensure_dir
else:
    from .api import routes_comfyui, routes_result, routes_tasks, routes_upload
    from .core.config import settings
    from .core.logger import configure_logging
    from .services.task_service import task_service
    from .services.storage_service import storage_service
    from .utils.file_utils import ensure_dir

configure_logging()

storage_service.ensure_roots()
ensure_dir(settings.data_dir)

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes_tasks.router, prefix=settings.api_prefix)
app.include_router(routes_result.router, prefix=settings.api_prefix)
app.include_router(routes_upload.router, prefix=settings.api_prefix)
app.include_router(routes_comfyui.router, prefix=settings.api_prefix)
app.mount("/outputs", StaticFiles(directory=str(settings.output_dir)), name="outputs")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.websocket("/ws/tasks/{task_id}")
async def task_progress_ws(websocket: WebSocket, task_id: str) -> None:
    await websocket.accept()
    try:
        while True:
            record = task_service.get_task(task_id)
            if record is None:
                await websocket.send_json({"error": "Task not found"})
                await websocket.close(code=1008)
                return
            payload = record.to_response()
            await websocket.send_json(payload)
            if payload["status"] in {"completed", "failed"}:
                return
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        return


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000)
