import math

import cv2
import numpy as np
import pytest

import drowsyalert.features.extra as extra_module
from drowsyalert.features.extra import POSE_INDICES, POSE_POINTS, ExtraTracker, estimate_pose
from drowsyalert.types import FaceObservation
from drowsyalert.utils.config import Config


def valid_observation() -> FaceObservation:
    return FaceObservation(True, landmarks=np.zeros((468, 2), dtype=float))


def projected_landmarks(pitch_radians: float) -> np.ndarray:
    camera = np.array([[640, 0, 320], [0, 640, 240], [0, 0, 1]], dtype=float)
    projected, _ = cv2.projectPoints(
        POSE_POINTS,
        np.array([pitch_radians, 0, 0], dtype=float),
        np.array([0, 0, 1200], dtype=float),
        camera,
        np.zeros(4),
    )
    landmarks = np.zeros((468, 2), dtype=float)
    landmarks[list(POSE_INDICES)] = projected.reshape(-1, 2)
    return landmarks


def test_pose_estimation_validates_inputs_and_positive_pitch_sign():
    pitch, yaw, roll = estimate_pose(projected_landmarks(0.3), 640, 480)
    assert pitch == pytest.approx(np.degrees(0.3), abs=0.1)
    assert abs(yaw) < 0.1 and abs(roll) < 0.1
    with pytest.raises(ValueError, match="landmarks"):
        estimate_pose(np.zeros((100, 2)), 640, 480)
    invalid = projected_landmarks(0.0)
    invalid[POSE_INDICES[0], 0] = math.nan
    with pytest.raises(ValueError, match="finite"):
        estimate_pose(invalid, 640, 480)
    with pytest.raises(ValueError, match="dimensions"):
        estimate_pose(projected_landmarks(0.0), 0, 480)


def test_fixed_reference_threshold_and_sustained_duration_are_inclusive(monkeypatch):
    monkeypatch.setattr(extra_module, "estimate_pose", lambda *_: (30.0, 2.0, -1.0))
    config = Config(
        head_pose_reference_degrees=10.0,
        head_down_degrees=20.0,
        head_down_seconds=0.2,
        max_gap_seconds=0.5,
    )
    tracker = ExtraTracker(config, "perclos-head-pose")

    first = tracker.update(valid_observation(), 0.0, 640, 480)
    at_duration = tracker.update(valid_observation(), 0.2, 640, 480)

    assert first.head_pose_valid and first.angles == pytest.approx((20.0, 2.0, -1.0))
    assert first.pose_reference_pitch == 10.0
    assert first.head_down_seconds == 0 and not first.head_down
    assert at_duration.head_down_seconds == pytest.approx(0.2)
    assert at_duration.head_down


def test_below_threshold_resets_head_down_continuity(monkeypatch):
    values = iter(((21.0, 0.0, 0.0), (19.9, 0.0, 0.0), (21.0, 0.0, 0.0)))
    monkeypatch.setattr(extra_module, "estimate_pose", lambda *_: next(values))
    config = Config(
        head_pose_reference_degrees=0.0,
        head_down_degrees=20.0,
        head_down_seconds=0.2,
    )
    tracker = ExtraTracker(config, "perclos-head-pose")

    tracker.update(valid_observation(), 0.0, 640, 480)
    below = tracker.update(valid_observation(), 0.1, 640, 480)
    restarted = tracker.update(valid_observation(), 0.2, 640, 480)

    assert below.head_down_seconds == 0 and not below.head_down
    assert restarted.head_down_seconds == 0 and not restarted.head_down


def test_automatic_reference_is_recorded_from_first_valid_sample(monkeypatch):
    values = iter(((12.0, 1.0, 2.0), (33.0, 1.0, 2.0)))
    monkeypatch.setattr(extra_module, "estimate_pose", lambda *_: next(values))
    tracker = ExtraTracker(Config(head_pose_reference_degrees=None), "perclos-head-pose")

    baseline = tracker.update(valid_observation(), 0.0, 640, 480)
    changed = tracker.update(valid_observation(), 0.1, 640, 480)

    assert baseline.pose_reference_pitch == 12.0
    assert baseline.angles[0] == pytest.approx(0.0)
    assert "first valid" in baseline.head_pose_reason.lower()
    assert changed.pose_reference_pitch == 12.0
    assert changed.angles[0] == pytest.approx(21.0)


def test_invalid_pose_and_gap_reset_duration_but_preserve_reference(monkeypatch):
    monkeypatch.setattr(extra_module, "estimate_pose", lambda *_: (25.0, 0.0, 0.0))
    config = Config(
        head_pose_reference_degrees=0.0,
        head_down_seconds=0.2,
        max_gap_seconds=0.15,
    )
    tracker = ExtraTracker(config, "perclos-head-pose")
    tracker.update(valid_observation(), 0.0, 640, 480)
    after_gap = tracker.update(valid_observation(), 0.2, 640, 480)
    unavailable = tracker.update(FaceObservation(False, "No face"), 0.3, 640, 480)
    resumed = tracker.update(valid_observation(), 0.4, 640, 480)

    assert after_gap.head_down_seconds == 0
    assert not unavailable.head_pose_valid and unavailable.head_pose_reason == "No face"
    assert unavailable.pose_reference_pitch == 0.0
    assert resumed.head_down_seconds == 0


def test_pose_solver_failure_is_unknown(monkeypatch):
    monkeypatch.setattr(extra_module, "estimate_pose", lambda *_: None)
    result = ExtraTracker(Config(), "perclos-head-pose").update(
        valid_observation(), 0.0, 640, 480
    )
    assert not result.head_pose_valid
    assert result.head_pose_reason == "Head pose unavailable"


def test_method_a_does_not_calculate_pose_evidence():
    result = ExtraTracker(Config(), "perclos").update(valid_observation(), 0.0, 640, 480)
    assert not result.head_pose_valid
    assert result.head_pose_reason == "Head-pose cue inactive for method"
