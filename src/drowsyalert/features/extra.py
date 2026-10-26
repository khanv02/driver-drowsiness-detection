"""Yawn events and relative head pose, independent of display and alerts."""

import math
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
    points = np.asarray(points, dtype=float)
    if points.ndim != 2 or points.shape[0] <= max(POSE_INDICES) or points.shape[1] != 2:
        raise ValueError("Pose estimation requires the configured 2D face landmarks")
    if not np.isfinite(points[list(POSE_INDICES)]).all():
        raise ValueError("Pose estimation requires finite landmarks")
    if width <= 0 or height <= 0:
        raise ValueError("Pose estimation requires positive frame dimensions")
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
        self.baseline = config.head_pose_reference_degrees

    def update(
        self, observation: FaceObservation, timestamp: float, width: int, height: int
    ) -> ExtraFeatures:
        if not math.isfinite(timestamp):
            raise ValueError("Extra-feature timestamp must be finite")
        if self.last_time is not None and timestamp <= self.last_time:
            raise ValueError("Extra-feature timestamp must be strictly increasing")
        gap = (
            self.last_time is not None and timestamp - self.last_time > self.config.max_gap_seconds
        )
        self.last_time = timestamp
        while self.yawns and self.yawns[0] < timestamp - self.config.window_seconds:
            self.yawns.popleft()
        if gap or not observation.valid:
            self.yawn_start = self.head_start = None
            self.yawn_counted = False
        if self.method == "perclos-yawn":
            return self._update_yawn(observation, timestamp)
        if self.method == "perclos-head-pose":
            return self._update_head_pose(observation, timestamp, width, height)
        if not observation.valid or observation.landmarks is None:
            return ExtraFeatures(yawns=len(self.yawns))
        mar, angles, head_seconds = None, None, 0.0
        return ExtraFeatures(
            yawns=len(self.yawns),
            mar=mar,
            head_down_seconds=head_seconds,
            angles=angles,
        )

    def _update_head_pose(
        self, observation: FaceObservation, timestamp: float, width: int, height: int
    ) -> ExtraFeatures:
        if not observation.valid or observation.landmarks is None:
            self.head_start = None
            return ExtraFeatures(
                yawns=len(self.yawns),
                pose_reference_pitch=self.baseline,
                head_pose_reason=observation.reason or "Face landmarks unavailable",
            )
        try:
            absolute_angles = estimate_pose(observation.landmarks, width, height)
        except (cv2.error, IndexError, TypeError, ValueError) as error:
            self.head_start = None
            return ExtraFeatures(
                yawns=len(self.yawns),
                pose_reference_pitch=self.baseline,
                head_pose_reason=str(error),
            )
        if absolute_angles is None:
            self.head_start = None
            return ExtraFeatures(
                yawns=len(self.yawns),
                pose_reference_pitch=self.baseline,
                head_pose_reason="Head pose unavailable",
            )

        reference_captured = self.baseline is None
        if reference_captured:
            self.baseline = absolute_angles[0]
        pitch = (absolute_angles[0] - self.baseline + 180) % 360 - 180
        angles = (pitch, absolute_angles[1], absolute_angles[2])
        head_seconds = 0.0
        if pitch >= self.config.head_down_degrees:
            if self.head_start is None:
                self.head_start = timestamp
            head_seconds = timestamp - self.head_start
        else:
            self.head_start = None
        return ExtraFeatures(
            yawns=len(self.yawns),
            head_down_seconds=head_seconds,
            head_down=head_seconds >= self.config.head_down_seconds - 1e-9,
            angles=angles,
            head_pose_valid=True,
            pose_reference_pitch=self.baseline,
            head_pose_reason=(
                "Head pose valid; first valid pitch captured as reference"
                if reference_captured
                else "Head pose valid"
            ),
        )

    def _update_yawn(self, observation: FaceObservation, timestamp: float) -> ExtraFeatures:
        if not observation.valid or observation.landmarks is None:
            reason = observation.reason or "Mouth landmarks unavailable"
            return ExtraFeatures(yawns=len(self.yawns), yawn_reason=reason)
        try:
            mar = mouth_aspect_ratio(observation.landmarks)
        except (IndexError, TypeError, ValueError) as error:
            self.yawn_start = None
            self.yawn_counted = False
            return ExtraFeatures(yawns=len(self.yawns), yawn_reason=str(error))

        event = False
        active_seconds = 0.0
        if mar >= self.config.yawn_threshold:
            if self.yawn_start is None:
                self.yawn_start = timestamp
            active_seconds = timestamp - self.yawn_start
            if not self.yawn_counted and active_seconds >= self.config.yawn_seconds - 1e-9:
                self.yawns.append(timestamp)
                self.yawn_counted = True
                event = True
        else:
            self.yawn_start, self.yawn_counted = None, False
        return ExtraFeatures(
            yawns=len(self.yawns),
            mar=mar,
            yawn_valid=True,
            yawn_event=event,
            yawn_active_seconds=active_seconds,
            yawn_reason="Mouth observation valid",
        )
