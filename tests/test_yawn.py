import math

import numpy as np
import pytest

from drowsyalert.features.extra import ExtraTracker
from drowsyalert.features.geometry import mouth_aspect_ratio
from drowsyalert.types import FaceObservation
from drowsyalert.utils.config import Config


def mouth_observation(mar: float) -> FaceObservation:
    points = np.zeros((468, 2), dtype=float)
    points[61], points[291] = (0, 0), (10, 0)
    height = mar * 10
    points[82], points[87] = (2, -height / 2), (2, height / 2)
    points[312], points[317] = (8, -height / 2), (8, height / 2)
    return FaceObservation(True, landmarks=points)


def test_mouth_aspect_ratio_validates_shape_values_and_width():
    assert mouth_aspect_ratio(mouth_observation(0.6).landmarks) == pytest.approx(0.6)
    with pytest.raises(ValueError, match="landmarks"):
        mouth_aspect_ratio(np.zeros((100, 2)))
    invalid = mouth_observation(0.6).landmarks.copy()
    invalid[82, 0] = math.nan
    with pytest.raises(ValueError, match="finite"):
        mouth_aspect_ratio(invalid)
    degenerate = mouth_observation(0.6).landmarks.copy()
    degenerate[291] = degenerate[61]
    with pytest.raises(ValueError, match="width"):
        mouth_aspect_ratio(degenerate)


@pytest.mark.parametrize("mar", [0.59, 0.6, 0.61])
def test_yawn_mar_threshold_is_inclusive_but_duration_is_required(mar):
    tracker = ExtraTracker(
        Config(yawn_threshold=0.6, yawn_seconds=0.5, max_gap_seconds=1.0),
        "perclos-yawn",
    )
    first = tracker.update(mouth_observation(mar), 0.0, 640, 480)
    later = tracker.update(mouth_observation(mar), 0.5, 640, 480)

    assert first.yawn_valid and first.yawn_active_seconds == 0
    assert later.yawns == (1 if mar >= 0.6 else 0)
    assert later.yawn_event is (mar >= 0.6)


def test_continuous_mouth_opening_counts_once_and_closure_allows_next_event():
    tracker = ExtraTracker(Config(yawn_seconds=0.2), "perclos-yawn")
    results = [
        tracker.update(mouth_observation(0.8), timestamp, 640, 480)
        for timestamp in (0.0, 0.2, 0.3, 0.4)
    ]
    assert [result.yawn_event for result in results] == [False, True, False, False]
    assert results[-1].yawns == 1

    closed = tracker.update(mouth_observation(0.2), 0.5, 640, 480)
    restarted = tracker.update(mouth_observation(0.8), 0.6, 640, 480)
    second = tracker.update(mouth_observation(0.8), 0.8, 640, 480)
    assert closed.yawn_active_seconds == 0
    assert restarted.yawns == 1 and not restarted.yawn_event
    assert second.yawns == 2 and second.yawn_event


def test_gap_and_invalid_observation_reset_duration_without_inventing_event():
    config = Config(yawn_seconds=0.3, max_gap_seconds=0.15)
    tracker = ExtraTracker(config, "perclos-yawn")
    tracker.update(mouth_observation(0.8), 0.0, 640, 480)
    after_gap = tracker.update(mouth_observation(0.8), 0.2, 640, 480)
    unavailable = tracker.update(FaceObservation(False, "No face"), 0.3, 640, 480)
    resumed = tracker.update(mouth_observation(0.8), 0.4, 640, 480)

    assert after_gap.yawn_active_seconds == 0 and after_gap.yawns == 0
    assert not unavailable.yawn_valid and unavailable.yawn_reason == "No face"
    assert not unavailable.yawn_event and unavailable.yawns == 0
    assert resumed.yawn_active_seconds == 0 and resumed.yawns == 0


def test_invalid_mouth_geometry_is_unknown_and_rolling_events_expire():
    config = Config(yawn_seconds=0.1, window_seconds=0.5, max_gap_seconds=1.0)
    tracker = ExtraTracker(config, "perclos-yawn")
    tracker.update(mouth_observation(0.8), 0.0, 640, 480)
    event = tracker.update(mouth_observation(0.8), 0.1, 640, 480)
    invalid = mouth_observation(0.8)
    invalid.landmarks[61] = invalid.landmarks[291]
    unknown = tracker.update(invalid, 0.2, 640, 480)
    expired = tracker.update(mouth_observation(0.2), 0.61, 640, 480)

    assert event.yawns == 1
    assert not unknown.yawn_valid and "width" in unknown.yawn_reason.lower()
    assert expired.yawns == 0


def test_yawn_tracker_rejects_invalid_or_non_increasing_timestamps():
    tracker = ExtraTracker(Config(), "perclos-yawn")
    tracker.update(mouth_observation(0.8), 1.0, 640, 480)
    for timestamp in (1.0, 0.9, math.nan):
        with pytest.raises(ValueError, match="timestamp"):
            tracker.update(mouth_observation(0.8), timestamp, 640, 480)


def test_method_a_does_not_calculate_mouth_evidence():
    result = ExtraTracker(Config(), "perclos").update(
        FaceObservation(False, "No face"), 0.0, 640, 480
    )
    assert not result.yawn_valid
    assert result.yawn_reason == "Yawn cue inactive for method"
