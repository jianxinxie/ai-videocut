from __future__ import annotations

from ..core.constants import SUPPORTED_TRANSITIONS


class TransitionService:
    def normalize(self, transition_type: str) -> str:
        if transition_type not in SUPPORTED_TRANSITIONS:
            return "fade"
        return transition_type
