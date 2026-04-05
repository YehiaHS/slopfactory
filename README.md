# Slop Factory

Turn Reddit posts into vertical (9:16) videos with TTS narration, animated subtitles, and gameplay backgrounds.

## Features

- **Reddit Browser** — Fetch top posts from any subreddit, sorted by hot/top/new/rising
- **TTS Narration** — Powered by Mistral AI with multiple voice options
- **Animated Subtitles** — Word-by-word highlight styles (Classic, Modern, Minimal, YouTube)
- **Background Footage** — Curated library of free-to-use gameplay videos (Subway Surfers, Minecraft Parkour, CS2, Satisfying)
- **Job Queue** — Monitor generation progress, download completed videos
- **Live Preview** — 9:16 preview panel showing the final video layout

## Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **ffmpeg** (must be on your PATH)
- **Reddit API credentials** (create at https://www.reddit.com/prefs/apps)
- **Mistral AI API key** (get at https://console.mistral.ai/)

## Quick Start

### 1. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Frontend

```bash
cd frontend
npm install
```

### 3. Configure

Copy `.env.example` to `.env` and fill in your API keys:

```env
SLOP_REDDIT_CLIENT_ID=your_reddit_client_id
SLOP_REDDIT_CLIENT_SECRET=your_reddit_client_secret
SLOP_MISTRAL_API_KEY=your_mistral_api_key
```

### 4. Run

```bash
# Terminal 1 — Backend
cd backend
python run.py

# Terminal 2 — Frontend (dev mode with hot reload)
cd frontend
npm run dev
```

The backend starts at `http://localhost:8000` and the frontend dev server at `http://localhost:3000`.

### Production Build

```bash
cd frontend
npm run build
cd ../backend
python run.py  # Serves the built frontend from dist/
```

## Project Structure

```
slopfactory/
├── backend/
│   ├── api.py              # FastAPI server and job management
│   ├── video_assembler.py  # Core video composition engine
│   ├── tts_service.py      # Mistral AI TTS integration
│   ├── reddit_fetcher.py   # Reddit API client
│   ├── asset_manager.py    # Background video catalog and downloads
│   ├── subtitle_renderer.py # SRT subtitle generation
│   ├── config.py           # Settings and .env management
│   └── run.py              # Launcher
├── frontend/
│   └── src/
│       ├── App.tsx         # Main app shell
│       ├── store.ts        # Zustand state management
│       └── components/     # UI components
└── .env.example
```

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `SLOP_REDDIT_CLIENT_ID` | Reddit API client ID | — |
| `SLOP_REDDIT_CLIENT_SECRET` | Reddit API client secret | — |
| `SLOP_MISTRAL_API_KEY` | Mistral AI API key | — |
| `SLOP_OUTPUT_DIR` | Directory for generated videos | `./outputs` |
| `SLOP_MAX_CONCURRENT_JOBS` | Parallel video generation | `4` |
| `SLOP_DEFAULT_SUBREDDITS` | Comma-separated subreddit list | `AskReddit,stories,confession,nosleep,TrueOffMyChest` |
| `SLOP_PORT` | Backend server port | `8000` |

## License

MIT
