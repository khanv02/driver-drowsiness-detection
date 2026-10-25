"""Yawn events and relative head pose, independent of display and alerts."""

from collections import deque

import cv2
import numpy as np

from drowsyalert.features.geometry import mouth_aspect_ratio
from drowsyalert.types import ExtraFeatures, FaceObservation
from drowsyalert.utils.config import Config

POSE_INDICES = (1, 152, 33, 263, 61, 291)
# Canonical face: x right, y down, z backwards from the nose; arbitrary common units.
POSE_POINTS = np.array(
    [
        (0, 0, 0),
        (0, 330, 65),
        (-225, -170, 135),
        (225, -170, 135),
        (-150, 150, 125),
        (150, 150, 125),
    ],
    dtype=np.float64,
)


def estimate_pose(points: np.ndarray, width: int, height: int):
    camera = np.array([[width, 0, width / 2], [0, width, height / 2], [0, 0, 1]], dtype=np.float64)
    success, rotation, _ = cv2.solvePnP(
        POSE_POINTS,
        points[list(POSE_INDICES)],
        camera,
        np.zeros(4),
        flags=cv2.SOLVEPNP_ITERATIVE,
    )
    if not success:
        return None
    matrix, _ = cv2.Rodrigues(rotation)
    return tuple(float(value) for value in cv2.RQDecomp3x3(matrix)[0])


class ExtraTracker:
    def __init__(self, config: Config, method: str):
        self.config, self.method = config, method
        self.last_time = None
        self.yawn_start = None
        self.yawn_counted = False
        self.yawns = deque()
        self.head_start = None
        self.baseline = None

    def update(
        self, observation: FaceObservation, timestamp: float, width: int, height: int
    ) -> ExtraFeatures:
        gap = (
            self.last_time is not None and timestamp - self.last_time > self.config.max_gap_seconds
        )
        self.last_time = timestamp
        while self.yawns and self.yawns[0] < timestamp - self.config.window_seconds:
            self.yawns.popleft()
        if gap or not observation.valid:
            self.yawn_start = self.head_start = None
            self.yawn_counted = False
        if not observation.valid or observation.landmarks is None:
            return ExtraFeatures(yawns=len(self.yawns))
        mar, angles, head_seconds = None, None, 0.0
        if self.method == "perclos-yawn":
            mar = mouth_aspect_ratio(observation.landmarks)
            if mar >= self.config.yawn_threshold:
                if self.yawn_start is None:
                    self.yawn_start = timestamp
                if (
                    not self.yawn_counted
                    and timestamp - self.yawn_start >= self.config.yawn_seconds
                ):
                    self.yawns.append(timestamp)
                    self.yawn_counted = True
            else:
                self.yawn_start, self.yawn_counted = None, False
        if self.method == "perclos-head-pose":
            angles = estimate_pose(observation.landmarks, width, height)
            if angles is not None:
                if self.baseline is None:
                    self.baseline = angles[0]
                pitch = (angles[0] - self.baseline + 180) % 360 - 180
                angles = (pitch, angles[1], angles[2])
                if pitch >= self.config.head_down_degrees:
                    if self.head_start is None:
                        self.head_start = timestamp
                    head_seconds = timestamp - self.head_start
                else:
                    self.head_start = None
            else:
                self.head_start = None
        return ExtraFeatures(len(self.yawns), mar, head_seconds, angles)
