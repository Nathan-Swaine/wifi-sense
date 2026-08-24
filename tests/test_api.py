from fastapi.testclient import TestClient

from wifi_sense.api import create_app


def test_health_and_status(tmp_path):
    client = TestClient(create_app(tmp_path / "observations.jsonl"))
    assert client.get("/health").json() == {"status": "ok"}
    status = client.get("/api/status").json()
    assert status["collector"] == "stopped"
    assert status["latest_presence"] is None
    assert client.get("/").status_code == 200