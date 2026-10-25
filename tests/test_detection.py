import numpy as np
import pytest

from drowsyalert.features.geometry import eye_aspect_ratio
from drowsyalert.models.ear import EARBackend
from drowsyalert.types import EyeState, FaceObservation


def test_ear_known_geometry():
    points = np.array([[0, 0], [1, 1], [3, 1], [4, 0], [3, -1], [1, -1]])
    assert eye_aspect_ratio(points) == pytest.approx(0.5)
    with pytest.raises(ValueError):
        eye_aspect_ratio(np.zeros((6, 2)))


def test_wink_is_not_bilateral_closure():
    backend = EARBackend()
    assert backend.predict(FaceObservation(True, ears=(0.1, 0.3))).state == EyeState.OPEN
    assert backend.predict(FaceObservation(True, ears=(0.1, 0.1))).state == EyeState.CLOSED
    assert backend.predict(FaceObservation(False)).state == EyeState.UNKNOWN


def test_head_pose_recovers_projected_pitch():
    import cv2

    from drowsyalert.features.extra import POSE_INDICES, POSE_POINTS, estimate_pose

    camera = np.array([[640, 0, 320], [0, 640, 240], [0, 0, 1]], dtype=float)
    projected, _ = cv2.projectPoints(
        POSE_POINTS,
        np.array([0.3, 0, 0], dtype=float),
        np.array([0, 0, 1200], dtype=float),
        camera,
        np.zeros(4),
    )
    landmarks = np.zeros((468, 2))
    landmarks[list(POSE_INDICES)] = projected.reshape(-1, 2)
    pitch, yaw, roll = estimate_pose(landmarks, 640, 480)
    assert pitch == pytest.approx(np.degrees(0.3), abs=0.1)
    assert abs(yaw) < 0.1 and abs(roll) < 0.1


def test_yawn_counted_once_and_gap_resets_duration():
    from drowsyalert.features.extra import ExtraTracker
    from drowsyalert.utils.config import Config

    points = np.zeros((468, 2))
    points[61], points[291] = (0, 0), (10, 0)
    points[82], points[87] = (2, -4), (2, 4)
    points[312], points[317] = (8, -4), (8, 4)
    observation = FaceObservation(True, landmarks=points)
    tracker = ExtraTracker(Config(yawn_seconds=0.3), "perclos-yawn")
    for index in range(11):
        result = tracker.update(observation, index / 10, 640, 480)
    assert result.yawns == 1
    tracker.update(FaceObservation(False), 1.1, 640, 480)
    assert tracker.update(observation, 1.2, 640, 480).yawns == 1
