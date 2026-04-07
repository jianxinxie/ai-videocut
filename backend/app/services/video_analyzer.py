from __future__ import annotations

import math
import re
from pathlib import Path

from app.core.logger import get_logger
from app.models.schemas import Segment
from app.services.ffmpeg_service import FFmpegService
from app.utils.ffmpeg_utils import FFmpegError

logger = get_logger(__name__)


class VideoAnalyzer:
    def __init__(self, ffmpeg: FFmpegService) -> None:
        self.ffmpeg = ffmpeg

    def analyze(self, video_path: Path) -> list[Segment]:
        duration = self.ffmpeg.probe_duration(video_path)
        scene_points = self._detect_scene_points(video_path, duration)
        segments = self._build_segments(duration, scene_points)
        scored = [self._score_segment(video_path, segment, index) for index, segment in enumerate(segments)]
        logger.info("Analyzed %s into %s segments", video_path, len(scored))
        return scored

    def _detect_scene_points(self, video_path: Path, duration: float) -> list[float]:
        try:
            points = self.ffmpeg.detect_scenes(video_path)
        except FFmpegError as exc:
            logger.warning("FFmpeg scene detection failed, falling back to uniform segments: %s", exc)
            return []
        return [point for point in points if 1.0 < point < duration - 1.0]

    def _build_segments(self, video_duration: float, scene_points: list[float]) -> list[Segment]:
        if not scene_points:
            step = 8.0
            return [
                Segment(start=start, end=min(video_duration, start + step), duration=min(step, video_duration - start))
                for start in self._float_range(0.0, video_duration, step)
                if video_duration - start > 1.0
            ]

        boundaries = [0.0, *scene_points, video_duration]
        merged: list[Segment] = []
        start = boundaries[0]
        for end in boundaries[1:]:
            if end - start < 3.0:
                continue
            merged.append(Segment(start=start, end=end, duration=end - start))
            start = end
        if not merged:
            return self._build_segments(video_duration, [])
        return merged

    def _score_segment(self, video_path: Path, segment: Segment, index: int) -> Segment:
        volume_score = self._volume_score(video_path, segment)
        duration_score = 1.0 - min(abs(segment.duration - 8.0) / 12.0, 1.0)
        rhythm_score = 0.5 + (math.sin(segment.start * 0.37 + index) * 0.5)
        score = (volume_score * 0.5) + (duration_score * 0.3) + (rhythm_score * 0.2)
        segment.score = round(max(0.05, min(score, 1.0)), 4)
        segment.reasons = {
            "audio_score": round(volume_score, 4),
            "duration_score": round(duration_score, 4),
            "rhythm_score": round(rhythm_score, 4),
            "method": "ffmpeg_scene_audio_heuristic",
        }
        return segment

    def _volume_score(self, video_path: Path, segment: Segment) -> float:
        try:
            stderr = self.ffmpeg.measure_volume(video_path, segment.start, min(segment.duration, 12.0))
        except FFmpegError:
            return 0.4
        match = re.search(r"max_volume:\s*(-?\d+(?:\.\d+)?) dB", stderr)
        if not match:
            return 0.4
        max_volume = float(match.group(1))
        return max(0.0, min((max_volume + 60.0) / 60.0, 1.0))

    def _float_range(self, start: float, stop: float, step: float) -> list[float]:
        values: list[float] = []
        current = start
        while current < stop:
            values.append(round(current, 3))
            current += step
        return values
