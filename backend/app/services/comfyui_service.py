from __future__ import annotations

from typing import Any

import httpx


class ComfyUIService:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")

    async def run_workflow(self, workflow: dict[str, Any]) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(f"{self.base_url}/prompt", json={"prompt": workflow})
            response.raise_for_status()
            return response.json()

    async def wait_for_result(self, prompt_id: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.get(f"{self.base_url}/history/{prompt_id}")
            response.raise_for_status()
            return response.json()

    async def health(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=3) as client:
                response = await client.get(f"{self.base_url}/system_stats")
            return response.status_code < 500
        except httpx.HTTPError:
            return False
