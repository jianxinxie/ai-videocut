from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from app.core.logger import get_logger
from app.utils.ffmpeg_utils import quote_concat_path, run_command
from app.utils.file_utils import ensure_dir

logger = get_logger(__name__)

STANDARD_VIDEO_FILTER = (
    "fps=30,"
    "scale=1280:720:force_original_aspect_ratio=decrease,"
    "pad=1280:720:(ow-iw)/2:(oh-ih)/2,"
    "setsar=1,format=yuv420p"
)


@dataclass(frozen=True)
class RenderItem:
    kind: Literal["source", "material_video", "material_image"]
    path: Path
    start: float
    end: float
    duration: float
    label: str


class FFmpegService:
    def probe_duration(self, video_path: Path) -> float:
        completed = run_command(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(video_path),
            ]
        )
        return max(0.0, float(completed.stdout.strip()))

    def has_audio(self, video_path: Path) -> bool:
        completed = run_command(
            [
                "ffprobe",
                "-v",
                "error",
                "-select_streams",
                "a",
                "-show_entries",
                "stream=index",
                "-of",
                "json",
                str(video_path),
            ]
        )
        return bool(json.loads(completed.stdout or "{}").get("streams"))

    def detect_scenes(self, video_path: Path) -> list[float]:
        completed = run_command(
            [
                "ffmpeg",
                "-hide_banner",
                "-i",
                str(video_path),
                "-filter:v",
                "select=gt(scene\\,0.35),showinfo",
                "-f",
                "null",
                "-",
            ]
        )
        return [
            float(match.group(1))
            for match in re.finditer(r"pts_time:([0-9]+(?:\.[0-9]+)?)", completed.stderr)
        ]

    def measure_volume(self, video_path: Path, start: float, duration: float) -> str:
        completed = run_command(
            [
                "ffmpeg",
                "-hide_banner",
                "-ss",
                f"{start:.3f}",
                "-t",
                f"{duration:.3f}",
                "-i",
                str(video_path),
                "-af",
                "volumedetect",
                "-f",
                "null",
                "-",
            ]
        )
        return completed.stderr

    def cut_clip(self, source: Path, start: float, end: float, output: Path) -> Path:
        ensure_dir(output.parent)
        duration = max(0.1, end - start)
        command = [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-ss",
            f"{start:.3f}",
            "-t",
            f"{duration:.3f}",
            "-i",
            str(source),
        ]
        if self.has_audio(source):
            command.extend(["-map", "0:v:0", "-map", "0:a:0"])
        else:
            command.extend(
                [
                    "-f",
                    "lavfi",
                    "-t",
                    f"{duration:.3f}",
                    "-i",
                    "anullsrc=channel_layout=stereo:sample_rate=44100",
                    "-map",
                    "0:v:0",
                    "-map",
                    "1:a:0",
                ]
            )
        command.extend(
            [
                "-vf",
                STANDARD_VIDEO_FILTER,
                "-c:v",
                "libx264",
                "-preset",
                "veryfast",
                "-crf",
                "23",
                "-c:a",
                "aac",
                "-ar",
                "44100",
                "-ac",
                "2",
                "-shortest",
                "-movflags",
                "+faststart",
                str(output),
            ]
        )
        run_command(command)
        return output

    def render_image_clip(self, source: Path, duration: float, output: Path) -> Path:
        ensure_dir(output.parent)
        run_command(
            [
                "ffmpeg",
                "-y",
                "-hide_banner",
                "-loop",
                "1",
                "-t",
                f"{duration:.3f}",
                "-i",
                str(source),
                "-f",
                "lavfi",
                "-t",
                f"{duration:.3f}",
                "-i",
                "anullsrc=channel_layout=stereo:sample_rate=44100",
                "-map",
                "0:v:0",
                "-map",
                "1:a:0",
                "-vf",
                STANDARD_VIDEO_FILTER,
                "-c:v",
                "libx264",
                "-preset",
                "veryfast",
                "-crf",
                "23",
                "-c:a",
                "aac",
                "-ar",
                "44100",
                "-ac",
                "2",
                "-shortest",
                "-movflags",
                "+faststart",
                str(output),
            ]
        )
        return output

    def apply_fade(self, clip: Path, output: Path, duration: float) -> Path:
        clip_duration = self.probe_duration(clip)
        fade_duration = min(duration, max(0.1, clip_duration / 3))
        fade_out_start = max(0.0, clip_duration - fade_duration)
        command = [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-i",
            str(clip),
            "-vf",
            f"fade=t=in:st=0:d={fade_duration:.3f},fade=t=out:st={fade_out_start:.3f}:d={fade_duration:.3f}",
        ]
        if self.has_audio(clip):
            command.extend(
                [
                    "-af",
                    f"afade=t=in:st=0:d={fade_duration:.3f},afade=t=out:st={fade_out_start:.3f}:d={fade_duration:.3f}",
                ]
            )
        command.extend(
            [
                "-c:v",
                "libx264",
                "-preset",
                "veryfast",
                "-crf",
                "23",
                "-c:a",
                "aac",
                "-ar",
                "44100",
                "-ac",
                "2",
                "-movflags",
                "+faststart",
                str(output),
            ]
        )
        run_command(command)
        return output

    def concat_clips(self, clips: list[Path], output: Path) -> Path:
        ensure_dir(output.parent)
        concat_file = output.parent / "concat.txt"
        concat_file.write_text("".join(quote_concat_path(clip) for clip in clips), encoding="utf-8")
        run_command(
            [
                "ffmpeg",
                "-y",
                "-hide_banner",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(concat_file),
                "-c",
                "copy",
                "-movflags",
                "+faststart",
                str(output),
            ]
        )
        return output

    def crossfade_clips(self, clips: list[Path], output: Path, transition_duration: float) -> Path:
        if len(clips) < 2:
            return self.concat_clips(clips, output)

        durations = [self.probe_duration(clip) for clip in clips]
        has_audio = all(self.has_audio(clip) for clip in clips)
        fade_duration = min(transition_duration, max(0.1, min(durations) / 3))
        inputs: list[str] = []
        for clip in clips:
            inputs.extend(["-i", str(clip)])

        filters: list[str] = []
        previous_video = "0:v"
        previous_audio = "0:a"
        elapsed = durations[0]
        for index in range(1, len(clips)):
            video_label = f"v{index}"
            offset = max(0.0, elapsed - fade_duration)
            filters.append(
                f"[{previous_video}][{index}:v]xfade=transition=fade:duration={fade_duration:.3f}:offset={offset:.3f}[{video_label}]"
            )
            previous_video = video_label
            elapsed += durations[index] - fade_duration

            if has_audio:
                audio_label = f"a{index}"
                filters.append(f"[{previous_audio}][{index}:a]acrossfade=d={fade_duration:.3f}[{audio_label}]")
                previous_audio = audio_label

        command = ["ffmpeg", "-y", "-hide_banner", *inputs, "-filter_complex", ";".join(filters)]
        command.extend(["-map", f"[{previous_video}]"])
        if has_audio:
            command.extend(["-map", f"[{previous_audio}]"])
        else:
            command.append("-an")
        command.extend(
            [
                "-c:v",
                "libx264",
                "-preset",
                "veryfast",
                "-crf",
                "23",
                "-c:a",
                "aac",
                "-ar",
                "44100",
                "-ac",
                "2",
                "-movflags",
                "+faststart",
                str(output),
            ]
        )
        run_command(command)
        return output

    def render_clips(
        self,
        source: Path,
        timeline: list[tuple[float, float]],
        output_dir: Path,
        transition_type: str,
        transition_duration: float,
    ) -> Path:
        ensure_dir(output_dir)
        clip_dir = ensure_dir(output_dir / "clips")
        clips = [
            self.cut_clip(source, start, end, clip_dir / f"clip_{index:03d}.mp4")
            for index, (start, end) in enumerate(timeline)
            if end - start > 0.5
        ]
        if not clips:
            raise ValueError("No renderable clips selected")
        return self.finalize_clips(clips, output_dir, transition_type, transition_duration)

    def render_items(
        self,
        items: list[RenderItem],
        output_dir: Path,
        transition_type: str,
        transition_duration: float,
    ) -> Path:
        ensure_dir(output_dir)
        clip_dir = ensure_dir(output_dir / "clips")
        clips: list[Path] = []

        for index, item in enumerate(items):
            output = clip_dir / f"clip_{index:03d}_{item.label}.mp4"
            if item.kind in {"source", "material_video"}:
                duration = item.duration if item.kind == "material_video" else max(0.1, item.end - item.start)
                clips.append(self.cut_clip(item.path, item.start, item.start + duration, output))
            elif item.kind == "material_image":
                clips.append(self.render_image_clip(item.path, item.duration, output))

        if not clips:
            raise ValueError("No renderable clips selected")

        return self.finalize_clips(clips, output_dir, transition_type, transition_duration)

    def finalize_clips(
        self,
        clips: list[Path],
        output_dir: Path,
        transition_type: str,
        transition_duration: float,
    ) -> Path:
        clip_dir = ensure_dir(output_dir / "clips")
        output = output_dir / "highlight.mp4"
        if transition_type == "crossfade":
            try:
                return self.crossfade_clips(clips, output, transition_duration)
            except Exception as exc:
                logger.warning("Crossfade render failed, falling back to fade+concat: %s", exc)
                transition_type = "fade"

        if transition_type == "fade":
            faded = [
                self.apply_fade(clip, clip_dir / f"faded_{index:03d}.mp4", transition_duration)
                for index, clip in enumerate(clips)
            ]
            return self.concat_clips(faded, output)

        return self.concat_clips(clips, output)
