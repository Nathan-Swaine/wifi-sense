import argparse
from pathlib import Path

from .api import create_app
from .capture import NetshBackend
from .inference import PresenceDetector
from .storage import JsonlStore


def main() -> None:
    parser = argparse.ArgumentParser(description="Local WiFi RSSI sensing")
    parser.add_argument("command", choices=("scan", "serve"))
    parser.add_argument("--data", type=Path, default=Path("data/observations.jsonl"))
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    if args.command == "scan":
        store = JsonlStore(args.data)
        observations = NetshBackend().scan()
        store.append_observations(observations)
        store.append_presence(PresenceDetector().update(observations))
        print("Recorded {} observations".format(len(observations)))
        return
    import uvicorn
    uvicorn.run(create_app(args.data), host=args.host, port=args.port)