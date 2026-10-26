"""Decision rules consume observations, not cameras, UI or audio."""

import math

from drowsyalert.types import AlertState, Decision, ExtraFeatures, EyeState, TemporalFeatures
from drowsyalert.utils.config import Config

METHODS = ("perclos", "perclos-yawn", "perclos-head-pose")
METHOD_IDENTITIES = {
    "perclos": ("A", None),
    "perclos-yawn": ("B", "yawn"),
    "perclos-head-pose": ("C", "head_pose"),
}


def method_metadata(config: Config, method: str, eye_source: str) -> dict:
    if method not in METHOD_IDENTITIES:
        raise ValueError(f"Unknown method: {method}")
    method_id, auxiliary_cue = METHOD_IDENTITIES[method]
    auxiliary_settings = {}
    if method == "perclos-yawn":
        auxiliary_settings = {
            "yawn_threshold": config.yawn_threshold,
            "yawn_seconds": config.yawn_seconds,
            "yawn_count": config.yawn_count,
        }
    elif method == "perclos-head-pose":
        auxiliary_settings = {
            "head_pose_reference_degrees": config.head_pose_reference_degrees,
            "head_down_degrees": config.head_down_degrees,
            "head_down_seconds": config.head_down_seconds,
        }
    return {
        "method_id": method_id,
        "method": method,
        "eye_source": eye_source,
        "auxiliary_cue": auxiliary_cue,
        "auxiliary_settings": auxiliary_settings,
        "common_settings": {
            "closed_seconds": config.closed_seconds,
            "max_gap_seconds": config.max_gap_seconds,
            "window_seconds": config.window_seconds,
            "min_valid_seconds": config.min_valid_seconds,
            "min_coverage": config.min_coverage,
            "perclos_threshold": config.perclos_threshold,
            "combined_perclos_threshold": config.combined_perclos_threshold,
        },
    }


class DecisionEngine:
    def __init__(self, config: Config, method: str = "perclos"):
        if method not in METHODS:
            raise ValueError(f"Unknown method: {method}")
        config.validate()
        self.config, self.method = config, method

    @staticmethod
    def _valid_temporal(temporal: TemporalFeatures) -> bool:
        scalars = (temporal.closed_seconds, temporal.coverage, temporal.valid_seconds)
        if any(not math.isfinite(value) for value in scalars):
            return False
        if temporal.closed_seconds < 0 or temporal.valid_seconds < 0:
            return False
        if not 0 <= temporal.coverage <= 1:
            return False
        return temporal.perclos is None or (
            math.isfinite(temporal.perclos) and 0 <= temporal.perclos <= 1
        )

    def decide(
        self, state: EyeState, temporal: TemporalFeatures, extra: ExtraFeatures = ExtraFeatures()
    ) -> Decision:
        if state == EyeState.UNKNOWN:
            return Decision(AlertState.UNKNOWN, "Eyes unavailable")
        if not self._valid_temporal(temporal):
            return Decision(AlertState.UNKNOWN, "Invalid temporal evidence")
        if temporal.closed_seconds >= self.config.closed_seconds - 1e-9:
            return Decision(AlertState.ALERT, "Prolonged eye closure")
        if not temporal.ready:
            return Decision(
                AlertState.UNKNOWN,
                "Window warming up: insufficient valid coverage",
            )
        if temporal.perclos is None:
            return Decision(AlertState.UNKNOWN, "PERCLOS unavailable")
        if temporal.perclos >= self.config.perclos_threshold:
            return Decision(AlertState.ALERT, "High estimated PERCLOS")
        if temporal.perclos < self.config.combined_perclos_threshold or self.method == "perclos":
            return Decision(AlertState.NORMAL, "Estimated PERCLOS below alert threshold")
        if self.method == "perclos-yawn":
            if not extra.yawn_valid:
                return Decision(
                    AlertState.UNKNOWN,
                    f"Yawn evidence unavailable: {extra.yawn_reason}",
                )
            if extra.yawns >= self.config.yawn_count:
                return Decision(AlertState.ALERT, "PERCLOS + yawns")
        if self.method == "perclos-head-pose":
            if not extra.head_pose_valid:
                return Decision(
                    AlertState.UNKNOWN,
                    f"Head-pose evidence unavailable: {extra.head_pose_reason}",
                )
            if extra.head_down_seconds >= self.config.head_down_seconds:
                return Decision(AlertState.ALERT, "PERCLOS + head down")
        return Decision(AlertState.NORMAL, "Estimated PERCLOS below alert threshold")
