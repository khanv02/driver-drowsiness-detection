"""Shared contracts. Algorithmic modules never own cameras or user interfaces."""

from dataclasses import dataclass
from enum import StrEnum

import numpy as np


class EyeState(StrEnum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    UNKNOWN = "UNKNOWN"


class AlertState(StrEnum):
    NORMAL = "NORMAL"
    ALERT = "ALERT"
    UNKNOWN = "UNKNOWN"


@dataclass
class FaceObservation:
    valid: bool
    reason: str = ""
    landmarks: np.ndarray | None = None
    eye_crops: tuple[np.ndarray | None, np.ndarray | None] | None = None
    eye_boxes: tuple[
        tuple[int, int, int, int] | None, tuple[int, int, int, int] | None
    ] | None = None
    ears: tuple[float | None, float | None] | None = None
    eye_valid: tuple[bool, bool] | None = None


@dataclass(frozen=True)
class EyeObservation:
    state: EyeState
    probabilities: tuple[float, float] | None = None
    source: str = "unknown"
    reason: str = ""


@dataclass(frozen=True)
class TemporalFeatures:
    closed_seconds: float
    perclos: float | None
    coverage: float
    valid_seconds: float
    ready: bool
    continuous: bool


@dataclass(frozen=True)
class Decision:
    state: AlertState
    reason: str


@dataclass(frozen=True)
class ExtraFeatures:
    yawns: int = 0
    mar: float | None = None
    head_down_seconds: float = 0.0
    angles: tuple[float, float, float] | None = None
