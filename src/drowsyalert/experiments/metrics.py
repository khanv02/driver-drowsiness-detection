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
class ClipTimeline:
    clip_id: str
    duration_seconds: float


@dataclass(frozen=True)
class StatusSample:
    timestamp_seconds: float
    state: str


@dataclass(frozen=True)
class StatusInterval:
    clip_id: str
    start_seconds: float
    end_seconds: float
    state: str


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


def status_intervals(
    clip_id: str, samples: Iterable[StatusSample], *, end_seconds: float
) -> tuple[StatusInterval, ...]:
    """Convert ordered frame states to earlier-sample media-time intervals."""
    values = list(samples)
    if not clip_id or not math.isfinite(end_seconds) or end_seconds <= 0:
        raise ValueError("Invalid status sample clip or media duration")
    previous = None
    for sample in values:
        if (
            not math.isfinite(sample.timestamp_seconds)
            or sample.timestamp_seconds < 0
            or sample.timestamp_seconds >= end_seconds
            or sample.state not in {"ALERT", "NORMAL", "UNKNOWN"}
            or (previous is not None and sample.timestamp_seconds <= previous)
        ):
            raise ValueError("Invalid or non-increasing status sample")
        previous = sample.timestamp_seconds

    intervals = []
    if not values:
        return (StatusInterval(clip_id, 0.0, end_seconds, "UNKNOWN"),)
    if values[0].timestamp_seconds > 0:
        intervals.append(StatusInterval(clip_id, 0.0, values[0].timestamp_seconds, "UNKNOWN"))
    for index, sample in enumerate(values):
        end = values[index + 1].timestamp_seconds if index + 1 < len(values) else end_seconds
        if end > sample.timestamp_seconds:
            intervals.append(StatusInterval(clip_id, sample.timestamp_seconds, end, sample.state))
    return tuple(intervals)


def extract_alert_episodes(
    clip_id: str, samples: Iterable[StatusSample], *, end_seconds: float
) -> tuple[AlertEpisode, ...]:
    intervals = status_intervals(clip_id, samples, end_seconds=end_seconds)
    episodes = []
    active_start = None
    for interval in intervals:
        if interval.state == "ALERT" and active_start is None:
            active_start = interval.start_seconds
        elif interval.state != "ALERT" and active_start is not None:
            episodes.append((active_start, interval.start_seconds))
            active_start = None
    if active_start is not None:
        episodes.append((active_start, end_seconds))
    return tuple(
        AlertEpisode(f"{clip_id}-alert-{index:04d}", clip_id, start, end)
        for index, (start, end) in enumerate(episodes, start=1)
        if end > start
    )


def system_accuracy(
    timelines: Iterable[ClipTimeline],
    references: Iterable[ReferenceEvent],
    states: Iterable[StatusInterval],
    *,
    bin_seconds: float,
    positive_fraction: float = 0.5,
) -> dict:
    """Score fixed media-time bins while counting UNKNOWN as primary errors."""
    timelines = list(timelines)
    references = list(references)
    states = list(states)
    _validate_system_inputs(timelines, references, states, bin_seconds, positive_fraction)
    outcomes = []
    references_by_clip = _group_intervals(references)
    states_by_clip = _group_intervals(states)
    for timeline in timelines:
        start = 0.0
        while start < timeline.duration_seconds:
            end = min(start + bin_seconds, timeline.duration_seconds)
            width = end - start
            reference_overlap = _union_overlap(
                references_by_clip.get(timeline.clip_id, []), start, end
            )
            reference_positive = reference_overlap >= positive_fraction * width
            state_durations = {"ALERT": 0.0, "NORMAL": 0.0, "UNKNOWN": 0.0}
            for interval in states_by_clip.get(timeline.clip_id, []):
                overlap = max(
                    0.0,
                    min(end, interval.end_seconds) - max(start, interval.start_seconds),
                )
                state_durations[interval.state] += overlap
            alert_qualified = state_durations["ALERT"] >= positive_fraction * width
            normal_qualified = state_durations["NORMAL"] >= positive_fraction * width
            if alert_qualified == normal_qualified:
                predicted = "unknown"
            elif alert_qualified:
                predicted = "positive"
            else:
                predicted = "negative"
            outcomes.append((reference_positive, predicted))
            start = end
    return _summarize_system_outcomes(outcomes)


