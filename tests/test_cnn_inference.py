import math

import numpy as np
import pytest

torch = pytest.importorskip("torch")

from drowsyalert.models.eye_cnn import (  # noqa: E402
    CNNBackend,
    classify_eye_probabilities,
)
from drowsyalert.types import EyeState, FaceObservation  # noqa: E402


@pytest.mark.parametrize(
    ("probabilities", "expected"),
    [
        ((0.2, 0.3), EyeState.OPEN),
        ((0.2, None), EyeState.OPEN),
        ((0.8, 0.9), EyeState.CLOSED),
        ((0.8, None), EyeState.UNKNOWN),
        ((0.55, 0.9), EyeState.UNKNOWN),
        ((None, None), EyeState.UNKNOWN),
    ],
)
def test_bilateral_probability_and_uncertainty_policy(probabilities, expected):
    state, _ = classify_eye_probabilities(probabilities, threshold=0.5, margin=0.1)
    assert state == expected


@pytest.mark.parametrize("probability", [-0.1, 1.1, math.nan, math.inf])
def test_probability_policy_rejects_invalid_values(probability):
    with pytest.raises(ValueError, match="probability"):
        classify_eye_probabilities((probability, 0.2), threshold=0.5, margin=0.1)


@pytest.mark.parametrize(
    ("threshold", "margin"),
    [(0, 0.1), (1, 0.1), (0.5, -0.1), (0.1, 0.2), (0.9, 0.2)],
)
def test_backend_rejects_invalid_confidence_policy(tmp_path, threshold, margin):
    with pytest.raises(ValueError):
        CNNBackend(tmp_path / "unused.pt", threshold=threshold, uncertainty_margin=margin)


def test_predict_preserves_per_eye_probabilities_and_source():
    class FixedModel(torch.nn.Module):
        def forward(self, inputs):
            closed = inputs.mean(dim=(1, 2, 3)).clamp(0.001, 0.999)
            return torch.stack(((1 - closed).log(), closed.log()), dim=1)

    backend = CNNBackend.__new__(CNNBackend)
    backend.model = FixedModel().eval()
    backend.metadata = {}
    backend.threshold = 0.5
    backend.uncertainty_margin = 0.1
    backend.checkpoint_sha256 = "a" * 64
    backend.source = "cnn_eye_classifier"
    open_eye = np.full((20, 20, 3), 51, dtype=np.uint8)
    closed_eye = np.full((20, 20, 3), 230, dtype=np.uint8)

    result = backend.predict(
        FaceObservation(
            True,
            eye_crops=(open_eye, closed_eye),
            eye_valid=(True, True),
        )
    )
    assert result.state == EyeState.OPEN
    assert result.source == "cnn_eye_classifier"
    assert result.probabilities[0] == pytest.approx(0.2, abs=0.01)
    assert result.probabilities[1] == pytest.approx(230 / 255, abs=0.01)

    partial = backend.predict(
        FaceObservation(True, eye_crops=(closed_eye, None), eye_valid=(True, False))
    )
    assert partial.state == EyeState.UNKNOWN
    assert partial.probabilities[0] == pytest.approx(230 / 255, abs=0.01)
    assert partial.probabilities[1] is None
    assert "bilateral" in partial.reason.lower()


def test_invalid_observation_is_unknown_without_model_call():
    backend = CNNBackend.__new__(CNNBackend)
    backend.model = None
    backend.source = "cnn_eye_classifier"
    result = backend.predict(FaceObservation(False, "Multiple faces"))
    assert result.state == EyeState.UNKNOWN
    assert result.source == "cnn_eye_classifier"
    assert result.reason == "Multiple faces"


def test_missing_and_incompatible_checkpoints_fail_explicitly(tmp_path):
    with pytest.raises(FileNotFoundError, match="Checkpoint not found"):
        CNNBackend(tmp_path / "missing.pt")
    incompatible = tmp_path / "incompatible.pt"
    torch.save({"architecture": "DifferentModel"}, incompatible)
    with pytest.raises(ValueError, match="incompatible"):
        CNNBackend(incompatible)
