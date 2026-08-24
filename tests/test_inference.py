from datetime import datetime, timezone

from wifi_sense.inference import PresenceDetector
from wifi_sense.models import Observation


def observation(rssi):
    return Observation(datetime.now(timezone.utc), "test", "network", rssi, backend="fixture")


def test_detector_calibrates_then_reports_activity():
    detector = PresenceDetector(baseline_size=2, activity_threshold=4)
    assert detector.update([observation(-60)]).state == "unknown"
    assert detector.update([observation(-60)]).state == "unknown"
    reading = detector.update([observation(-48)])
    assert reading.state == "activity"
    assert reading.confidence > 0