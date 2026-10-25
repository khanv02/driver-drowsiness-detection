"""Load one YAML file. Resolve resources independently of the current directory."""

import math
from dataclasses import asdict, dataclass, fields
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[3]


@dataclass
class Config:
    face_model: str = "models/pretrained/face_landmarker.task"
    checkpoint: str = "models/checkpoints/eye_cnn.pt"
    ear_threshold: float = 0.21
    closed_seconds: float = 2.0
    cooldown_seconds: float = 5.0
    max_gap_seconds: float = 0.25
    window_seconds: float = 60.0
    min_valid_seconds: float = 30.0
    min_coverage: float = 0.8
    perclos_threshold: float = 0.2
    combined_perclos_threshold: float = 0.1
    cnn_threshold: float = 0.5
    yawn_threshold: float = 0.6
    yawn_seconds: float = 1.5
    yawn_count: int = 2
    head_down_degrees: float = 20.0
    head_down_seconds: float = 1.5
    width: int = 640
    height: int = 480

    def validate(self) -> None:
        for key, value in asdict(self).items():
            if isinstance(value, (int, float)):
                if isinstance(value, bool) or not math.isfinite(value) or value <= 0:
                    raise ValueError(f"{key} must be finite and greater than zero")
        for key in (
            "min_coverage",
            "perclos_threshold",
            "combined_perclos_threshold",
            "cnn_threshold",
        ):
            if getattr(self, key) > 1:
                raise ValueError(f"{key} must be in (0, 1]")
        if self.min_valid_seconds > self.window_seconds:
            raise ValueError("min_valid_seconds must not exceed window_seconds")
        if self.combined_perclos_threshold > self.perclos_threshold:
            raise ValueError("combined_perclos_threshold must not exceed perclos_threshold")
        for key in ("width", "height", "yawn_count"):
            if not isinstance(getattr(self, key), int):
                raise ValueError(f"{key} must be an integer")

    def resource(self, value: str) -> Path:
        path = Path(value).expanduser()
        return path.resolve() if path.is_absolute() else (PROJECT_ROOT / path).resolve()


def load_config(path: Path | None = None) -> Config:
    path = path or PROJECT_ROOT / "configs/config.yaml"
    data = {}
    if path.exists():
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        if not isinstance(data, dict):
            raise ValueError("Configuration must be a YAML mapping")
    elif path != PROJECT_ROOT / "configs/config.yaml":
        raise FileNotFoundError(f"Configuration not found: {path}")
    unknown = set(data) - {f.name for f in fields(Config)}
    if unknown:
        raise ValueError(f"Unknown configuration fields: {sorted(unknown)}")
    config = Config(**data)
    config.validate()
    return config
