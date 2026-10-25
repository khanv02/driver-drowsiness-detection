"""Time-weighted rolling measurements. Missing observations are never treated as open."""

import math
from collections import deque

from drowsyalert.types import EyeState, TemporalFeatures


class TemporalTracker:
    def __init__(
        self,
        window: float = 60,
        min_valid: float = 30,
        min_coverage: float = 0.8,
        max_gap: float = 0.25,
    ):
        if not (window > 0 and 0 < min_valid <= window and 0 < min_coverage <= 1 and max_gap > 0):
            raise ValueError("Invalid temporal configuration")
        self.window, self.min_valid = window, min_valid
        self.min_coverage, self.max_gap = min_coverage, max_gap
        self.intervals = deque()
        self.last_time = None
        self.first_time = None
        self.last_state = EyeState.UNKNOWN
        self.closed = 0.0

    def update(self, timestamp: float, state: EyeState) -> TemporalFeatures:
        if not math.isfinite(timestamp):
            raise ValueError("Timestamp must be finite")
        if self.last_time is not None and timestamp <= self.last_time:
            raise ValueError("Timestamps must strictly increase")
        if self.first_time is None:
            self.first_time = timestamp
        dt = 0 if self.last_time is None else timestamp - self.last_time
        continuous = (
            self.last_time is not None
            and dt <= self.max_gap
            and state != EyeState.UNKNOWN
            and self.last_state != EyeState.UNKNOWN
        )
        if continuous:
            # The previous observation describes [previous timestamp, current timestamp).
            self.intervals.append((self.last_time, timestamp, self.last_state))
        if state == EyeState.CLOSED:
            self.closed = (
                self.closed + dt if (continuous and self.last_state == EyeState.CLOSED) else 0.0
            )
        else:
            self.closed = 0.0
        cutoff = timestamp - self.window
        while self.intervals and self.intervals[0][1] <= cutoff:
            self.intervals.popleft()
        valid = closed = 0.0
        for start, end, observed in self.intervals:
            duration = end - max(start, cutoff)
            valid += duration
            if observed == EyeState.CLOSED:
                closed += duration
        elapsed = min(self.window, timestamp - self.first_time)
        coverage = valid / elapsed if elapsed > 0 else 0.0
        ready = valid >= self.min_valid - 1e-9 and coverage >= self.min_coverage
        self.last_time, self.last_state = timestamp, state
        return TemporalFeatures(
            self.closed, closed / valid if valid else None, coverage, valid, ready, continuous
        )
