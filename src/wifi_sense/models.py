from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Optional


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class Observation:
    timestamp: datetime
    interface: str
    identifier: str
    rssi_dbm: Optional[int]
    channel: Optional[int] = None
    frequency_mhz: Optional[int] = None
    backend: str = "unknown"

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result["timestamp"] = self.timestamp.isoformat()
        return result


@dataclass(frozen=True)
class PresenceReading:
    timestamp: datetime
    state: str
    confidence: float
    activity_score: Optional[float]
    explanation: str

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result["timestamp"] = self.timestamp.isoformat()
        return result