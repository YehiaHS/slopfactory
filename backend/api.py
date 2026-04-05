"""Slop Factory API Server — FastAPI backend."""

import os
import re
import time
import uuid
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

_UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from config import settings
import reddit_fetcher as reddit
from tts_service import generate_tts_audio, AVAILABLE_VOICES
from subtitle_renderer import generate_srt, SubtitleCue
from asset_manager import get_assets, get_categories, get_random_asset
from video_assembler import assemble_video

# Job management — persisted to disk for history
JOBS_FILE = Path(settings.output_dir) / "jobs.json"
jobs_lock = Lock()
executor = ThreadPoolExecutor(max_workers=settings.max_concurrent_jobs)

def _load_jobs() -> dict[str, dict]:
    if JOBS_FILE.exists():
        try:
            return json.loads(JOBS_FILE.read_text())
        except Exception:
            return {}
    return {}

def _save_jobs() -> None:
    JOBS_FILE.parent.mkdir(parents=True, exist_ok=True)
    JOBS_FILE.write_text(json.dumps(jobs, indent=2))

jobs: dict[str, dict] = _load_jobs()


class FetchPostsRequest(BaseModel):
    subreddits: list[str] = []
    sort: str = "top"
    time_filter: str = "week"
    limit: int = 10


class GenerateRequest(BaseModel):
    post_id: str
    post_title: str
    post_text: str
    post_subreddit: str
    voice: str = "voice_troll"
    background: str = "subway_surfers"
    secondary_background: str = "minecraft_parkour"
    subtitle_style: str = "classic"
    fps: int = 30


class SettingsRequest(BaseModel):
    reddit_client_id: str = ""
    reddit_client_secret: str = ""
    mistral_api_key: str = ""


