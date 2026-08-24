import json
from pathlib import Path
from typing import Any, Dict, Iterable, List

from .models import Observation, PresenceReading


class JsonlStore:
    def __init__(self, path: Path):
        self.path = path

    def append(self, record: Dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, separators=(",", ":")) + "\n")

    def append_observations(self, observations: Iterable[Observation]) -> None:
        for observation in observations:
            self.append({"type": "observation", **observation.to_dict()})

    def append_presence(self, reading: PresenceReading) -> None:
        self.append({"type": "presence", **reading.to_dict()})

    def recent(self, limit: int = 100) -> List[Dict[str, Any]]:
        if not self.path.exists():
            return []
        lines = self.path.read_text(encoding="utf-8").splitlines()
        records = [json.loads(line) for line in lines[-limit:] if line.strip()]
        return records