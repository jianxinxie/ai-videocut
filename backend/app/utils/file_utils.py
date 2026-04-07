from __future__ import annotations

import re
from pathlib import Path

from fastapi import UploadFile


SAFE_NAME_PATTERN = re.compile(r"[^A-Za-z0-9._-]+")


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def safe_filename(filename: str | None, fallback: str) -> str:
    if not filename:
        return fallback
    cleaned = SAFE_NAME_PATTERN.sub("_", Path(filename).name).strip("._")
    return cleaned or fallback


async def save_upload_file(upload: UploadFile, destination: Path) -> Path:
    ensure_dir(destination.parent)
    with destination.open("wb") as output:
        while chunk := await upload.read(1024 * 1024):
            output.write(chunk)
    await upload.close()
    return destination
