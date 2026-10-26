"""Deterministic aggregation of approved annotations and headless run records."""

import json
import math
import statistics
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping

from drowsyalert.experiments.annotations import Annotation
from drowsyalert.experiments.metrics import (
    ClipTimeline,
    ReferenceEvent,
    StatusInterval,
    StatusSample,
    coverage_summary,
    event_metrics,
    extract_alert_episodes,
    latency_summary,
    match_events,
    status_intervals,
    system_accuracy,
)


@dataclass(frozen=True)
class EvaluationProtocol:
    early_tolerance: float
    late_tolerance: float
    bin_seconds: float
    positive_fraction: float
    reference_labels: frozenset[str]

    def __post_init__(self) -> None:
        scalars = (
            self.early_tolerance,
            self.late_tolerance,
            self.bin_seconds,
            self.positive_fraction,
        )
        if any(not math.isfinite(value) for value in scalars):
            raise ValueError("Evaluation protocol values must be finite")
        if self.early_tolerance < 0 or self.late_tolerance < 0:
            raise ValueError("Evaluation tolerances must be nonnegative")
        if self.bin_seconds <= 0 or not 0 < self.positive_fraction <= 1:
            raise ValueError("Evaluation bin settings are invalid")
        if not self.reference_labels or any(not label for label in self.reference_labels):
            raise ValueError("At least one reference label is required")


def evaluate_method_runs(
    method_id: str,
    annotations: Iterable[Annotation],
    media_durations: Mapping[str, float],
    run_records: Iterable[Mapping],
    protocol: EvaluationProtocol,
) -> dict:
    annotations = list(annotations)
    records = list(run_records)
    record_by_clip = _validate_runs(method_id, media_durations, records)
    timelines = [
        ClipTimeline(clip_id, duration)
        for clip_id, duration in sorted(media_durations.items())
    ]

    references = []
    condition_counts = {
        "glasses": {},
        "head_movement": {},
        "lighting": {},
    }
    event_index: dict[str, int] = {}
    for row in annotations:
        if row.clip_id not in media_durations:
            raise ValueError(f"Annotation clip is outside evaluation corpus: {row.clip_id}")
        for field in condition_counts:
            value = getattr(row, field)
            condition_counts[field][value] = condition_counts[field].get(value, 0) + 1
        if row.label not in protocol.reference_labels:
            continue
        index = event_index.get(row.clip_id, 0) + 1
        event_index[row.clip_id] = index
        references.append(
            ReferenceEvent(
                f"{row.clip_id}-reference-{index:04d}",
                row.clip_id,
                row.start_seconds,
                row.end_seconds,
            )
        )

    all_alerts = []
    all_states: list[StatusInterval] = []
    failure_summary: dict[str, dict] = {}
    processing_values = []
    total_wall_seconds = 0.0
    for timeline in timelines:
        record = record_by_clip[timeline.clip_id]
        frames = record["frames"]
        samples = []
        for frame in frames:
            try:
                timestamp = float(frame["timestamp"])
                processing_ms = float(frame["processing_ms"])
                state = str(frame["state"])
            except (KeyError, TypeError, ValueError) as error:
                raise ValueError(
                    f"Invalid frame record for {timeline.clip_id}: {error}"
                ) from error
            if not math.isfinite(processing_ms) or processing_ms < 0:
                raise ValueError(f"Invalid processing_ms for {timeline.clip_id}")
            processing_values.append(processing_ms)
            samples.append(StatusSample(timestamp, state))
        clip_states = status_intervals(
            timeline.clip_id, samples, end_seconds=timeline.duration_seconds
        )
        all_states.extend(clip_states)
        all_alerts.extend(
            extract_alert_episodes(
                timeline.clip_id, samples, end_seconds=timeline.duration_seconds
            )
        )
        _accumulate_failures(failure_summary, frames, timeline.duration_seconds)
        wall_seconds = float(record.get("summary", {}).get("wall_seconds", 0.0))
        if not math.isfinite(wall_seconds) or wall_seconds < 0:
            raise ValueError(f"Invalid wall time for {timeline.clip_id}")
        total_wall_seconds += wall_seconds

    eligible_seconds = sum(media_durations.values())
    valid_seconds = sum(
        item.end_seconds - item.start_seconds
        for item in all_states
        if item.state != "UNKNOWN"
    )
    unknown_seconds = eligible_seconds - valid_seconds
    matches = match_events(
        references,
        all_alerts,
        early_tolerance=protocol.early_tolerance,
        late_tolerance=protocol.late_tolerance,
    )
    return {
        "method_id": method_id,
        "clips": len(timelines),
        "reference_events": len(references),
        "alert_episodes": len(all_alerts),
        "event_metrics": event_metrics(matches, valid_observed_seconds=valid_seconds),
        "latency": latency_summary(matches),
        "coverage": coverage_summary(
            eligible_seconds=eligible_seconds,
            valid_seconds=valid_seconds,
            unknown_seconds=unknown_seconds,
        ),
        "system_accuracy": system_accuracy(
            timelines,
            references,
            all_states,
            bin_seconds=protocol.bin_seconds,
            positive_fraction=protocol.positive_fraction,
        ),
        "condition_counts": {
            field: dict(sorted(counts.items()))
            for field, counts in sorted(condition_counts.items())
        },
        "observation_failures": dict(sorted(failure_summary.items())),
        "processing": {
            "frames": len(processing_values),
            "wall_seconds": total_wall_seconds,
            "mean_processing_ms": (
                statistics.fmean(processing_values) if processing_values else None
            ),
            "median_processing_ms": (
                statistics.median(processing_values) if processing_values else None
            ),
        },
    }


