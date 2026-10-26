import math

import pytest

from drowsyalert.experiments.metrics import (
    AlertEpisode,
    ReferenceEvent,
    coverage_summary,
    event_metrics,
    latency_summary,
    match_events,
)


def reference(identifier, start, end, clip="clip-1"):
    return ReferenceEvent(identifier, clip, start, end)


def alert(identifier, start, end, clip="clip-1"):
    return AlertEpisode(identifier, clip, start, end)


def test_chronological_matching_is_one_to_one_and_clip_scoped():
    references = [
        reference("r1", 10.0, 12.0),
        reference("r2", 20.0, 22.0),
        reference("r3", 10.0, 12.0, "clip-2"),
    ]
    alerts = [
        alert("a1", 9.0, 10.5),
        alert("a2", 11.0, 11.5),
        alert("a3", 24.1, 25.0),
        alert("a4", 10.5, 11.0, "clip-2"),
    ]
    result = match_events(references, alerts, early_tolerance=1.0, late_tolerance=2.0)
    assert [(match.reference_id, match.alert_id) for match in result.matches] == [
        ("r1", "a1"),
        ("r3", "a4"),
    ]
    assert result.unmatched_reference_ids == ("r2",)
    assert result.unmatched_alert_ids == ("a2", "a3")


def test_matching_boundaries_are_inclusive_and_latency_is_signed():
    references = [reference("r1", 10.0, 12.0), reference("r2", 20.0, 22.0)]
    alerts = [alert("a1", 9.0, 9.5), alert("a2", 24.0, 25.0)]
    result = match_events(references, alerts, early_tolerance=1.0, late_tolerance=2.0)
    assert [match.latency_seconds for match in result.matches] == [-1.0, 4.0]


def test_alert_before_matching_window_is_false_positive_even_if_it_overlaps():
    result = match_events(
        [reference("r1", 10.0, 12.0)],
        [alert("too-early", 8.9, 11.0)],
        early_tolerance=1.0,
        late_tolerance=2.0,
    )
    assert not result.matches
    assert result.unmatched_reference_ids == ("r1",)
    assert result.unmatched_alert_ids == ("too-early",)


def test_known_event_counts_and_false_alarm_rate():
    result = match_events(
        [reference("r1", 10, 12), reference("r2", 20, 22), reference("r3", 30, 32)],
        [alert("a1", 10.5, 11), alert("a2", 21, 21.5), alert("fp", 50, 51)],
        early_tolerance=0,
        late_tolerance=0,
    )
    metrics = event_metrics(result, valid_observed_seconds=1800)
    assert metrics == {
        "tp": 2,
        "fp": 1,
        "fn": 1,
        "precision": pytest.approx(2 / 3),
        "recall": pytest.approx(2 / 3),
        "f1": pytest.approx(2 / 3),
        "false_alarms_per_valid_hour": 2.0,
        "valid_observed_hours": 0.5,
    }


def test_empty_denominators_are_unavailable_not_fabricated_zero():
    result = match_events([], [], early_tolerance=0, late_tolerance=0)
    metrics = event_metrics(result, valid_observed_seconds=0)
    assert metrics["precision"] is None
    assert metrics["recall"] is None
    assert metrics["f1"] is None
    assert metrics["false_alarms_per_valid_hour"] is None


def test_real_reference_and_alert_with_no_match_have_zero_scores():
    result = match_events(
        [reference("r", 1, 2)],
        [alert("a", 5, 6)],
        early_tolerance=0,
        late_tolerance=0,
    )
    metrics = event_metrics(result, valid_observed_seconds=10)
    assert (metrics["precision"], metrics["recall"], metrics["f1"]) == (0.0, 0.0, 0.0)


def test_latency_summary_excludes_misses_and_reports_population_statistics():
    result = match_events(
        [reference("r1", 10, 12), reference("r2", 20, 22), reference("miss", 40, 42)],
        [alert("a1", 9, 10), alert("a2", 22, 23)],
        early_tolerance=1,
        late_tolerance=0,
    )
    summary = latency_summary(result)
    assert summary["detected_events"] == 2
    assert summary["missed_events"] == 1
    assert summary["values_seconds"] == [-1, 2]
    assert summary["mean_seconds"] == 0.5
    assert summary["median_seconds"] == 0.5
    assert summary["std_seconds"] == 1.5
    assert summary["p25_seconds"] == -0.25
    assert summary["p75_seconds"] == 1.25


def test_no_detected_events_has_null_latency_statistics_and_real_miss_count():
    result = match_events(
        [reference("miss", 1, 2)], [], early_tolerance=0, late_tolerance=0
    )
    summary = latency_summary(result)
    assert summary["detected_events"] == 0 and summary["missed_events"] == 1
    for field in (
        "mean_seconds",
        "median_seconds",
        "std_seconds",
        "min_seconds",
        "max_seconds",
        "p25_seconds",
        "p75_seconds",
    ):
        assert summary[field] is None


def test_coverage_keeps_eligible_valid_and_unknown_time_separate():
    assert coverage_summary(eligible_seconds=100, valid_seconds=75, unknown_seconds=25) == {
        "eligible_seconds": 100,
        "valid_seconds": 75,
        "unknown_seconds": 25,
        "coverage": 0.75,
        "eligible_hours": pytest.approx(1 / 36),
        "valid_hours": pytest.approx(1 / 48),
    }
    assert coverage_summary(eligible_seconds=0, valid_seconds=0, unknown_seconds=0)[
        "coverage"
    ] is None


@pytest.mark.parametrize(
    "bad",
    [
        reference("r", 1, 1),
        reference("r", 2, 1),
        reference("r", math.nan, 1),
        alert("a", -1, 1),
    ],
)
def test_invalid_intervals_are_rejected(bad):
    references = [bad] if isinstance(bad, ReferenceEvent) else []
    alerts = [bad] if isinstance(bad, AlertEpisode) else []
    with pytest.raises(ValueError, match="interval"):
        match_events(references, alerts, early_tolerance=0, late_tolerance=0)


@pytest.mark.parametrize(("early", "late"), [(-1, 0), (0, -1), (math.nan, 0)])
def test_matching_tolerances_must_be_finite_and_nonnegative(early, late):
    with pytest.raises(ValueError, match="tolerance"):
        match_events([], [], early_tolerance=early, late_tolerance=late)


def test_duplicate_event_or_alert_ids_are_rejected():
    with pytest.raises(ValueError, match="Duplicate reference"):
        match_events(
            [reference("same", 1, 2), reference("same", 3, 4)],
            [],
            early_tolerance=0,
            late_tolerance=0,
        )
    with pytest.raises(ValueError, match="Duplicate alert"):
        match_events(
            [],
            [alert("same", 1, 2), alert("same", 3, 4)],
            early_tolerance=0,
            late_tolerance=0,
        )
