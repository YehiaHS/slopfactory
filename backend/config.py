import os
from pathlib import Path
from dotenv import dotenv_values
import logging

logger = logging.getLogger(__name__)

def _load_env() -> dict[str, str]:
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        vals = dotenv_values(env_path)
        for k, v in vals.items():
            if v and k not in os.environ:
                os.environ[k] = v
        return vals
    return {}

_vals = _load_env()

_env_path = Path(__file__).parent.parent / ".env"

_KEY_MAP = {
    "reddit_client_id": "SLOP_REDDIT_CLIENT_ID",
    "reddit_client_secret": "SLOP_REDDIT_CLIENT_SECRET",
    "mistral_api_key": "SLOP_MISTRAL_API_KEY",
}

def _quote_env_value(v: str) -> str:
    """Quote a value for safe .env file writing if it contains special chars."""
    if any(c in v for c in (' ', '#', '=', '"', "'")):
        return f'"{v.replace(chr(34), chr(92) + chr(34))}"'
    return v


def _unquote_env_value(v: str) -> str:
    """Strip surrounding quotes from a .env value."""
    if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
        return v[1:-1].replace('\\"', '"').replace("\\'", "'")
    return v


def _save_env(updates: dict[str, str]) -> None:
    """Persist secrets to .env file, preserving existing entries."""
    existing: dict[str, str] = {}
    if _env_path.exists():
        with open(_env_path, "r") as f:
            for line in f:
                stripped = line.strip()
                if stripped and "=" in stripped and not stripped.startswith("#"):
                    k, v = stripped.split("=", 1)
                    existing[k.strip()] = _unquote_env_value(v.strip())
    # Translate short keys to full env var names before saving
    for short_key, val in updates.items():
        env_key = _KEY_MAP.get(short_key, short_key)
        existing[env_key] = _quote_env_value(val)
    _env_path.parent.mkdir(parents=True, exist_ok=True)
    with open(_env_path, "w") as f:
        for k, v in existing.items():
            f.write(f"{k}={v}\n")
    # Also update in-memory settings and os.environ
    for short_key, v in updates.items():
        env_key = _KEY_MAP.get(short_key)
        if env_key and v:
            os.environ[env_key] = v
        if hasattr(settings, short_key):
            setattr(settings, short_key, v)
    logger.info("Settings saved to %s", _env_path)


class Settings:
    reddit_client_id: str
    reddit_client_secret: str
    reddit_user_agent: str
    mistral_api_key: str
    output_dir: str
    max_concurrent_jobs: int
    default_subreddits: str
    default_post_count: int
    default_sort: str
    default_time: str

    def __init__(self):
        self.reddit_client_id = os.environ.get("SLOP_REDDIT_CLIENT_ID", "")
        self.reddit_client_secret = os.environ.get("SLOP_REDDIT_CLIENT_SECRET", "")
        self.reddit_user_agent = os.environ.get("SLOP_REDDIT_USER_AGENT", "SlopFactory/1.0")
        self.mistral_api_key = os.environ.get("SLOP_MISTRAL_API_KEY", "")
        self.output_dir = os.environ.get("SLOP_OUTPUT_DIR", "./outputs")
        self.max_concurrent_jobs = int(os.environ.get("SLOP_MAX_CONCURRENT_JOBS", "4"))
        self.default_subreddits = os.environ.get("SLOP_DEFAULT_SUBREDDITS", "AskReddit,stories,confession,nosleep,TrueOffMyChest")
        self.default_post_count = 5
        self.default_sort = "top"
        self.default_time = "week"


settings = Settings()
