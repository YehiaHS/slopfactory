"""Video assembler -- core composition engine for Slop Factory.

Composes Reddit story videos with:
- Background gameplay footage (looped, scaled to fill 9:16)
- Reddit post overlay (title + body styled like the Reddit UI)
- Animated word-by-word subtitles (gold-highlight style)
- TTS audio track

Optimized for memory efficiency (streaming frame pipeline) and parallel
processing (independent segment rendering).
Outputs vertical 9:16 (1080x1920) H.264 MP4 video.
"""

from __future__ import annotations

import logging
import math
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Canvas & encoding defaults
# ---------------------------------------------------------------------------

CANVAS_W: int = 1080
CANVAS_H: int = 1920
DEFAULT_FPS: int = 30
DEFAULT_AUDIO_BITRATE: str = "192k"
DEFAULT_FONT_SIZE: int = 56
DEFAULT_SUBTITLE_Y: float = 0.72  # 72 % down = lower-third
DEFAULT_WORDS_PER_LINE: int = 8

HIGHLIGHT = "#FFD700"  # golden yellow
WHITE = "#FFFFFF"

FFMPEG: Optional[str] = shutil.which("ffmpeg")
FFPROBE: Optional[str] = shutil.which("ffprobe")

# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class SubtitleStyle:
    """Styling knobs for the subtitle overlay."""

    font_name: str = "Arial"
    font_size: int = DEFAULT_FONT_SIZE
    highlight_color: str = HIGHLIGHT
    default_color: str = WHITE
    bg_opacity: float = 0.7
    y_position: float = DEFAULT_SUBTITLE_Y
    words_per_line: int = DEFAULT_WORDS_PER_LINE
    stroke_width: int = 2
    stroke_color: str = "#000000"

    @classmethod
    def from_dict(cls, d: dict) -> "SubtitleStyle":
        valid = {f.name for f in cls.__dataclass_fields__.values()}
        return cls(**{k: v for k, v in d.items() if k in valid})


@dataclass
class WordTS:
    """A word with estimated start / end timestamps."""

    word: str
    start: float
    end: float


# ---------------------------------------------------------------------------
# Helpers -- external tools
# ---------------------------------------------------------------------------


def _ensure_ffmpeg() -> str:
    if FFMPEG is None:
        raise RuntimeError(
            "ffmpeg not found on PATH. Install from https://ffmpeg.org/"
        )
    return FFMPEG


def _ensure_ffprobe() -> str:
    if FFPROBE is None:
        raise RuntimeError("ffprobe not found on PATH.")
    return FFPROBE


