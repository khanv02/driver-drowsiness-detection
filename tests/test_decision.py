import math

import pytest

from drowsyalert.pipeline.decision import DecisionEngine, method_metadata
from drowsyalert.types import AlertState, ExtraFeatures, EyeState, TemporalFeatures
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


def test_method_a_ignores_all_auxiliary_evidence():
    extra = ExtraFeatures(
        yawns=99,
        yawn_valid=True,
        head_down_seconds=99.0,
        head_down=True,
        head_pose_valid=True,
    )
    result = DecisionEngine(Config(), "perclos").decide(
        EyeState.OPEN, features(perclos=0.15), extra
    )
    assert result.state == AlertState.NORMAL


def test_method_b_consumes_only_valid_yawn_evidence_in_combined_band():
    engine = DecisionEngine(Config(yawn_count=2), "perclos-yawn")
    invalid = engine.decide(
        EyeState.OPEN,
        features(perclos=0.15),
        ExtraFeatures(yawns=2, yawn_valid=False, yawn_reason="Mouth unavailable"),
    )
    insufficient = engine.decide(
        EyeState.OPEN,
        features(perclos=0.15),
        ExtraFeatures(
            yawns=1,
            yawn_valid=True,
            head_down=True,
            head_pose_valid=True,
            head_down_seconds=99,
        ),
    )
    alert = engine.decide(
        EyeState.OPEN,
        features(perclos=0.15),
        ExtraFeatures(yawns=2, yawn_valid=True),
    )
    assert (invalid.state, invalid.reason) == (
        AlertState.UNKNOWN,
        "Yawn evidence unavailable: Mouth unavailable",
    )
    assert insufficient.state == AlertState.NORMAL
    assert (alert.state, alert.reason) == (AlertState.ALERT, "PERCLOS + yawns")


def test_method_c_consumes_only_valid_pose_evidence_in_combined_band():
    engine = DecisionEngine(Config(head_down_seconds=1.5), "perclos-head-pose")
    invalid = engine.decide(
        EyeState.OPEN,
        features(perclos=0.15),
        ExtraFeatures(
            head_down_seconds=2.0,
            head_pose_valid=False,
            head_pose_reason="Pose unavailable",
        ),
    )
    insufficient = engine.decide(
        EyeState.OPEN,
        features(perclos=0.15),
        ExtraFeatures(
            yawns=99,
            yawn_valid=True,
            head_down_seconds=1.4,
            head_pose_valid=True,
        ),
    )
    alert = engine.decide(
        EyeState.OPEN,
        features(perclos=0.15),
        ExtraFeatures(head_down_seconds=1.5, head_down=True, head_pose_valid=True),
    )
    assert (invalid.state, invalid.reason) == (
        AlertState.UNKNOWN,
        "Head-pose evidence unavailable: Pose unavailable",
    )
    assert insufficient.state == AlertState.NORMAL
    assert (alert.state, alert.reason) == (AlertState.ALERT, "PERCLOS + head down")


@pytest.mark.parametrize("method", ["perclos-yawn", "perclos-head-pose"])
def test_primary_perclos_alert_does_not_require_auxiliary_evidence(method):
    result = DecisionEngine(Config(), method).decide(
        EyeState.OPEN, features(perclos=0.2), ExtraFeatures()
    )
    assert (result.state, result.reason) == (AlertState.ALERT, "High estimated PERCLOS")


def test_method_metadata_keeps_common_perclos_settings_equal():
    config = Config()
    records = [
        method_metadata(config, method, "landmark_ear")
        for method in ("perclos", "perclos-yawn", "perclos-head-pose")
    ]
    assert [record["method_id"] for record in records] == ["A", "B", "C"]
    assert {record["eye_source"] for record in records} == {"landmark_ear"}
    assert len({tuple(record["common_settings"].items()) for record in records}) == 1
    assert [record["auxiliary_cue"] for record in records] == [None, "yawn", "head_pose"]
    assert records[0]["auxiliary_settings"] == {}
    assert records[1]["auxiliary_settings"]["yawn_count"] == config.yawn_count
    assert (
        records[2]["auxiliary_settings"]["head_pose_reference_degrees"]
        == config.head_pose_reference_degrees
    )
