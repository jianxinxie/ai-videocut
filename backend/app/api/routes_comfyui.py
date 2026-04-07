from __future__ import annotations

from fastapi import APIRouter

from ..core.config import settings
from ..services.comfyui_service import ComfyUIService

router = APIRouter(prefix="/comfyui", tags=["comfyui"])


@router.get("/health")
async def comfyui_health() -> dict[str, str | bool]:
    service = ComfyUIService(settings.comfyui_base_url)
    available = await service.health()
    return {
        "base_url": settings.comfyui_base_url,
        "available": available,
        "status": "available" if available else "unavailable",
    }
