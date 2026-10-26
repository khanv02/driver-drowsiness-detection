"""Protocol-parameterized temporal event metrics for synthetic and approved data."""

import math
import statistics
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class ReferenceEvent:
    event_id: str
    clip_id: str
    start_seconds: float
    end_seconds: float


@dataclass(frozen=True)
class AlertEpisode:
    alert_id: str
    clip_id: str
    start_seconds: float
    end_seconds: float


@dataclass(frozen=True)
class EventMatch:
    reference_id: str
    alert_id: str
    clip_id: str
    reference_start_seconds: float
    alert_start_seconds: float
    latency_seconds: float


@dataclass(frozen=True)
class MatchResult:
    matches: tuple[EventMatch, ...]
    unmatched_reference_ids: tuple[str, ...]
    unmatched_alert_ids: tuple[str, ...]


def match_events(
    references: Iterable[ReferenceEvent],
    alerts: Iterable[AlertEpisode],
    *,
    early_tolerance: float,
    late_tolerance: float,
) -> MatchResult:
    _validate_tolerance(early_tolerance, "early")
    _validate_tolerance(late_tolerance, "late")
    references = sorted(
        references,
        key=lambda item: (item.clip_id, item.start_seconds, item.event_id),
    )
    alerts = sorted(alerts, key=lambda item: (item.clip_id, item.start_seconds, item.alert_id))
    _validate_intervals(references, "reference")
    _validate_intervals(alerts, "alert")

    unused_alerts = {item.alert_id for item in alerts}
    matches = []
    unmatched_references = []
    for reference in references:
        candidates = [
            candidate
            for candidate in alerts
            if candidate.alert_id in unused_alerts
            and candidate.clip_id == reference.clip_id
            and reference.start_seconds - early_tolerance
            <= candidate.start_seconds
            <= reference.end_seconds + late_tolerance
        ]
        if not candidates:
            unmatched_references.append(reference.event_id)
            continue
        selected = candidates[0]
        unused_alerts.remove(selected.alert_id)
        matches.append(
            EventMatch(
                reference.event_id,
                selected.alert_id,
                reference.clip_id,
                reference.start_seconds,
                selected.start_seconds,
                selected.start_seconds - reference.start_seconds,
            )
        )
    return MatchResult(
        tuple(matches),
        tuple(unmatched_references),
        tuple(item.alert_id for item in alerts if item.alert_id in unused_alerts),
    )


def event_metrics(result: MatchResult, *, valid_observed_seconds: float) -> dict:
    if not math.isfinite(valid_observed_seconds) or valid_observed_seconds < 0:
        raise ValueError("valid_observed_seconds must be finite and nonnegative")
    tp = len(result.matches)
    fp = len(result.unmatched_alert_ids)
    fn = len(result.unmatched_reference_ids)
    precision = _ratio(tp, tp + fp)
    recall = _ratio(tp, tp + fn)
    if precision is None or recall is None:
        f1 = None
    elif precision == recall == 0:
        f1 = 0.0
    else:
        f1 = 2 * precision * recall / (precision + recall)
    valid_hours = valid_observed_seconds / 3600
    return {
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "false_alarms_per_valid_hour": _ratio(fp, valid_hours),
        "valid_observed_hours": valid_hours,
    }


def latency_summary(result: MatchResult) -> dict:
    values = [match.latency_seconds for match in result.matches]
    summary = {
        "detected_events": len(values),
        "missed_events": len(result.unmatched_reference_ids),
        "values_seconds": values,
        "mean_seconds": None,
        "median_seconds": None,
        "std_seconds": None,
        "min_seconds": None,
        "max_seconds": None,
        "p25_seconds": None,
        "p75_seconds": None,
    }
    if values:
        summary.update(
            mean_seconds=statistics.fmean(values),
            median_seconds=statistics.median(values),
            std_seconds=statistics.pstdev(values),
            min_seconds=min(values),
            max_seconds=max(values),
            p25_seconds=_percentile(values, 0.25),
            p75_seconds=_percentile(values, 0.75),
        )
    return summary


def coverage_summary(
    *, eligible_seconds: float, valid_seconds: float, unknown_seconds: float
) -> dict:
    values = (eligible_seconds, valid_seconds, unknown_seconds)
    if any(not math.isfinite(value) or value < 0 for value in values):
        raise ValueError("Coverage durations must be finite and nonnegative")
    if valid_seconds + unknown_seconds > eligible_seconds + 1e-9:
        raise ValueError("Valid and unknown duration cannot exceed eligible duration")
    return {
        "eligible_seconds": eligible_seconds,
        "valid_seconds": valid_seconds,
        "unknown_seconds": unknown_seconds,
        "coverage": _ratio(valid_seconds, eligible_seconds),
        "eligible_hours": eligible_seconds / 3600,
        "valid_hours": valid_seconds / 3600,
    }


def _validate_tolerance(value: float, name: str) -> None:
    if not math.isfinite(value) or value < 0:
        raise ValueError(f"{name} tolerance must be finite and nonnegative")


def _validate_intervals(intervals: list, kind: str) -> None:
    seen = set()
    for interval in intervals:
        identifier = (
            interval.event_id if isinstance(interval, ReferenceEvent) else interval.alert_id
        )
        if identifier in seen:
            raise ValueError(f"Duplicate {kind} ID: {identifier}")
        seen.add(identifier)
        values = (interval.start_seconds, interval.end_seconds)
        if (
            not interval.clip_id
            or not identifier
            or any(not math.isfinite(value) for value in values)
            or not 0 <= interval.start_seconds < interval.end_seconds
        ):
            raise ValueError(f"Invalid {kind} interval: {identifier}")


def _ratio(numerator: float, denominator: float) -> float | None:
    return None if denominator == 0 else numerator / denominator


def _percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * fraction
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)
