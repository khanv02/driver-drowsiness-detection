import math

import pytest

from drowsyalert.pipeline.decision import DecisionEngine
from drowsyalert.types import AlertState, EyeState, TemporalFeatures
from drowsyalert.utils.config import Config


def features(
    *,
    closed_seconds=0.0,
    perclos=0.1,
    coverage=1.0,
    valid_seconds=60.0,
    ready=True,
):
    return TemporalFeatures(
        closed_seconds=closed_seconds,
        perclos=perclos,
        coverage=coverage,
        valid_seconds=valid_seconds,
        ready=ready,
        continuous=True,
        source="landmark_ear",
        window_seconds=60.0,
        window_start=0.0,
        window_end=60.0,
    )


def test_unknown_eye_observation_overrides_historical_alert_evidence():
    result = DecisionEngine(Config()).decide(
        EyeState.UNKNOWN,
        features(closed_seconds=3.0, perclos=0.9),
    )
    assert result.state == AlertState.UNKNOWN
    assert result.reason == "Eyes unavailable"


def test_warmup_and_missing_perclos_are_unknown():
    engine = DecisionEngine(Config())
    warming = engine.decide(EyeState.OPEN, features(perclos=None, ready=False))
    unavailable = engine.decide(EyeState.OPEN, features(perclos=None, ready=True))
    assert (warming.state, warming.reason) == (
        AlertState.UNKNOWN,
        "Window warming up: insufficient valid coverage",
    )
    assert (unavailable.state, unavailable.reason) == (
        AlertState.UNKNOWN,
        "PERCLOS unavailable",
    )


def test_prolonged_closure_alerts_before_window_is_ready_at_boundary():
    engine = DecisionEngine(Config(closed_seconds=2.0))
    before = engine.decide(
        EyeState.CLOSED,
        features(closed_seconds=2.0 - 1e-6, perclos=None, ready=False),
    )
    at = engine.decide(
        EyeState.CLOSED,
        features(closed_seconds=2.0, perclos=None, ready=False),
    )
    above = engine.decide(
        EyeState.CLOSED,
        features(closed_seconds=2.1, perclos=None, ready=False),
    )
    assert before.state == AlertState.UNKNOWN
    assert (at.state, at.reason) == (AlertState.ALERT, "Prolonged eye closure")
    assert above == at


@pytest.mark.parametrize(
    ("perclos", "expected"),
    [
        (0.2 - 1e-6, AlertState.NORMAL),
        (0.2, AlertState.ALERT),
        (0.2 + 1e-6, AlertState.ALERT),
    ],
)
def test_perclos_threshold_is_inclusive(perclos, expected):
    result = DecisionEngine(Config(perclos_threshold=0.2)).decide(
        EyeState.OPEN, features(perclos=perclos)
    )
    assert result.state == expected
    assert result.reason == (
        "High estimated PERCLOS"
        if expected == AlertState.ALERT
        else "Estimated PERCLOS below alert threshold"
    )


def test_short_closure_with_ready_low_perclos_is_normal():
    result = DecisionEngine(Config(closed_seconds=2.0)).decide(
        EyeState.CLOSED,
        features(closed_seconds=0.5, perclos=0.1),
    )
    assert (result.state, result.reason) == (
        AlertState.NORMAL,
        "Estimated PERCLOS below alert threshold",
    )


@pytest.mark.parametrize(
    "temporal",
    [
        features(closed_seconds=-0.1),
        features(closed_seconds=math.nan),
        features(perclos=-0.1),
        features(perclos=1.1),
        features(perclos=math.inf),
        features(coverage=-0.1),
        features(coverage=1.1),
        features(valid_seconds=-1),
    ],
)
def test_invalid_temporal_evidence_becomes_unknown(temporal):
    result = DecisionEngine(Config()).decide(EyeState.OPEN, temporal)
    assert (result.state, result.reason) == (
        AlertState.UNKNOWN,
        "Invalid temporal evidence",
    )


def test_engine_rejects_invalid_configuration():
    with pytest.raises(ValueError, match="perclos_threshold"):
        DecisionEngine(Config(perclos_threshold=2.0))
