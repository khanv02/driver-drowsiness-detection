"""One small CNN and one preprocessing function shared by training and runtime."""

import hashlib
import math
from pathlib import Path

import cv2
import numpy as np

try:
    import torch
    from torch import nn
except ImportError as error:
    raise ImportError("Install CNN dependencies with: uv sync --extra cnn") from error

IMAGE_SIZE = 64
CLASS_NAMES = ["open", "closed"]


def preprocess_eye(image_bgr: np.ndarray) -> torch.Tensor:
    if image_bgr is None or image_bgr.ndim != 3 or image_bgr.shape[2] != 3 or not image_bgr.size:
        raise ValueError("Expected a nonempty BGR eye image")
    rgb = cv2.cvtColor(cv2.resize(image_bgr, (IMAGE_SIZE, IMAGE_SIZE)), cv2.COLOR_BGR2RGB)
    return torch.from_numpy(rgb.transpose(2, 0, 1).copy()).float().div(255)


class EyeCNN(nn.Module):
    def __init__(self):
        super().__init__()
        layers = []
        channels = 3
        for output in (32, 64, 128):
            layers.extend([nn.Conv2d(channels, output, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2)])
            channels = output
        self.features = nn.Sequential(*layers, nn.AdaptiveAvgPool2d(1))
        self.classifier = nn.Sequential(nn.Flatten(), nn.Dropout(0.3), nn.Linear(128, 2))

    def forward(self, inputs):
        return self.classifier(self.features(inputs))


def save_checkpoint(path: Path, model: EyeCNN, **metadata):
    path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "format_version": 1,
            "architecture": "EyeCNN",
            "class_names": CLASS_NAMES,
            "image_size": IMAGE_SIZE,
            "preprocessing": "BGR-to-RGB; CHW float32 / 255",
            "state_dict": {
                name: tensor.detach().cpu() for name, tensor in model.state_dict().items()
            },
            "metadata": metadata,
        },
        path,
    )


def load_checkpoint(path: Path):
    if not path.is_file():
        raise FileNotFoundError(f"Checkpoint not found: {path}. Train the CNN first.")
    checkpoint = torch.load(path, map_location="cpu", weights_only=True)
    expected = {
        "format_version": 1,
        "architecture": "EyeCNN",
        "class_names": CLASS_NAMES,
        "image_size": IMAGE_SIZE,
        "preprocessing": "BGR-to-RGB; CHW float32 / 255",
    }
    if any(checkpoint.get(key) != value for key, value in expected.items()):
        raise ValueError("Checkpoint architecture, labels or preprocessing are incompatible")
    model = EyeCNN()
    model.load_state_dict(checkpoint["state_dict"])
    model.eval()
    return model, checkpoint


def classify_eye_probabilities(
    probabilities: tuple[float | None, float | None],
    threshold: float,
    margin: float,
):
    from drowsyalert.types import EyeState

    if not math.isfinite(threshold) or not 0 < threshold < 1:
        raise ValueError("CNN threshold must be finite and between zero and one")
    if not math.isfinite(margin) or margin < 0:
        raise ValueError("CNN uncertainty margin must be finite and nonnegative")
    if threshold - margin <= 0 or threshold + margin > 1:
        raise ValueError("CNN uncertainty band must remain inside (0, 1]")
    for probability in probabilities:
        if probability is not None and (
            not math.isfinite(probability) or not 0 <= probability <= 1
        ):
            raise ValueError("CNN eye probability must be finite and between zero and one")
    lower, upper = threshold - margin, threshold + margin
    if any(value is not None and value <= lower for value in probabilities):
        return EyeState.OPEN, ""
    if all(value is not None and value >= upper for value in probabilities):
        return EyeState.CLOSED, ""
    if any(value is not None and lower < value < upper for value in probabilities):
        return EyeState.UNKNOWN, "CNN probability is inside the uncertainty band"
    return EyeState.UNKNOWN, "Bilateral confident CNN evidence unavailable"


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while block := source.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


class CNNBackend:
    source = "cnn_eye_classifier"

    def __init__(
        self,
        checkpoint: Path,
        threshold: float = 0.5,
        uncertainty_margin: float = 0.1,
    ):
        classify_eye_probabilities((None, None), threshold, uncertainty_margin)
        torch.set_num_threads(min(4, torch.get_num_threads()))
        self.model, self.metadata = load_checkpoint(checkpoint)
        self.threshold = threshold
        self.uncertainty_margin = uncertainty_margin
        self.checkpoint_sha256 = _file_sha256(checkpoint)

    def predict(self, observation):
        from drowsyalert.types import EyeObservation, EyeState

        if not observation.valid:
            return EyeObservation(
                EyeState.UNKNOWN,
                source=self.source,
                reason=observation.reason or "Face unavailable",
            )
        if observation.eye_crops is None or len(observation.eye_crops) != 2:
            return EyeObservation(
                EyeState.UNKNOWN,
                probabilities=(None, None),
                source=self.source,
                reason="Bilateral eye crops unavailable",
            )
        inferred_valid = tuple(eye is not None for eye in observation.eye_crops)
        valid = observation.eye_valid or inferred_valid
        usable = tuple(
            flag and inferred
            for flag, inferred in zip(valid, inferred_valid, strict=True)
        )
        indices = [index for index, flag in enumerate(usable) if flag]
        if not indices:
            return EyeObservation(
                EyeState.UNKNOWN,
                probabilities=(None, None),
                source=self.source,
                reason="Bilateral eye crops unavailable",
            )
        inputs = torch.stack(
            [preprocess_eye(observation.eye_crops[index]) for index in indices]
        )
        with torch.inference_mode():
            inferred = self.model(inputs).softmax(dim=1)[:, 1].tolist()
        probabilities: list[float | None] = [None, None]
        for index, probability in zip(indices, inferred, strict=True):
            probabilities[index] = probability
        values = (probabilities[0], probabilities[1])
        state, reason = classify_eye_probabilities(
            values, self.threshold, self.uncertainty_margin
        )
        return EyeObservation(state, values, source=self.source, reason=reason)
