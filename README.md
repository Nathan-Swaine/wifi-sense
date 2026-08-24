# WiFi Sense

Local Windows WiFi observation and RSSI-based motion/presence sensing.

## Status

The first vertical slice records anonymized BSSID observations from the Windows `netsh` WiFi API, stores them as local JSONL, exposes a FastAPI dashboard, and provides a replayable presence detector. CSI capture is intentionally not assumed: support depends on the exact WiFi module, driver, and firmware.

## Setup

```powershell
cd .\wifi-sense
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

Run tests:

```powershell
python -m pytest
```

Record one scan and start the local dashboard:

```powershell
wifi-sense scan
wifi-sense serve
```

Open `http://127.0.0.1:8000`. Live data is written to `data/observations.jsonl`, which is ignored by Git.

The dashboard UI lives in `frontend/src/main.jsx` and is built with Vite:

```powershell
cd .\frontend
npm install
npm run build
```

For frontend-only development, run the FastAPI service on port 8000 and start Vite in another terminal:

```powershell
cd .\frontend
npm run dev
```

Vite serves the React UI at `http://127.0.0.1:5173` and proxies `/api` requests to the FastAPI service.

The dashboard's **Start collector** button runs continuous scans at the default 10-second interval. The service reports adapter errors in the page and keeps the last known state available. Use the **Stop collector** button before closing the dashboard.

For a quick parser/inference check without WiFi hardware:

```powershell
python -m pytest tests\test_capture.py tests\test_inference.py
```

The API test requires the FastAPI development dependencies in the selected Python environment. WSL and Windows Python installations are separate environments, so install the project with `python -m pip install -e ".[dev]"` in the environment used to run the tests.

## Limitations

RSSI from periodic Windows scans is a coarse activity signal, not guaranteed occupancy detection. The prototype does not capture packet payloads, identify people, or upload data. CSI support requires a separate validated capture backend and may require Linux, special firmware, or external hardware.