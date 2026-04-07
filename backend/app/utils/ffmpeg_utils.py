from __future__ import annotations

import subprocess
from pathlib import Path


class FFmpegError(RuntimeError):
    pass


def run_command(command: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        command,
        cwd=str(cwd) if cwd else None,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        raise FFmpegError(
            f"Command failed ({completed.returncode}): {' '.join(command)}\n{completed.stderr[-4000:]}"
        )
    return completed


def quote_concat_path(path: Path) -> str:
    escaped = str(path.resolve()).replace("'", "'\\''")
    return f"file '{escaped}'\n"
