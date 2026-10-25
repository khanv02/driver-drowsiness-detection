from drowsyalert.types import EyeObservation, EyeState, FaceObservation


class EARBackend:
    def __init__(self, threshold: float = 0.21):
        self.threshold = threshold

    def predict(self, observation: FaceObservation) -> EyeObservation:
        if not observation.valid or observation.ears is None:
            return EyeObservation(EyeState.UNKNOWN)
        closed = all(value < self.threshold for value in observation.ears)
        return EyeObservation(EyeState.CLOSED if closed else EyeState.OPEN)
