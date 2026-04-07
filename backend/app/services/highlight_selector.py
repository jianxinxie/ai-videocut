from __future__ import annotations

from ..models.schemas import Segment
from ..utils.time_utils import duration


class HighlightSelector:
    def select_highlights(
        self,
        segments: list[Segment],
        hook: Segment,
        target_duration: float,
        hook_duration: float,
    ) -> list[Segment]:
        remaining = max(0.0, target_duration - hook_duration)
        selected: list[Segment] = []
        total = 0.0
        if remaining < 1.0:
            return selected

        for segment in sorted(segments, key=lambda item: item.score, reverse=True):
            if self._overlaps(segment, hook):
                continue
            segment_duration = duration(segment.start, segment.end)
            if segment_duration <= 1.0:
                continue
            available = remaining - total
            if available < 1.0:
                break
            if total + segment_duration > remaining:
                segment = segment.model_copy(update={"end": segment.start + available})
                segment.duration = duration(segment.start, segment.end)
            selected.append(segment)
            total += segment.duration
            if total >= remaining:
                break

        return sorted(selected, key=lambda item: item.start)

    def _overlaps(self, left: Segment, right: Segment) -> bool:
        return left.start < right.end and right.start < left.end
