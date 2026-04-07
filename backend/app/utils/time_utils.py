from __future__ import annotations


def clamp_duration(start: float, end: float, max_duration: float) -> tuple[float, float]:
    if end <= start:
        return start, start
    return start, min(end, start + max_duration)


def duration(start: float, end: float) -> float:
    return max(0.0, end - start)
