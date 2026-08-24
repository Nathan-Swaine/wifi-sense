import threading
import time
from typing import Any, Dict, Optional

from .capture import CaptureBackend
from .inference import PresenceDetector
from .storage import JsonlStore


class Collector:
    def __init__(self, backend: CaptureBackend, store: JsonlStore, interval_seconds: float = 10.0):
        self.backend = backend
        self.store = store
        self.interval_seconds = interval_seconds
        self.detector = PresenceDetector()
        self._thread: Optional[threading.Thread] = None
        self._stop = threading.Event()
        self._lock = threading.Lock()
        self._last_error: Optional[str] = None
        self._last_scan_at: Optional[str] = None
        self._last_presence: Optional[Dict[str, Any]] = None

    @property
    def running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def start(self) -> bool:
        if self.running:
            return False
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, name="wifi-sense-collector", daemon=True)
        self._thread.start()
        return True

    def stop(self) -> bool:
        if not self.running:
            return False
        self._stop.set()
        self._thread.join(timeout=max(1.0, self.interval_seconds + 1))
        return True

    def status(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "collector": "running" if self.running else "stopped",
                "backend": self.backend.name,
                "interval_seconds": self.interval_seconds,
                "last_scan_at": self._last_scan_at,
                "latest_presence": self._last_presence,
                "last_error": self._last_error,
            }

    def _run(self) -> None:
        while not self._stop.is_set():
            try:
                observations = self.backend.scan()
                presence = self.detector.update(observations)
                self.store.append_observations(observations)
                self.store.append_presence(presence)
                with self._lock:
                    self._last_scan_at = presence.timestamp.isoformat()
                    self._last_presence = presence.to_dict()
                    self._last_error = None
            except Exception as error:
                with self._lock:
                    self._last_error = str(error)
            self._stop.wait(self.interval_seconds)