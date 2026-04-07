from __future__ import annotations

from app.models.schemas import Segment
from app.utils.time_utils import clamp_duration, duration


class HookSelector:
    def select_hook(self, segments: list[Segment], hook_duration: float) -> Segment:
        if not segments:
            raise ValueError("No segments available for hook selection")
        best = max(segments, key=lambda item: item.score)
        start, end = clamp_duration(best.start, best.end, hook_duration)
        return best.model_copy(update={"start": start, "end": end, "duration": duration(start, end)})
