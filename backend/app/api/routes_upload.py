from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/uploads", tags=["uploads"])


@router.get("/limits")
async def upload_limits() -> dict[str, str | int]:
    return {
        "source_video": "required",
        "materials": "optional",
        "note": "Local MVP stores uploads on disk under backend/uploads/{task_id}.",
        "max_materials_recommended": 20,
    }