# App
app = FastAPI(title="Slop Factory", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Config Endpoints ───────────────────────────────────────────

@app.get("/api/config")
def get_config():
    return {
        "has_reddit": bool(settings.reddit_client_id),
        "has_mistral": bool(settings.mistral_api_key),
        "max_concurrent_jobs": settings.max_concurrent_jobs,
        "default_subreddits": settings.default_subreddits,
        "output_dir": settings.output_dir,
    }


@app.post("/api/config/settings")
def update_settings(req: SettingsRequest):
    updates = {}
    if req.reddit_client_id:
        settings.reddit_client_id = req.reddit_client_id
        updates["reddit_client_id"] = req.reddit_client_id
    if req.reddit_client_secret:
        settings.reddit_client_secret = req.reddit_client_secret
        updates["reddit_client_secret"] = req.reddit_client_secret
    if req.mistral_api_key:
        settings.mistral_api_key = req.mistral_api_key
        updates["mistral_api_key"] = req.mistral_api_key
    if updates:
        from config import _save_env
        _save_env(updates)
    return {"ok": True}


@app.get("/api/voices")
def list_voices():
    return {"voices": AVAILABLE_VOICES}


# ─── Reddit Endpoints ───────────────────────────────────────────

@app.post("/api/reddit/fetch")
def fetch_posts(req: FetchPostsRequest):
    try:
        posts = reddit.fetch_posts(
            subreddits=req.subreddits or None,
            sort=req.sort,
            time_filter=req.time_filter,
            limit=req.limit,
        )
        return {"posts": posts, "count": len(posts)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── Asset Endpoints ────────────────────────────────────────────

@app.get("/api/assets")
def list_assets():
    return {"categories": get_categories(), "assets": get_assets()}


@app.get("/api/assets/categories")
def categories():
    return {"categories": get_categories()}


@app.post("/api/assets/{asset_id}/download")
def download_asset(asset_id: str):
    """Download a background video asset for offline use."""
    import threading
    from asset_manager import download_asset as _download

    def _worker():
        try:
            _download(asset_id)
        except Exception as e:
            print(f"Asset download failed: {e}")

    threading.Thread(target=_worker, daemon=True).start()
    return {"asset_id": asset_id}


# ─── Generation Endpoints ───────────────────────────────────────

@app.post("/api/generate")
async def generate_video(req: GenerateRequest):
    job_id = str(uuid.uuid4())

    with jobs_lock:
        jobs[job_id] = {
            "id": job_id,
            "status": "queued",
            "progress": 0,
            "stage": "initializing",
            "request": req.model_dump(),
            "error": None,
            "output_path": None,
            "created_at": time.time(),
        }

    # Submit to thread pool for parallel processing
    try:
        executor.submit(_process_video_job, job_id, req)
    except Exception as e:
        with jobs_lock:
            jobs[job_id]["status"] = "failed"
            jobs[job_id]["error"] = str(e)
        _save_jobs()
        return {"job_id": job_id, "status": "failed"}

    _save_jobs()

    return {"job_id": job_id, "status": "queued"}


def _persist_job(job_id: str) -> None:
    """Save a single job to disk."""
    _save_jobs()


def _process_video_job(job_id: str, req: GenerateRequest):
    """Core video processing pipeline, runs in a worker thread."""

    try:
        with jobs_lock:
            jobs[job_id]["status"] = "processing"

        # Step 1: Prepare post text
        with jobs_lock:
            jobs[job_id]["stage"] = "fetching reddit post"
            jobs[job_id]["progress"] = 5

        post_text = req.post_text or f"{req.post_title}\n{req.post_subreddit}"

        with jobs_lock:
            jobs[job_id]["stage"] = "generating voice"
            jobs[job_id]["progress"] = 20
        audio_path = generate_tts_audio(post_text, req.voice)

        with jobs_lock:
            jobs[job_id]["stage"] = "voice generated"
            jobs[job_id]["progress"] = 40

        # Step 3: Prepare backgrounds
        with jobs_lock:
            jobs[job_id]["stage"] = "preparing backgrounds"
            jobs[job_id]["progress"] = 50

        backgrounds = set()
        backgrounds.add(req.background)
        if req.secondary_background and req.secondary_background != req.background:
            backgrounds.add(req.secondary_background)

        bg_paths = []
        for bg in backgrounds:
            asset = get_random_asset(bg)
            if asset and asset.get("is_downloaded"):
                bg_paths.append(asset["local_path"])

        # Step 4: Generate subtitles (SRT file with audio-driven timing)
        with jobs_lock:
            jobs[job_id]["stage"] = "generating subtitles"
            jobs[job_id]["progress"] = 60

        srt_path = _create_subtitle_placeholder(post_text, audio_path, job_id)

        with jobs_lock:
            jobs[job_id]["stage"] = "subtitles ready"
            jobs[job_id]["progress"] = 70

        # Step 5: Assemble video
        with jobs_lock:
            jobs[job_id]["stage"] = "assembling video"
            jobs[job_id]["progress"] = 80

        output_path = Path(settings.output_dir) / f"{job_id}.mp4"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        subtitle_style = _get_subtitle_style(req.subtitle_style)

        # Assemble video
        try:
            assemble_video(
                post_text=post_text,
                audio_path=audio_path,
                background_video_paths=bg_paths,
                output_path=output_path,
                subtitle_style=subtitle_style,
                fps=req.fps,
                post_title=req.post_title,
                post_subreddit=req.post_subreddit,
            )
        except (ImportError, RuntimeError, ValueError) as e:
            raise RuntimeError(f"Video assembly failed: {e}")

        with jobs_lock:
            jobs[job_id]["status"] = "completed"
            jobs[job_id]["progress"] = 100
            jobs[job_id]["stage"] = "done"
            jobs[job_id]["output_path"] = str(output_path)
            _persist_job(job_id)

    except Exception as e:
        with jobs_lock:
            jobs[job_id]["status"] = "failed"
            jobs[job_id]["error"] = str(e)
            jobs[job_id]["stage"] = f"error: {e}"
            _persist_job(job_id)


@app.get("/api/jobs")
def list_jobs():
    with jobs_lock:
        return {"jobs": list(jobs.values())}


@app.get("/api/jobs/{job_id}")
def get_job(job_id: str):
    with jobs_lock:
        job = jobs.get(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        return job


@app.get("/api/jobs/{job_id}/download")
def download_job(job_id: str):
    """Serve generated video files."""
    from fastapi.responses import FileResponse

    if not _UUID_RE.match(job_id):
        raise HTTPException(status_code=400, detail="Invalid job ID format")

    with jobs_lock:
        job = jobs.get(job_id)

    if not job or job.get("status") != "completed":
        raise HTTPException(status_code=404, detail="Job not completed")

    output_path = job.get("output_path")
    if not output_path or not os.path.exists(output_path):
        raise HTTPException(status_code=404, detail="Output file not found")

    return FileResponse(output_path, filename=f"slop_factory_{job_id}.mp4")


@app.delete("/api/jobs/{job_id}")
def delete_job(job_id: str):
    """Remove a job from history."""
    if not _UUID_RE.match(job_id):
        raise HTTPException(status_code=400, detail="Invalid job ID format")
    with jobs_lock:
        if jobs.pop(job_id, None):
            _save_jobs()
            return {"ok": True}
    raise HTTPException(status_code=404, detail="Job not found")


# ─── Utility ────────────────────────────────────────────────────


def _create_subtitle_placeholder(post_text: str, audio_path: Path, job_id: str) -> Path:
    """Generate SRT with sentence-based cues spaced across the actual audio
    duration. The assembler renders word-by-word subtitles inside the video
    separately; this SRT is for accessibility / reference."""
    srt_path = Path(settings.output_dir) / "subs" / f"{job_id}.srt"
    srt_path.parent.mkdir(parents=True, exist_ok=True)

    sentences = [s.strip() for s in post_text.split(".") if s.strip()]
    sentences = sentences or [post_text]

    try:
        from video_assembler import get_media_duration
        audio_dur = get_media_duration(Path(audio_path))
    except Exception:
        audio_dur = len(post_text.split()) / 2.5

    cues = []
    total = len(sentences)
    for i, sentence in enumerate(sentences):
        cues.append(SubtitleCue(
            start=(i / total) * audio_dur,
            end=((i + 1) / total) * audio_dur,
            text=sentence,
        ))

    generate_srt(cues, srt_path)
    return srt_path


def _get_subtitle_style(style: str) -> dict:
    styles = {
        "classic": {
            "bg_color": "#000000cc",
            "text_color": "#FFFFFF",
            "highlight_color": "#FFD700",
            "font_size": 48,
            "position": "bottom",
        },
        "modern": {
            "bg_color": "#1a1a2ecc",
            "text_color": "#FFFFFF",
            "highlight_color": "#00FF00",
            "font_size": 52,
            "position": "bottom",
        },
        "minimal": {
            "bg_color": "#00000099",
            "text_color": "#FFFFFF",
            "highlight_color": "#FF6B6B",
            "font_size": 44,
            "position": "center",
        },
        "youtube": {
            "bg_color": "#000000dd",
            "text_color": "#FFFFFF",
            "highlight_color": "#FFD700",
            "font_size": 56,
            "position": "bottom",
        },
    }
    return styles.get(style, styles["classic"])


# Serve static files for the UI
STATIC_DIR = Path(__file__).parent.parent / "frontend" / "dist"
if STATIC_DIR.exists():
    app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
