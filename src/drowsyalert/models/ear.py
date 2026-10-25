import math

from drowsyalert.types import EyeObservation, EyeState, FaceObservation


class EARBackend:
    def __init__(self, threshold: float = 0.21):
        if not math.isfinite(threshold) or threshold <= 0:
            raise ValueError("EAR threshold must be finite and greater than zero")
        self.threshold = threshold

    def predict(self, observation: FaceObservation) -> EyeObservation:
        if not observation.valid:
            return EyeObservation(
                EyeState.UNKNOWN,
                source="landmark_ear",
                reason=observation.reason or "Face unavailable",
            )
        if observation.ears is None:
            return EyeObservation(
                EyeState.UNKNOWN, source="landmark_ear", reason="EAR unavailable"
            )
        inferred_valid = tuple(
            value is not None and math.isfinite(value) for value in observation.ears
        )
        valid = observation.eye_valid or inferred_valid
        valid = tuple(
            flag and inferred for flag, inferred in zip(valid, inferred_valid, strict=True)
        )

        if any(flag and value >= self.threshold for flag, value in zip(valid, observation.ears)):
            return EyeObservation(EyeState.OPEN, source="landmark_ear")
        if all(valid) and all(value < self.threshold for value in observation.ears):
            return EyeObservation(EyeState.CLOSED, source="landmark_ear")
        return EyeObservation(
            EyeState.UNKNOWN,
            source="landmark_ear",
            reason="Bilateral EAR evidence unavailable",
        )
