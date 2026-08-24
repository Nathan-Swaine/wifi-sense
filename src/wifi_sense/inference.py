from collections import deque
from statistics import mean, pstdev
from typing import Deque, Iterable, List, Optional

from .models import Observation, PresenceReading, utc_now


class PresenceDetector:
    """A small, replayable RSSI activity detector.

    It compares the current scan's RSSI values with the recent baseline and
    reports unknown until enough complete scans have been observed.
    """

    def __init__(self, baseline_size: int = 10, activity_threshold: float = 4.0):
        self.baseline_size = baseline_size
        self.activity_threshold = activity_threshold
        self._scan_scores: Deque[float] = deque(maxlen=baseline_size)

    def update(self, observations: Iterable[Observation]) -> PresenceReading:
        values: List[int] = [item.rssi_dbm for item in observations if item.rssi_dbm is not None]
        timestamp = utc_now()
        if not values:
            return PresenceReading(timestamp, "unknown", 0.0, None, "No RSSI values in scan")

        current_mean = mean(values)
        if len(self._scan_scores) < self.baseline_size:
            self._scan_scores.append(current_mean)
            return PresenceReading(timestamp, "unknown", 0.0, 0.0, "Calibrating quiet baseline")

        baseline = mean(self._scan_scores)
        activity_score = abs(current_mean - baseline) + pstdev(values)
        self._scan_scores.append(current_mean)
        if activity_score >= self.activity_threshold:
            confidence = min(1.0, activity_score / (self.activity_threshold * 2))
            return PresenceReading(timestamp, "activity", confidence, activity_score, "RSSI pattern changed")
        return PresenceReading(timestamp, "quiet", 1.0 - activity_score / self.activity_threshold, activity_score, "RSSI is near baseline")