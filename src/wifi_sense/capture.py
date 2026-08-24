import hashlib
import re
import subprocess
from datetime import datetime
from typing import List, Optional, Protocol

from .models import Observation, utc_now


class CaptureBackend(Protocol):
    name: str

    def scan(self) -> List[Observation]: ...


def anonymize_identifier(identifier: str, salt: str = "local-wifi-sense") -> str:
    return hashlib.sha256((salt + identifier.lower()).encode("utf-8")).hexdigest()[:16]


class NetshBackend:
    name = "windows-netsh"

    def __init__(self, interface: Optional[str] = None, salt: str = "local-wifi-sense"):
        self.interface = interface or ""
        self.salt = salt

    def scan(self) -> List[Observation]:
        command = ["netsh", "wlan", "show", "networks", "mode=bssid"]
        completed = subprocess.run(command, capture_output=True, text=True, check=True)
        return parse_netsh_scan(completed.stdout, self.interface, self.salt, utc_now())


def parse_netsh_scan(output: str, interface: str, salt: str, timestamp: datetime) -> List[Observation]:
    observations: List[Observation] = []
    bssid: Optional[str] = None
    signal: Optional[int] = None
    channel: Optional[int] = None
    bssid_pattern = re.compile(r"^\s*BSSID\s+\d+\s*:\s*(.+)$", re.IGNORECASE)
    signal_pattern = re.compile(r"^\s*Signal\s*:\s*(\d+)%", re.IGNORECASE)
    channel_pattern = re.compile(r"^\s*Channel\s*:\s*(\d+)", re.IGNORECASE)

    def flush() -> None:
        nonlocal bssid, signal, channel
        if bssid is not None:
            rssi = None if signal is None else int(signal / 2) - 100
            observations.append(Observation(timestamp, interface, anonymize_identifier(bssid, salt), rssi, channel, None, "windows-netsh"))
        bssid, signal, channel = None, None, None

    for line in output.splitlines():
        match = bssid_pattern.match(line)
        if match:
            flush()
            bssid = match.group(1).strip()
            continue
        match = signal_pattern.match(line)
        if match:
            signal = int(match.group(1))
            continue
        match = channel_pattern.match(line)
        if match:
            channel = int(match.group(1))
    flush()
    return observations