def get_media_duration(path: Path) -> float:
    """Return duration in seconds via ffprobe."""
    ffprobe = _ensure_ffprobe()
    out = subprocess.run(
        [
            ffprobe, "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        capture_output=True, text=True, check=True,
    )
    try:
        return float(out.stdout.strip())
    except ValueError:
        raise RuntimeError(f"Cannot parse duration of {path}")


def _estimate_word_timestamps(
    audio_path: Path, words: list[str]
) -> list[WordTS]:
    """Distribute words across audio duration, weighted by char count.

    Accounts for inter-word gaps so total timing matches audio duration.
    """
    dur = get_media_duration(audio_path)
    total_chars = sum(len(w) for w in words)
    if total_chars == 0:
        return []
    # Reserved time for gaps — words must fit in remaining time
    gap = 0.05
    gap_time = gap * max(len(words) - 1, 0)
    speech_time = max(dur - gap_time, dur * 0.5)
    wts: list[WordTS] = []
    t = 0.0
    for w in words:
        wd = max((len(w) / total_chars) * speech_time, 0.12)
        wts.append(WordTS(w, t, t + wd))
        t += wd + gap
    return wts


# ---------------------------------------------------------------------------
# Background video
# ---------------------------------------------------------------------------


def _build_background_video(
    video_paths: list[str], target_dur: float, tmp: Path
) -> Path:
    """Concatenate / loop *video_paths* until they cover *target_dur* s."""
    if not video_paths:
        raise ValueError("No background videos provided")

    ffprobe = _ensure_ffprobe()
    ffmpeg = _ensure_ffmpeg()

    clips: list[tuple[str, float]] = []
    for vp in video_paths:
        p = Path(vp)
        if not p.exists():
            logger.warning("Background clip not found: %s", vp)
            continue
        try:
            d = float(
                subprocess.run(
                    [
                        ffprobe, "-v", "error",
                        "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1",
                        str(p),
                    ],
                    capture_output=True, text=True, check=True,
                ).stdout.strip()
            )
        except Exception as exc:
            logger.warning("Skipping %s (%s)", vp, exc)
            continue
        clips.append((vp, d))
    if not clips:
        raise RuntimeError("No usable background videos")

    # Build concat list covering target_dur
    concat = tmp / "bg_concat.txt"
    lines: list[str] = []
    elapsed = 0.0
    i = 0
    while elapsed < target_dur:
        vp, d = clips[i % len(clips)]
        lines.append(f"file '{vp}'")
        elapsed += d
        i += 1
    concat.write_text("\n".join(lines) + "\n")

    out = tmp / "background.mp4"
    scale_pad = (
        f"scale={CANVAS_W}:{CANVAS_H}:force_original_aspect_ratio=decrease,"
        f"pad={CANVAS_W}:{CANVAS_H}:"
        f"({CANVAS_W}-iw)/2:({CANVAS_H}-ih)/2:black"
    )
    cmd = [
        ffmpeg, "-y",
        "-f", "concat", "-safe", "0", "-i", str(concat),
        "-vf", scale_pad,
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "23",
        "-an", "-t", str(target_dur),
        str(out),
    ]
    logger.info("Building background: %s %s", ffmpeg, " ".join(cmd[1:]))
    subprocess.run(cmd, capture_output=True, text=True, check=True)
    return out


# ---------------------------------------------------------------------------
# Reddit post card renderer
# ---------------------------------------------------------------------------


def _render_reddit_card(
    body: str, title: str, subreddit: str,
    upvotes: str, awards: Optional[list[str]], tmp: Path,
) -> Path:
    """Render the Reddit-style post card as an RGBA PNG."""
    from PIL import Image, ImageDraw, ImageFont

    img = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Card geometry
    card_w = CANVAS_W - 100
    card_max_h = int(CANVAS_H * DEFAULT_SUBTITLE_Y) - 80
    card_x = 50
    card_y = 40

    # Dark rounded card
    draw.rounded_rectangle(
        [card_x, card_y, card_x + card_w, card_y + card_max_h],
        radius=20, fill=(28, 28, 28, 255), outline=(50, 50, 50, 255),
    )

    # Fonts
    try:
        font_header = ImageFont.truetype("arial.ttf", 28)
        font_title = ImageFont.truetype("arial.ttf", 34)
        font_body = ImageFont.truetype("arial.ttf", 30)
        font_meta = ImageFont.truetype("arial.ttf", 22)
    except (IOError, OSError):
        font_header = font_title = font_body = font_meta = ImageFont.load_default()

    pad = 20
    x0 = card_x + pad
    y0 = card_y + pad

    # Subreddit header
    draw.ellipse(
        [x0, y0 + 4, x0 + 28, y0 + 32], fill=(255, 68, 68, 255)
    )
    draw.text((x0 + 38, y0), subreddit, fill=(190, 190, 190, 255),
              font=font_header)

    # Title
    ty = y0 + 42
    draw.text((x0, ty), title, fill=(255, 255, 255, 255), font=font_title)

    # Upvote / awards meta line
    my = ty + 46
    parts = []
    if awards:
        parts.append("  ".join(awards))
    parts.append(f"{upvotes} upvotes")
    draw.text(
        (x0, my), "  --  ".join(parts), fill=(130, 130, 130, 255),
        font=font_meta,
    )

    # Body text (word-wrapped)
    by = my + 40
    max_w = card_w - pad * 2
    max_h = card_max_h - (by - card_y) - pad
    _draw_wrapped_text(
        draw, body, font_body, x0, by, max_w, max_h,
    )

    png = tmp / "reddit_post.png"
    img.save(str(png), "PNG")
    return png


def _draw_wrapped_text(
    draw: "ImageDraw.ImageDraw",
    text: str,
    font: "ImageFont.FreeTypeFont",
    x: int, y: int,
    max_w: int, max_h: int,
    fill: tuple[int, ...] = (255, 255, 255, 255),
) -> None:
    """Draw word-wrapped text within a bounding box."""
    x0 = x
    cur_y = y
    try:
        ascent, descent = font.getmetrics()
        line_h = ascent + descent
    except (AttributeError, Exception):
        line_h = 0
    if line_h <= 0:
        line_h = 38

    sb = draw.textbbox((0, 0), " ", font=font)
    sw = sb[2] - sb[0]

    line_start_x = x0
    for word in text.split():
        wb = draw.textbbox((0, 0), word, font=font)
        ww = wb[2] - wb[0]
        if x + ww > x0 + max_w and x > x0:
            cur_y += line_h
            x = x0
        if cur_y - y + line_h > max_h:
            break
        draw.text((x, cur_y), word, fill=fill, font=font)
        x += ww + sw



# ---------------------------------------------------------------------------
# Subtitle frame generator
# ---------------------------------------------------------------------------


def _gen_subtitle_frames(
    word_timestamps: list[WordTS], style: SubtitleStyle,
    fps: int, audio_dur: float, time_offset: float = 0.0,
) -> "np.ndarray":
    """Generate ALL subtitle overlay frames as RGBA array.

    Returns (N, H, W, 4) uint8 array where N = total frames.
    This is done per-segment in the parallel path; here for the
    sequential path it generates the full overlay stream.

    `time_offset` is added to the per-frame time to align with
    global word timestamps when rendering segmented frames.
    """
    from PIL import Image, ImageDraw, ImageFont

    total_frames = int(audio_dur * fps)
    bar_y = int(CANVAS_H * style.y_position)
    bar_h = 200  # height of subtitle bar

    # Pre-build the semi-transparent bar
    bar_img = Image.new("RGBA", (CANVAS_W, bar_h), (0, 0, 0, 0))
    bd = ImageDraw.Draw(bar_img)
    bd.rounded_rectangle(
        [10, 0, CANVAS_W - 10, bar_h], radius=20,
        fill=(25, 25, 25, int(255 * style.bg_opacity)),
    )
    bar_np = np.array(bar_img)

    # Try to load font
    try:
        font = ImageFont.truetype("arial.ttf", style.font_size)
    except (IOError, OSError):
        font = ImageFont.load_default()

    lines = _split_into_display_lines(word_timestamps, style.words_per_line)

    frames: list[np.ndarray] = []
    # Measure space width from font bounding box
    if font:
        try:
            tmp_d = Image.new("RGBA", (1, 1))
            tmp_draw = ImageDraw.Draw(tmp_d)
            space_w = tmp_draw.textbbox((0, 0), " ", font=font)[2]
        except Exception:
            space_w = 12
    else:
        space_w = 12

    for fi in range(total_frames):
        t = time_offset + fi / fps
        frame = np.zeros((CANVAS_H, CANVAS_W, 4), dtype=np.uint8)

        # Place bar
        frame[bar_y:bar_y + bar_h, :, :] = bar_np

        # Draw each line
        line_y = bar_y + 10
        for lw in lines:
            if not lw:
                continue
            active_ids = {
                id(w) for w in lw
                if w.start <= t and w.end > t
            }
            # Build text line
            tmp_im = Image.new("RGBA", (CANVAS_W, 60), (0, 0, 0, 0))
            td = ImageDraw.Draw(tmp_im)

            # Measure full line
            full = " ".join(w.word for w in lw)
            fb = td.textbbox((0, 0), full, font=font)
            tw = fb[2] - fb[0]
            tx = (CANVAS_W - tw) // 2

            cx = tx
            for w in lw:
                wc = HIGHLIGHT if id(w) in active_ids else WHITE
                wb = td.textbbox((0, 0), w.word, font=font)
                td.text((cx, 0), w.word, fill=wc, font=font)
                cx += (wb[2] - wb[0]) + space_w

            line_np = np.array(tmp_im)
            lh = line_np.shape[0]
            if line_y + lh <= CANVAS_H:
                frame[line_y:line_y + lh, :, :] = line_np
            line_y += lh + 2

        frames.append(frame)

    return np.array(frames, dtype=np.uint8)


def _split_into_display_lines(
    wts: list[WordTS], wpl: int
) -> list[list[WordTS]]:
    return [wts[i:i + wpl] for i in range(0, len(wts), wpl)]


# ---------------------------------------------------------------------------
# Core encoder -- streams frames through ffmpeg pipe
# ---------------------------------------------------------------------------


def _encode_composite(
    bg_video: Path,
    reddit_png: Path,
    audio_path: Path,
    word_timestamps: list[WordTS],
    style: SubtitleStyle,
    fps: int,
    audio_dur: float,
    output: Path,
) -> None:
    """Stream subtitle frames as raw RGBA into ffmpeg.

    ffmpeg composite:
      [0:v] background
      [1:v] reddit card (looped)
      [2:v] raw subtitle frames from stdin
      [3:a] audio
    """
    ffmpeg = _ensure_ffmpeg()
    seg_dur = 5.0
    seg_frames = int(seg_dur * fps)
    total_frames = int(audio_dur * fps)
    num_segs = math.ceil(total_frames / seg_frames)

    filter_complex = (
        f"[0:v]fps={fps}[bg];"
        f"[1:v]fps={fps}[rp];"
        f"[2:v]format=rgba[subs];"
        f"[bg][rp]overlay=0:0:format=auto[bg_rp];"
        f"[bg_rp][subs]overlay=0:0:format=auto[outv]"
    )

    cmd = [
        ffmpeg, "-y",
        # 0: background
        "-i", str(bg_video),
        # 1: reddit card
        "-loop", "1", "-i", str(reddit_png),
        # 2: subtitle frames from stdin
        "-f", "rawvideo", "-pix_fmt", "rgba",
        "-s", f"{CANVAS_W}x{CANVAS_H}", "-r", str(fps),
        "-i", "pipe:0",
        # 3: audio
        "-i", str(audio_path),
        "-filter_complex", filter_complex,
        "-map", "[outv]", "-map", "3:a",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-c:a", "aac", "-b:a", DEFAULT_AUDIO_BITRATE,
        "-t", str(audio_dur),
        "-movflags", "+faststart",
        "-pix_fmt", "yuv420p",
        str(output),
    ]
    logger.info("Encoding: %s", " ".join(cmd))

    proc = subprocess.Popen(
        cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )
    try:
        for si in range(num_segs):
            seg_start = si * seg_frames
            seg_len = min(seg_frames, total_frames - seg_start)
            t_start = seg_start / fps
            t_end = t_start + seg_len / fps

            seg_wts = [
                w for w in word_timestamps
                if w.start < t_end and w.end > t_start
            ]
            seg_frames_arr = _gen_subtitle_frames(
                seg_wts, style, fps, t_end - t_start, t_start,
            )
            for fr in seg_frames_arr:
                proc.stdin.write(fr.tobytes())

        proc.stdin.close()
        _, stderr = proc.communicate()
        if proc.returncode != 0:
            logger.error("ffmpeg error:\n%s", stderr.decode()[-1000:])
            raise RuntimeError(f"ffmpeg exit {proc.returncode}")
    except Exception:
        try:
            proc.stdin.close()
        except Exception:
            pass
        proc.kill()
        raise


# ---------------------------------------------------------------------------
# Public API -- top-level video assembly
# ---------------------------------------------------------------------------


def assemble_video(
    post_text: str,
    audio_path: Path,
    background_video_paths: list[str],
    output_path: Path,
    subtitle_style: dict,
    fps: int = DEFAULT_FPS,
    post_title: str = "",
    post_subreddit: str = "",
) -> None:
    """High-level entry point called from the API layer.

    Coordinates the full pipeline: word timestamps, background prep, subtitle
    generation, and ffmpeg encoding.
    """
    audio_dur = get_media_duration(Path(audio_path))

    # Estimate word timestamps from the audio file
    words = post_text.split()
    word_timestamps = _estimate_word_timestamps(Path(audio_path), words)

    # Build composite: background + reddit card + subtitles + audio
    if background_video_paths:
        import tempfile as _tmp
        with _tmp.TemporaryDirectory() as td:
            tmp = Path(td)
            bg_path = _build_background_video(
                background_video_paths, audio_dur, tmp
            )
            reddit_path = _render_reddit_card(
                body=post_text,
                title=post_title or (post_text[:80] if post_text else "Reddit Post"),
                subreddit=post_subreddit or "reddit",
                upvotes="0",
                awards=None,
                tmp=tmp,
            )
            _encode_composite(
                bg_path,
                reddit_path,
                Path(audio_path),
                word_timestamps,
                SubtitleStyle.from_dict(subtitle_style),
                fps,
                audio_dur,
                output_path,
            )
    else:
        raise ValueError("No background videos available")