def write_evaluation_result(path: Path, result: Mapping, *, overwrite: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w" if overwrite else "x", encoding="utf-8", newline="\n") as destination:
        json.dump(result, destination, indent=2, sort_keys=True, allow_nan=False)
        destination.write("\n")


def _validate_runs(
    method_id: str,
    media_durations: Mapping[str, float],
    records: list[Mapping],
) -> dict[str, Mapping]:
    if not method_id:
        raise ValueError("Evaluation method ID is required")
    for clip_id, duration in media_durations.items():
        if not clip_id or not math.isfinite(duration) or duration <= 0:
            raise ValueError(f"Invalid media duration for {clip_id}")
    record_by_clip = {}
    for record in records:
        clip_id = str(record.get("source", {}).get("id", ""))
        if not clip_id or clip_id in record_by_clip:
            raise ValueError(f"Missing or duplicate run clip: {clip_id}")
        if record.get("status") != "completed":
            raise ValueError(f"Run is not completed: {clip_id}")
        if record.get("source", {}).get("kind") != "video_media":
            raise ValueError(f"Run is not media-time video: {clip_id}")
        if str(record.get("method", {}).get("method_id", "")) != method_id:
            raise ValueError(f"Run method does not match {method_id}: {clip_id}")
        if not record.get("frames"):
            raise ValueError(f"Run has no frame records: {clip_id}")
        record_by_clip[clip_id] = record
    if set(record_by_clip) != set(media_durations):
        raise ValueError("Run clips do not match the declared evaluation corpus")
    return record_by_clip


def _accumulate_failures(
    summary: dict[str, dict], frames: list[Mapping], end_seconds: float
) -> None:
    first_timestamp = float(frames[0]["timestamp"])
    if first_timestamp > 0:
        summary["no_status_before_first_frame"] = {
            "intervals": 1,
            "seconds": first_timestamp,
        }
    for index, frame in enumerate(frames):
        if str(frame.get("state")) != "UNKNOWN":
            continue
        start = float(frame["timestamp"])
        end = float(frames[index + 1]["timestamp"]) if index + 1 < len(frames) else end_seconds
        if end <= start:
            continue
        reason = str(frame.get("observation_reason") or frame.get("reason") or "unspecified")
        target = summary.setdefault(reason, {"intervals": 0, "seconds": 0.0})
        target["intervals"] += 1
        target["seconds"] += end - start