def grouped_system_accuracy(
    timelines: Iterable[ClipTimeline],
    references: Iterable[ReferenceEvent],
    states: Iterable[StatusInterval],
    *,
    conditions: dict[str, str],
    bin_seconds: float,
    positive_fraction: float = 0.5,
) -> dict[str, dict]:
    """Apply the identical bin definition to each declared clip-level condition."""
    timeline_values = list(timelines)
    reference_values = list(references)
    state_values = list(states)
    groups = sorted({conditions.get(item.clip_id, "unknown") for item in timeline_values})
    result = {}
    for group in groups:
        selected = [
            item for item in timeline_values if conditions.get(item.clip_id, "unknown") == group
        ]
        clip_ids = {item.clip_id for item in selected}
        result[group] = system_accuracy(
            selected,
            [item for item in reference_values if item.clip_id in clip_ids],
            [item for item in state_values if item.clip_id in clip_ids],
            bin_seconds=bin_seconds,
            positive_fraction=positive_fraction,
        )
    return result


def _summarize_system_outcomes(outcomes: list[tuple[bool, str]]) -> dict:
    tp = sum(reference and predicted == "positive" for reference, predicted in outcomes)
    tn = sum(not reference and predicted == "negative" for reference, predicted in outcomes)
    fp = sum(not reference and predicted == "positive" for reference, predicted in outcomes)
    fn = sum(reference and predicted == "negative" for reference, predicted in outcomes)
    unknown = sum(predicted == "unknown" for _reference, predicted in outcomes)
    total = len(outcomes)
    observed = total - unknown
    correct = tp + tn
    return {
        "bins": total,
        "observed_bins": observed,
        "unknown_bins": unknown,
        "correct_bins": correct,
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
        "accuracy": _ratio(correct, total),
        "observed_only_accuracy": _ratio(correct, observed),
        "observation_coverage": _ratio(observed, total),
    }


def _validate_system_inputs(
    timelines: list[ClipTimeline],
    references: list[ReferenceEvent],
    states: list[StatusInterval],
    bin_seconds: float,
    positive_fraction: float,
) -> None:
    if not math.isfinite(bin_seconds) or bin_seconds <= 0:
        raise ValueError("bin_seconds must be finite and positive")
    if not math.isfinite(positive_fraction) or not 0 < positive_fraction <= 1:
        raise ValueError("positive_fraction must be in (0, 1]")
    durations = {}
    for timeline in timelines:
        if (
            not timeline.clip_id
            or timeline.clip_id in durations
            or not math.isfinite(timeline.duration_seconds)
            or timeline.duration_seconds <= 0
        ):
            raise ValueError(f"Invalid or duplicate clip timeline: {timeline.clip_id}")
        durations[timeline.clip_id] = timeline.duration_seconds
    _validate_intervals(references, "reference")
    _validate_status_intervals(states)
    for interval in [*references, *states]:
        duration = durations.get(interval.clip_id)
        if duration is None or interval.end_seconds > duration:
            raise ValueError(f"Interval is outside declared timeline: {interval.clip_id}")


def _validate_status_intervals(states: list[StatusInterval]) -> None:
    previous_end: dict[str, float] = {}
    for interval in sorted(states, key=lambda item: (item.clip_id, item.start_seconds)):
        if (
            not interval.clip_id
            or interval.state not in {"ALERT", "NORMAL", "UNKNOWN"}
            or any(
                not math.isfinite(value)
                for value in (interval.start_seconds, interval.end_seconds)
            )
            or not 0 <= interval.start_seconds < interval.end_seconds
            or interval.start_seconds < previous_end.get(interval.clip_id, 0.0)
        ):
            raise ValueError(f"Invalid or overlapping status interval: {interval.clip_id}")
        previous_end[interval.clip_id] = interval.end_seconds


def _group_intervals(intervals: Iterable) -> dict[str, list]:
    result: dict[str, list] = {}
    for interval in intervals:
        result.setdefault(interval.clip_id, []).append(interval)
    return result


def _union_overlap(intervals: Iterable, start: float, end: float) -> float:
    clipped = sorted(
        (
            max(start, item.start_seconds),
            min(end, item.end_seconds),
        )
        for item in intervals
        if item.end_seconds > start and item.start_seconds < end
    )
    total = 0.0
    current_start = current_end = None
    for item_start, item_end in clipped:
        if current_start is None:
            current_start, current_end = item_start, item_end
        elif item_start <= current_end:
            current_end = max(current_end, item_end)
        else:
            total += current_end - current_start
            current_start, current_end = item_start, item_end
    if current_start is not None:
        total += current_end - current_start
    return total


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
