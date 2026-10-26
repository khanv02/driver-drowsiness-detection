import math

from drowsyalert.models.ear import EARBackend
from drowsyalert.types import EyeState, FaceObservation


def predict(ears, eye_valid=None):
    return EARBackend(threshold=0.21).predict(
        FaceObservation(True, ears=ears, eye_valid=eye_valid)
    )


def test_bilateral_closure_requires_two_valid_closed_eyes():
    result = predict((0.10, 0.20), (True, True))
    assert result.state == EyeState.CLOSED
    assert result.source == "landmark_ear"


def test_threshold_equality_is_open():
    assert predict((0.21, 0.20), (True, True)).state == EyeState.OPEN


def test_one_valid_open_eye_establishes_open_state():
    assert predict((0.30, None), (True, False)).state == EyeState.OPEN


def test_one_closed_eye_with_other_invalid_is_unknown():
    result = predict((0.10, None), (True, False))
    assert result.state == EyeState.UNKNOWN
    assert "bilateral" in result.reason.lower()


def test_invalid_or_nonfinite_ear_is_unknown():
    for ears in (None, (None, None), (math.nan, 0.10), (math.inf, 0.10)):
        result = predict(ears)
        assert result.state == EyeState.UNKNOWN
        assert result.source == "landmark_ear"


def test_invalid_face_is_unknown():
    result = EARBackend().predict(FaceObservation(False, "No face"))
    assert result.state == EyeState.UNKNOWN
    assert result.reason == "No face"
