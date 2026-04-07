from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    app_name: str = "AI Highlight Video Agent"
    app_env: str = os.getenv("APP_ENV", "local")
    api_prefix: str = "/api"
    comfyui_base_url: str = os.getenv("COMFYUI_BASE_URL", "http://127.0.0.1:8188")
    storage_provider: str = os.getenv("STORAGE_PROVIDER", "local")
    queue_backend: str = os.getenv("QUEUE_BACKEND", "background_tasks")
    cors_origins: tuple[str, ...] = tuple(
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://127.0.0.1:5173,http://localhost:5173",
        ).split(",")
        if origin.strip()
    )
    backend_dir: Path = Path(__file__).resolve().parents[2]

    @property
    def upload_dir(self) -> Path:
        return Path(os.getenv("UPLOAD_DIR", self.backend_dir / "uploads")).resolve()

    @property
    def output_dir(self) -> Path:
        return Path(os.getenv("OUTPUT_DIR", self.backend_dir / "outputs")).resolve()

    @property
    def temp_dir(self) -> Path:
        return Path(os.getenv("TEMP_DIR", self.backend_dir / "temp")).resolve()

    @property
    def data_dir(self) -> Path:
        return Path(os.getenv("DATA_DIR", self.backend_dir / "data")).resolve()

    @property
    def task_store_path(self) -> Path:
        return Path(os.getenv("TASK_STORE_PATH", self.data_dir / "tasks.json")).resolve()


settings = Settings()
