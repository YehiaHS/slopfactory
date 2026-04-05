"""Slop Factory launcher — starts the FastAPI server."""

import os
import sys
import webbrowser
import threading
import time
from pathlib import Path


def launch():
    # Load env vars from .env file (config.py handles this at import time)
    from config import settings

    # Start the API server
    host = "0.0.0.0"
    port = int(os.environ.get("SLOP_PORT", "8000"))

    def open_browser():
        time.sleep(1.5)
        webbrowser.open(f"http://localhost:{port}")

    threading.Thread(target=open_browser, daemon=True).start()

    # Check if frontend dist exists for serving
    dist = Path(__file__).parent.parent / "frontend" / "dist"
    if not dist.exists():
        print("Frontend not built. Run `cd frontend && npm run build` first.")
        print("Starting API-only mode...")

    import uvicorn
    print(f"Slop Factory starting on http://localhost:{port}")
    uvicorn.run("api:app", host=host, port=port, reload=False)


if __name__ == "__main__":
    launch()
