from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from .capture import NetshBackend
from .collector import Collector
from .storage import JsonlStore


PROJECT_ROOT = Path(__file__).resolve().parents[2]
FRONTEND_DIST = PROJECT_ROOT / "frontend" / "dist"


def create_app(data_path: Path = Path("data/observations.jsonl")) -> FastAPI:
    app = FastAPI(title="WiFi Sense", version="0.1.0")
    store = JsonlStore(data_path)
    collector = Collector(NetshBackend(), store)
    if (FRONTEND_DIST / "assets").exists():
        app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")

    @app.get("/health")
    def health() -> Dict[str, str]:
        return {"status": "ok"}

    @app.get("/api/status")
    def status() -> Dict[str, Any]:
        result = collector.status()
        result["records"] = len(store.recent(1000))
        return result

    @app.post("/api/collector/start")
    def start_collector() -> Dict[str, Any]:
        collector.start()
        return collector.status()

    @app.post("/api/collector/stop")
    def stop_collector() -> Dict[str, Any]:
        collector.stop()
        return collector.status()

    @app.get("/api/recent")
    def recent(limit: int = 100) -> Dict[str, Any]:
        return {"records": store.recent(max(1, min(limit, 1000)))}

    @app.get("/", response_class=HTMLResponse)
    def dashboard() -> FileResponse:
        index_path = FRONTEND_DIST / "index.html"
        if index_path.exists():
            return FileResponse(index_path)
        return HTMLResponse("""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>WiFi Sense</title></head><body><main><h1>WiFi Sense</h1><p>Build the frontend with <code>npm run build</code> from the <code>frontend</code> directory.</p></main></body></html>""")

    return app