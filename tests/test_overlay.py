import numpy as np

from drowsyalert.types import (
    AlertState,
    Decision,
    ExtraFeatures,
    EyeObservation,
    EyeState,
    FaceObservation,
    TemporalFeatures,
)
from drowsyalert.utils.overlay import ADVISORY_TEXT, CONTROLS_TEXT, draw_overlay, overlay_lines


def temporal(*, ready=True, perclos=0.1, coverage=1.0):
    return TemporalFeatures(
        closed_seconds=0.4,
        perclos=perclos,
        coverage=coverage,
        valid_seconds=40.0,
        ready=ready,
        continuous=True,
        source="landmark_ear",
        window_seconds=60.0,
        window_start=0.0,
        window_end=40.0,
    )


def test_normal_overlay_names_source_status_reason_controls_and_advisory():
    lines = overlay_lines(
        FaceObservation(True, ears=(0.3, 0.31)),
        EyeObservation(EyeState.OPEN, source="landmark_ear"),
        temporal(),
        ExtraFeatures(),
        Decision(AlertState.NORMAL, "Estimated PERCLOS below alert threshold"),
        24.5,
    )
    assert lines[0] == "Status: NORMAL | Estimated PERCLOS below alert threshold"
    assert "Eye source: landmark_ear | Eyes: OPEN" in lines
    assert "Estimated PERCLOS: 10.0% | coverage: 100%" in lines
    assert ADVISORY_TEXT in lines
    assert CONTROLS_TEXT in lines


def test_alert_and_unknown_reasons_are_visibly_distinct():
    alert = overlay_lines(
        FaceObservation(True),
        EyeObservation(EyeState.CLOSED, source="cnn_eye_classifier"),
        temporal(perclos=0.3),
        ExtraFeatures(),
        Decision(AlertState.ALERT, "High estimated PERCLOS"),
        10.0,
    )
    unknown = overlay_lines(
        FaceObservation(False, "No face"),
        EyeObservation(EyeState.UNKNOWN, source="landmark_ear", reason="Face unavailable"),
        temporal(ready=False, perclos=None, coverage=0.2),
        ExtraFeatures(),
        Decision(AlertState.UNKNOWN, "Window warming up: insufficient valid coverage"),
        10.0,
    )
    assert alert[0] == "Status: ALERT | High estimated PERCLOS"
    assert unknown[0].startswith("Status: UNKNOWN | Window warming up")
    assert "Observation: unavailable | No face" in unknown
    assert "Estimated PERCLOS: warming up | coverage: 20%" in unknown


def test_unavailable_probability_and_optional_features_are_readable():
    lines = overlay_lines(
        FaceObservation(True, eye_boxes=((1, 1, 4, 4), None)),
        EyeObservation(
            EyeState.UNKNOWN,
            probabilities=(0.8, None),
            source="cnn_eye_classifier",
            reason="Bilateral confident CNN evidence unavailable",
        ),
        temporal(ready=True, perclos=None),
        ExtraFeatures(mar=0.7, yawns=1, head_down_seconds=1.2, angles=(12.0, 0.0, 0.0)),
        Decision(AlertState.UNKNOWN, "PERCLOS unavailable"),
        18.0,
    )
    assert "Estimated PERCLOS: unavailable | coverage: 100%" in lines
    assert "P(closed): 0.80 / unknown" in lines
    assert "MAR: 0.70 | yawns: 1" in lines
    assert "Relative pitch: 12.0 | head down: 1.2s" in lines


def test_draw_overlay_renders_without_mutating_contract_values():
    frame = np.zeros((300, 640, 3), dtype=np.uint8)
    rendered = draw_overlay(
        frame,
        FaceObservation(True, eye_boxes=((5, 5, 20, 20), None)),
        EyeObservation(EyeState.OPEN, source="landmark_ear"),
        temporal(),
        ExtraFeatures(),
        Decision(AlertState.NORMAL, "Estimated PERCLOS below alert threshold"),
        30.0,
    )
    assert rendered is frame
    assert np.any(rendered)
