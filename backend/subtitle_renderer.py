"""Subtitle renderer — creates live subtitles in the Reddit story style.
Generates SRT files and renders subtitle overlays as images that can be
composited onto the video. Uses efficient batching.
"""

from pathlib import Path
from dataclasses import dataclass
from typing import List

@dataclass
class SubtitleCue:
    start: float  # seconds
    end: float    # seconds
    text: str


def generate_srt(cues: List[SubtitleCue], output_path: Path) -> Path:
    """Generate standard SRT subtitle file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    lines = []
    for idx, cue in enumerate(cues, 1):
        start_str = _format_srt_time(cue.start)
        end_str = _format_srt_time(cue.end)
        clean_text = cue.text.replace("\n", " ")
        lines.append(f"{idx}\n{start_str} --> {end_str}\n{clean_text}\n")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
        if lines and not lines[-1].endswith("\n"):
            f.write("\n")

    return output_path


def _format_srt_time(seconds: float) -> str:
    """Format seconds as SRT timestamp HH:MM:SS,mmm"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
