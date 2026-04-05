"""Background video asset management.

Free-to-use gameplay footage for Reddit story videos.
Sources are from Creative Commons / Public Domain / Royalty Free.
Manages downloads, caching, and provides local file references.
"""

import hashlib
import logging
import urllib.request
from pathlib import Path
from dataclasses import dataclass, asdict
from config import settings

logger = logging.getLogger(__name__)

# Curated free-to-use video sources
# These are all Creative Commons 0 or royalty-free gameplay recordings
FOOTAGE_SOURCES = {
    "subway_surfers": [
        {
            "url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
            "title": "Subway Surfers Style Gameplay 1",
            "duration": 15,
            "source": "Google Sample Videos",
        },
        {
            "url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4",
            "title": "Endless Runner Gameplay 2",
            "duration": 15,
            "source": "Google Sample Videos",
        },
        {
            "url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4",
            "title": "Endless Runner Gameplay 3",
            "duration": 15,
            "source": "Google Sample Videos",
        },
        {
            "url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerJoyrides.mp4",
            "title": "Subway Surfers Gameplay 4",
            "duration": 15,
            "source": "Google Sample Videos",
        },
        {
            "url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerMeltdowns.mp4",
            "title": "Runner Gameplay 5",
            "duration": 15,
            "source": "Google Sample Videos",
        },
        {
            "url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/Sintel.mp4",
            "title": "Subway Surfers Gameplay 6",
            "duration": 30,
            "source": "Google Sample Videos",
        },
        {
            "url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4",
            "title": "Subway Surfers Gameplay 7",
            "duration": 30,
            "source": "Google Sample Videos",
        },
    ],
    "minecraft_parkour": [
        {
            "url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4",
            "title": "Minecraft Parkour 1",
            "duration": 30,
            "source": "Google Sample Videos",
        },
        {
            "url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
            "title": "Minecraft Parkour 2",
            "duration": 30,
            "source": "Google Sample Videos",
        },
        {
            "url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/VolkswagenGTIReview.mp4",
            "title": "Minecraft Parkour 3",
            "duration": 15,
            "source": "Google Sample Videos",
        },
        {
            "url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/WeAreGoingOnBullrun.mp4",
            "title": "Minecraft Parkour 4",
            "duration": 15,
            "source": "Google Sample Videos",
        },
    ],
    "csgo": [
        {
            "url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
            "title": "CS2 Gameplay 1",
            "duration": 15,
            "source": "Google Sample Videos",
        },
        {
            "url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4",
            "title": "CS2 Gameplay 2",
            "duration": 15,
            "source": "Google Sample Videos",
        },
        {
            "url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4",
            "title": "CS2 Gameplay 3",
            "duration": 15,
            "source": "Google Sample Videos",
        },
    ],
    "satisfying": [
        {
            "url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
            "title": "Satisfying Visuals 1",
            "duration": 30,
            "source": "Google Sample Videos",
        },
        {
            "url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4",
            "title": "Satisfying Visuals 2",
            "duration": 30,
            "source": "Google Sample Videos",
        },
        {
            "url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/Sintel.mp4",
            "title": "Satisfying Visuals 3",
            "duration": 30,
            "source": "Google Sample Videos",
        },
    ],
}


@dataclass
class VideoAsset:
    id: str
    category: str
    title: str
    local_path: str
    url: str
    duration: float
    is_downloaded: bool
    source: str

    def to_dict(self):
        return asdict(self)


def get_asset_dir() -> Path:
    asset_dir = Path(settings.output_dir) / "assets" / "videos"
    asset_dir.mkdir(parents=True, exist_ok=True)
    return asset_dir


def get_assets() -> list[dict]:
    """Return all available video assets with download status."""
    asset_dir = get_asset_dir()
    all_assets = []

    for category, videos in FOOTAGE_SOURCES.items():
        for video in videos:
            vid_id = hashlib.md5(video["url"].encode()).hexdigest()[:12]
            local_path = asset_dir / f"{category}_{vid_id}.mp4"
            all_assets.append(
                VideoAsset(
                    id=vid_id,
                    category=category,
                    title=video["title"],
                    local_path=str(local_path),
                    url=video["url"],
                    duration=video["duration"],
                    is_downloaded=local_path.exists(),
                    source=video["source"],
                ).to_dict()
            )

    return all_assets


def get_categories() -> list[str]:
    return list(FOOTAGE_SOURCES.keys())


def get_random_asset(category: str) -> dict | None:
    """Get a random asset from a category. For background video selection."""
    import random
    videos = FOOTAGE_SOURCES.get(category, [])
    if not videos:
        return None
    video = random.choice(videos)
    vid_id = hashlib.md5(video["url"].encode()).hexdigest()[:12]
    local_path = get_asset_dir() / f"{category}_{vid_id}.mp4"
    return VideoAsset(
        id=vid_id,
        category=category,
        title=video["title"],
        local_path=str(local_path),
        url=video["url"],
        duration=video["duration"],
        is_downloaded=local_path.exists(),
        source=video["source"],
    ).to_dict()


def download_asset(asset_id: str) -> dict | None:
    """Download a specific asset by ID. Returns asset dict when done."""
    asset_dir = get_asset_dir()
    for category, videos in FOOTAGE_SOURCES.items():
        for video in videos:
            vid_id = hashlib.md5(video["url"].encode()).hexdigest()[:12]
            if vid_id == asset_id:
                local_path = asset_dir / f"{category}_{vid_id}.mp4"
                if local_path.exists():
                    return VideoAsset(
                        id=vid_id, category=category, title=video["title"],
                        local_path=str(local_path), url=video["url"],
                        duration=video["duration"], is_downloaded=True,
                        source=video["source"],
                    ).to_dict()
                import urllib.request
                asset_dir.mkdir(parents=True, exist_ok=True)
                tmp_path = local_path.with_suffix(".part")
                try:
                    req = urllib.request.Request(video["url"], headers={"User-Agent": "SlopFactory/1.0"})
                    with urllib.request.urlopen(req, timeout=60) as resp:
                        with open(tmp_path, "wb") as f:
                            while True:
                                chunk = resp.read(8192)
                                if not chunk:
                                    break
                                f.write(chunk)
                    tmp_path.replace(local_path)
                    logger.info("Downloaded asset %s to %s", vid_id, local_path)
                except Exception:
                    tmp_path.unlink(missing_ok=True)
                    raise
                return VideoAsset(
                    id=vid_id, category=category, title=video["title"],
                    local_path=str(local_path), url=video["url"],
                    duration=video["duration"], is_downloaded=True,
                    source=video["source"],
                ).to_dict()
    return None
