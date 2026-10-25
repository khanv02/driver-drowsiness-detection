"""One small CNN and one preprocessing function shared by training and runtime."""

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


class CNNBackend:
    def __init__(self, checkpoint: Path, threshold: float = 0.5):
        torch.set_num_threads(min(4, torch.get_num_threads()))
        self.model, self.metadata = load_checkpoint(checkpoint)
        self.threshold = threshold

    def predict(self, observation):
        from drowsyalert.types import EyeObservation, EyeState

        if (
            not observation.valid
            or observation.eye_crops is None
            or any(eye is None for eye in observation.eye_crops)
        ):
            return EyeObservation(
                EyeState.UNKNOWN, source="cnn", reason="Bilateral eye crops unavailable"
            )
        inputs = torch.stack([preprocess_eye(eye) for eye in observation.eye_crops])
        with torch.inference_mode():
            probabilities = self.model(inputs).softmax(dim=1)[:, 1].tolist()
        state = (
            EyeState.CLOSED if all(p >= self.threshold for p in probabilities) else EyeState.OPEN
        )
        return EyeObservation(state, tuple(probabilities), source="cnn")
