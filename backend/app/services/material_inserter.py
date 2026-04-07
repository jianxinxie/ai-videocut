from __future__ import annotations

from pathlib import Path

from ..models.schemas import MaterialInsertion, Segment

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
VIDEO_EXTENSIONS = {".mp4", ".mov", ".mkv", ".webm", ".avi", ".m4v"}
AUDIO_EXTENSIONS = {".mp3", ".wav", ".aac", ".m4a", ".flac", ".ogg"}


class MaterialInserter:
    def plan_insertions(
        self,
        materials: list[Path],
        highlights: list[Segment],
        enabled: bool,
        initial_offset: float = 0.0,
    ) -> list[MaterialInsertion]:
        if not enabled or not materials:
            return []

        insertions: list[MaterialInsertion] = []
        cursor = initial_offset
        visual_materials = [material for material in materials if self.media_type(material) in {"image", "video"}]
        for index, (material, segment) in enumerate(zip(visual_materials, highlights)):
            cursor += segment.duration
            insertions.append(
                MaterialInsertion(
                    file=material.name,
                    source_path=str(material),
                    media_type=self.media_type(material),
                    insert_at=round(cursor, 2),
                    duration=2.5,
                    after_segment_index=index,
                    rendered=True,
                )
            )

        for material in materials:
            media_type = self.media_type(material)
            if media_type not in {"image", "video"}:
                insertions.append(
                    MaterialInsertion(
                        file=material.name,
                        source_path=str(material),
                        media_type=media_type,
                        insert_at=round(cursor, 2),
                        duration=0.0,
                        rendered=False,
                    )
                )
        return insertions

    def media_type(self, material: Path) -> str:
        suffix = material.suffix.lower()
        if suffix in IMAGE_EXTENSIONS:
            return "image"
        if suffix in VIDEO_EXTENSIONS:
            return "video"
        if suffix in AUDIO_EXTENSIONS:
            return "audio"
        return "unsupported"
