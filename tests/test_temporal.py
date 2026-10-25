import pytest

from drowsyalert.features.temporal import TemporalTracker
from drowsyalert.pipeline.decision import DecisionEngine
from drowsyalert.types import AlertState, ExtraFeatures, EyeState, TemporalFeatures
from drowsyalert.utils.config import Config


def test_long_closure_and_short_blink():
    tracker = TemporalTracker()
    engine = DecisionEngine(Config())
    for index in range(21):
        result = tracker.update(index / 10, EyeState.CLOSED)
    assert result.closed_seconds == pytest.approx(2)
    assert engine.decide(EyeState.CLOSED, result).state == AlertState.ALERT
    opened = tracker.update(2.1, EyeState.OPEN)
    assert opened.closed_seconds == 0
    assert engine.decide(EyeState.OPEN, opened).state == AlertState.NORMAL
    blink = tracker.update(2.2, EyeState.CLOSED)
    assert engine.decide(EyeState.CLOSED, blink).state == AlertState.NORMAL


@pytest.mark.parametrize("gap_state", [EyeState.UNKNOWN, EyeState.CLOSED])
def test_gap_breaks_closure(gap_state):
    tracker = TemporalTracker()
    tracker.update(0, EyeState.CLOSED)
    tracker.update(0.1, EyeState.CLOSED)
    tracker.update(1, gap_state)
    result = tracker.update(1.1, EyeState.CLOSED)
    assert result.closed_seconds <= 0.1 + 1e-9
    assert result.valid_seconds < 0.21


def test_time_weighting_and_unknown_coverage():
    tracker = TemporalTracker(window=1, min_valid=0.2, min_coverage=0.8, max_gap=0.5)
    tracker.update(0, EyeState.CLOSED)
    tracker.update(0.2, EyeState.OPEN)
    result = tracker.update(0.5, EyeState.OPEN)
    assert result.perclos == pytest.approx(0.4)  # Not one closed frame out of three.
    result = tracker.update(0.6, EyeState.UNKNOWN)
    result = tracker.update(0.8, EyeState.OPEN)
    assert result.valid_seconds == pytest.approx(0.5)
    assert result.coverage == pytest.approx(0.625)
    assert not result.ready


def test_eviction_clips_boundary_intervals():
    tracker = TemporalTracker(window=1, min_valid=0.2, max_gap=0.5)
    tracker.update(0, EyeState.CLOSED)
    tracker.update(0.4, EyeState.OPEN)
    tracker.update(0.8, EyeState.OPEN)
    result = tracker.update(1.2, EyeState.OPEN)
    assert result.valid_seconds == pytest.approx(1)
    assert result.perclos == pytest.approx(0.2)


@pytest.mark.parametrize("timestamp", [0, -1, float("nan"), float("inf")])
def test_invalid_timestamp(timestamp):
    tracker = TemporalTracker()
    tracker.update(0, EyeState.OPEN)
    with pytest.raises(ValueError):
        tracker.update(timestamp, EyeState.OPEN)


def test_window_must_be_ready_and_unknown_overrides_history():
    engine = DecisionEngine(Config())
    features = TemporalFeatures(0, 0.9, 1, 10, False, True)
    assert engine.decide(EyeState.OPEN, features).state == AlertState.NORMAL
    ready = TemporalFeatures(0, 0.9, 1, 60, True, True)
    assert engine.decide(EyeState.OPEN, ready).state == AlertState.ALERT
    assert engine.decide(EyeState.UNKNOWN, ready).state == AlertState.UNKNOWN


def test_combined_methods_share_same_base_rule():
    config = Config()
    features = TemporalFeatures(0, 0.12, 1, 60, True, True)
    extra = ExtraFeatures(yawns=2, head_down_seconds=2)
    assert DecisionEngine(config).decide(EyeState.OPEN, features, extra).state == AlertState.NORMAL
    for method in ("perclos-yawn", "perclos-head-pose"):
        assert (
            DecisionEngine(config, method).decide(EyeState.OPEN, features, extra).state
            == AlertState.ALERT
        )
