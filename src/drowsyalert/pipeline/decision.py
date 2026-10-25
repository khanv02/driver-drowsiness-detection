"""Decision rules consume observations, not cameras, UI or audio."""

from drowsyalert.types import AlertState, Decision, ExtraFeatures, EyeState, TemporalFeatures
from drowsyalert.utils.config import Config

METHODS = ("perclos", "perclos-yawn", "perclos-head-pose")


class DecisionEngine:
    def __init__(self, config: Config, method: str = "perclos"):
        if method not in METHODS:
            raise ValueError(f"Unknown method: {method}")
        self.config, self.method = config, method

    def decide(
        self, state: EyeState, temporal: TemporalFeatures, extra: ExtraFeatures = ExtraFeatures()
    ) -> Decision:
        if state == EyeState.UNKNOWN:
            return Decision(AlertState.UNKNOWN, "Eyes unavailable")
        if temporal.closed_seconds >= self.config.closed_seconds - 1e-9:
            return Decision(AlertState.ALERT, "Prolonged eye closure")
        if temporal.ready and temporal.perclos is not None:
            if temporal.perclos >= self.config.perclos_threshold:
                return Decision(AlertState.ALERT, "High estimated PERCLOS")
            if temporal.perclos >= self.config.combined_perclos_threshold:
                if self.method == "perclos-yawn" and extra.yawns >= self.config.yawn_count:
                    return Decision(AlertState.ALERT, "PERCLOS + yawns")
                if (
                    self.method == "perclos-head-pose"
                    and extra.head_down_seconds >= self.config.head_down_seconds
                ):
                    return Decision(AlertState.ALERT, "PERCLOS + head down")
        return Decision(AlertState.NORMAL, "" if temporal.ready else "Window warming up")
