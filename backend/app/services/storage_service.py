from __future__ import annotations

from pathlib import Path

from fastapi import UploadFile

from ..core.config import settings
from ..utils.file_utils import ensure_dir, safe_filename, save_upload_file


class LocalStorageService:
    def __init__(self, upload_dir: Path, output_dir: Path, temp_dir: Path) -> None:
        self.upload_dir = upload_dir
        self.output_dir = output_dir
        self.temp_dir = temp_dir

    def ensure_roots(self) -> None:
        ensure_dir(self.upload_dir)
        ensure_dir(self.output_dir)
        ensure_dir(self.temp_dir)

    def task_upload_dir(self, task_id: str) -> Path:
        return ensure_dir(self.upload_dir / task_id)

    def task_output_dir(self, task_id: str) -> Path:
        return ensure_dir(self.output_dir / task_id)

    async def save_source_video(self, task_id: str, upload: UploadFile) -> Path:
        source_name = safe_filename(upload.filename, "source.mp4")
        return await save_upload_file(upload, self.task_upload_dir(task_id) / source_name)

    async def save_materials(self, task_id: str, uploads: list[UploadFile] | None) -> list[Path]:
        materials_dir = ensure_dir(self.task_upload_dir(task_id) / "materials")
        material_paths: list[Path] = []
        for index, upload in enumerate(uploads or []):
            material_name = safe_filename(upload.filename, f"material_{index}")
            material_paths.append(await save_upload_file(upload, materials_dir / material_name))
        return material_paths


storage_service = LocalStorageService(
    upload_dir=settings.upload_dir,
    output_dir=settings.output_dir,
    temp_dir=settings.temp_dir,
)
