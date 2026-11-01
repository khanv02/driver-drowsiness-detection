"""Deterministic validation-only replay and bounded configuration sweeps."""

import itertools
import json
import math
import statistics
from collections import deque
from dataclasses import asdict, dataclass, fields, replace
from pathlib import Path
from typing import Iterable, Iterator, Mapping

from drowsyalert.experiments.annotations import (
    Annotation,
    annotation_manifest_sha256,
    validate_annotations,
)
from drowsyalert.experiments.batch import BatchPlan, batch_plan_sha256, validate_batch_plan
from drowsyalert.experiments.evaluation import EvaluationProtocol, evaluate_method_runs
from drowsyalert.experiments.records import canonical_sha256, read_run_record
from drowsyalert.features.temporal import TemporalTracker
from drowsyalert.pipeline.decision import DecisionEngine
from drowsyalert.types import ExtraFeatures, EyeState
from drowsyalert.utils.config import Config

DEFAULT_MAX_CANDIDATES = 350


@dataclass(frozen=True)
class SweepAxis:
    field: str
    values: tuple[float | int, ...]


DEFAULT_SWEEP_AXES = (
    # Warm-up is the dominant unknown-time source in the v1.1 baseline.
    SweepAxis("window_seconds", (20.0, 30.0, 60.0)),
    SweepAxis("min_valid_seconds", (10.0, 20.0, 30.0)),
    SweepAxis("min_coverage", (0.5, 0.8)),
    SweepAxis("perclos_threshold", (0.10, 0.15, 0.20)),
    SweepAxis("closed_seconds", (1.5, 2.0)),
    SweepAxis("ear_threshold", (0.18, 0.21, 0.24)),
)


def default_sweep_axes() -> tuple[SweepAxis, ...]:
    return DEFAULT_SWEEP_AXES


def iter_sweep_configs(
    base_config: Config,
    *,
    axes: Iterable[SweepAxis] | None = None,
    max_candidates: int = DEFAULT_MAX_CANDIDATES,
) -> Iterator[Config]:
    """Yield a finite, deterministic grid after rejecting invalid configurations."""
    if max_candidates <= 0:
        raise ValueError("max_candidates must be positive")
    axes = list(default_sweep_axes() if axes is None else axes)
    if not axes:
        raise ValueError("At least one sweep axis is required")
    known_fields = {field.name for field in fields(Config)}
    names = [axis.field for axis in axes]
    if len(set(names)) != len(names):
        raise ValueError("Sweep axis fields must be unique")
    unknown = sorted(set(names) - known_fields)
    if unknown:
        raise ValueError(f"Unknown sweep fields: {unknown}")
    for axis in axes:
        if not axis.values:
            raise ValueError(f"Sweep axis has no values: {axis.field}")
    total = math.prod(len(axis.values) for axis in axes)
    if total > max_candidates:
        raise ValueError(
            f"Sweep grid has {total} combinations, above max_candidates={max_candidates}"
        )
    seen = set()
    for combination in itertools.product(*(axis.values for axis in axes)):
        overrides = dict(zip(names, combination, strict=True))
        candidate = replace(base_config, **overrides)
        try:
            candidate.validate()
        except ValueError:
            continue
        identity = config_sha256(candidate)
        if identity in seen:
            continue
        seen.add(identity)
        yield candidate


def config_sha256(config: Config) -> str:
    return canonical_sha256(asdict(config))


def replay_run_record(record: Mapping, config: Config) -> dict:
    """Recompute frame states from stored observations without rerunning face inference."""
    config.validate()
    if record.get("status") != "completed":
        raise ValueError("Only completed run records can be replayed")
    if record.get("model", {}).get("eye_source") != "landmark_ear":
        raise ValueError("Replay requires landmark_ear run records")
    method = str(record.get("method", {}).get("method", ""))
    if method not in {"perclos", "perclos-yawn", "perclos-head-pose"}:
        raise ValueError(f"Unsupported replay method: {method}")
    frames = record.get("frames")
    if not isinstance(frames, list) or not frames:
        raise ValueError("Replay requires stored frame observations")

    source_reference = _finite(record.get("config", {}).get("head_pose_reference_degrees"))
    tracker = TemporalTracker(
        config.window_seconds,
        config.min_valid_seconds,
        config.min_coverage,
        config.max_gap_seconds,
        source="landmark_ear",
    )
    extra_tracker = _ReplayExtraTracker(
        config, method, 0.0 if source_reference is None else source_reference
    )
    engine = DecisionEngine(config, method)
    replayed_frames = []
    for frame in frames:
        timestamp = _required_finite(frame.get("timestamp"), "frame timestamp")
        eye_state, eye_reason = _replay_eye_state(frame, config.ear_threshold)
        temporal = tracker.update(timestamp, eye_state)
        extra = extra_tracker.update(frame, timestamp)
        decision = engine.decide(eye_state, temporal, extra)
        output = dict(frame)
        output.update(
            eye_source="landmark_ear",
            eye_threshold=config.ear_threshold,
            eye_state=eye_state.value,
            eye_reason=eye_reason,
            closed_seconds=temporal.closed_seconds,
            perclos=temporal.perclos,
            coverage=temporal.coverage,
            valid_seconds=temporal.valid_seconds,
            ready=temporal.ready,
            window_seconds=temporal.window_seconds,
            window_start=temporal.window_start,
            window_end=temporal.window_end,
            yawns=extra.yawns,
            mar=extra.mar,
            yawn_valid=extra.yawn_valid,
            yawn_event=extra.yawn_event,
            yawn_active_seconds=extra.yawn_active_seconds,
            yawn_reason=extra.yawn_reason,
            pitch=extra_tracker.relative_pitch,
            head_down_seconds=extra.head_down_seconds,
            head_down=extra.head_down,
            head_pose_valid=extra.head_pose_valid,
            pose_reference_pitch=extra.pose_reference_pitch,
            head_pose_reason=extra.head_pose_reason,
            state=decision.state.value,
            reason=decision.reason,
        )
        replayed_frames.append(output)

    replayed = dict(record)
    replayed["frames"] = replayed_frames
    replayed["replay"] = {
        "source_run_id": record.get("run_id"),
        "source_config_sha256": record.get("config_sha256"),
        "replay_config_sha256": config_sha256(config),
    }
    return replayed


def load_replay_records(plan: BatchPlan, output_root: Path) -> dict[str, tuple[dict, ...]]:
    """Load the exact planned validation records and reject test or mismatched data."""
    validate_batch_plan(plan)
    if plan.partition != "validation":
        raise ValueError("Offline replay is restricted to the validation partition")
    records: dict[str, tuple[dict, ...]] = {}
    for method in plan.methods:
        loaded = []
        for clip in plan.clips:
            path = output_root / "runs" / method.method_id / f"{clip.clip_id}.json"
            if not path.is_file():
                raise ValueError(f"Planned validation record is missing: {path}")
            record = read_run_record(path)
            if (
                record.get("status") != "completed"
                or record.get("source", {}).get("id") != clip.clip_id
                or record.get("source", {}).get("sha256") != clip.sha256
                or record.get("source", {}).get("kind") != "video_media"
                or record.get("method", {}).get("method_id") != method.method_id
                or record.get("model", {}).get("eye_source") != "landmark_ear"
                or record.get("audio", {}).get("enabled") is not False
            ):
                raise ValueError(f"Replay record is incompatible with the plan: {path}")
            if record.get("data", {}).get("split_id") not in (None, plan.split_id):
                raise ValueError(f"Replay record split does not match the plan: {path}")
            loaded.append(record)
        records[method.method_id] = tuple(loaded)
    return records


def evaluate_replay_candidate(
    plan: BatchPlan,
    records_by_method: Mapping[str, Iterable[Mapping]],
    annotations: Iterable[Annotation],
    protocol: EvaluationProtocol,
    config: Config,
) -> dict[str, dict]:
    """Replay every planned method/clip once and recalculate the standard metrics."""
    validate_batch_plan(plan)
    if plan.partition != "validation":
        raise ValueError("Offline replay is restricted to the validation partition")
    media_durations = {clip.clip_id: clip.duration_seconds for clip in plan.clips}
    annotations = list(annotations)
    results = {}
    for method in plan.methods:
        replayed = [
            replay_run_record(record, config) for record in records_by_method[method.method_id]
        ]
        results[method.method_id] = evaluate_method_runs(
            method.method_id,
            annotations,
            media_durations,
            replayed,
            protocol,
        )
    return results


def run_validation_sweep(
    plan: BatchPlan,
    *,
    output_root: Path,
    annotations: Iterable[Annotation],
    protocol: EvaluationProtocol,
    base_config: Config | None = None,
    axes: Iterable[SweepAxis] | None = None,
    max_candidates: int = DEFAULT_MAX_CANDIDATES,
) -> dict:
    """Evaluate a bounded configuration grid over stored validation observations only."""
    validate_batch_plan(plan)
    if plan.partition != "validation":
        raise ValueError("Offline replay is restricted to the validation partition")
    durations = {clip.clip_id: clip.duration_seconds for clip in plan.clips}
    rows = list(annotations)
    if any(row.split != "validation" for row in rows):
        raise ValueError("Held-out test annotations must not enter the validation sweep")
    rows = validate_annotations(rows, durations)
    if base_config is None:
        base_config = Config(**plan.shared_config)
    base_config.validate()
    selected_axes = default_sweep_axes() if axes is None else tuple(axes)
    records_by_method = load_replay_records(plan, output_root)
    configs = list(
        iter_sweep_configs(
            base_config,
            axes=selected_axes,
            max_candidates=max_candidates,
        )
    )
    if not configs:
        raise ValueError("The bounded sweep produced no valid configuration")

    candidates = []
    for index, config in enumerate(configs, start=1):
        methods = evaluate_replay_candidate(
            plan, records_by_method, rows, protocol, config
        )
        candidate_sha256 = config_sha256(config)
        candidates.append(
            {
                "index": index,
                "candidate_id": f"cfg-{candidate_sha256[:16]}",
                "config": asdict(config),
                "config_sha256": candidate_sha256,
                "methods": methods,
                "aggregate": _aggregate(methods),
            }
        )
    result = {
        "schema_version": 1,
        "partition": "validation",
        "plan_sha256": batch_plan_sha256(plan),
        "dataset_id": plan.dataset_id,
        "split_id": plan.split_id,
        "code_revision": plan.code_revision,
        "clip_ids": [clip.clip_id for clip in plan.clips],
        "annotations_sha256": annotation_manifest_sha256(rows),
        "base_config": asdict(base_config),
        "base_config_sha256": config_sha256(base_config),
        "search_space": {
            "axes": [
                {"field": axis.field, "values": list(axis.values)}
                for axis in selected_axes
            ],
            "max_candidates": max_candidates,
            "generated_candidates": len(candidates),
        },
        "candidates": candidates,
    }
    result["sweep_sha256"] = canonical_sha256(result)
    return result


def write_sweep_result(path: Path, result: Mapping, *, overwrite: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w" if overwrite else "x", encoding="utf-8", newline="\n") as destination:
        json.dump(result, destination, indent=2, sort_keys=True, allow_nan=False)
        destination.write("\n")


def _replay_eye_state(frame: Mapping, threshold: float) -> tuple[EyeState, str]:
    if not bool(frame.get("valid")):
        return EyeState.UNKNOWN, str(frame.get("observation_reason") or "Face unavailable")
    ears = (_finite(frame.get("ear_left")), _finite(frame.get("ear_right")))
    valid = tuple(value is not None for value in ears)
    if any(flag and value >= threshold for flag, value in zip(valid, ears, strict=True)):
        return EyeState.OPEN, ""
    if all(valid) and all(value < threshold for value in ears):
        return EyeState.CLOSED, ""
    return EyeState.UNKNOWN, "Bilateral EAR evidence unavailable"


class _ReplayExtraTracker:
    def __init__(self, config: Config, method: str, source_reference: float):
        self.config = config
        self.method = method
        self.source_reference = source_reference
        self.last_time = None
        self.yawn_start = None
        self.yawn_counted = False
        self.yawns = deque()
        self.head_start = None
        self.relative_pitch = None

    def update(self, frame: Mapping, timestamp: float) -> ExtraFeatures:
        gap = (
            self.last_time is not None
            and timestamp - self.last_time > self.config.max_gap_seconds
        )
        self.last_time = timestamp
        if self.method == "perclos-yawn":
            return self._update_yawn(frame, timestamp, gap)
        if self.method == "perclos-head-pose":
            return self._update_head_pose(frame, timestamp, gap)
        return ExtraFeatures()

    def _update_yawn(self, frame: Mapping, timestamp: float, gap: bool) -> ExtraFeatures:
        while self.yawns and self.yawns[0] < timestamp - self.config.window_seconds:
            self.yawns.popleft()
        valid = bool(frame.get("valid"))
        if gap or not valid:
            self.yawn_start = None
            self.yawn_counted = False
        mar = _finite(frame.get("mar"))
        if not valid or mar is None:
            return ExtraFeatures(
                yawns=len(self.yawns),
                yawn_reason=(
                    str(frame.get("observation_reason") or "Mouth landmarks unavailable")
                    if not valid
                    else "Mouth observation unavailable"
                ),
            )
        event = False
        active_seconds = 0.0
        if mar >= self.config.yawn_threshold:
            if self.yawn_start is None:
                self.yawn_start = timestamp
            active_seconds = timestamp - self.yawn_start
            if not self.yawn_counted and active_seconds >= self.config.yawn_seconds - 1e-9:
                self.yawns.append(timestamp)
                self.yawn_counted = True
                event = True
        else:
            self.yawn_start, self.yawn_counted = None, False
        return ExtraFeatures(
            yawns=len(self.yawns),
            mar=mar,
            yawn_valid=True,
            yawn_event=event,
            yawn_active_seconds=active_seconds,
            yawn_reason="Mouth observation valid",
        )

    def _update_head_pose(self, frame: Mapping, timestamp: float, gap: bool) -> ExtraFeatures:
        self.relative_pitch = None
        valid = bool(frame.get("valid"))
        if gap or not valid:
            self.head_start = None
        reference = self.config.head_pose_reference_degrees
        if reference is None:
            raise ValueError("Replay requires a numeric head-pose reference")
        pitch = _finite(frame.get("pitch"))
        if not valid or pitch is None:
            return ExtraFeatures(
                pose_reference_pitch=reference,
                head_pose_reason=(
                    str(frame.get("observation_reason") or "Face landmarks unavailable")
                    if not valid
                    else "Head pose unavailable"
                ),
            )
        relative = (pitch + self.source_reference - reference + 180) % 360 - 180
        self.relative_pitch = relative
        head_seconds = 0.0
        if relative >= self.config.head_down_degrees:
            if self.head_start is None:
                self.head_start = timestamp
            head_seconds = timestamp - self.head_start
        else:
            self.head_start = None
        return ExtraFeatures(
            head_down_seconds=head_seconds,
            head_down=head_seconds >= self.config.head_down_seconds - 1e-9,
            head_pose_valid=True,
            pose_reference_pitch=reference,
            head_pose_reason="Head pose valid",
        )


def _aggregate(methods: Mapping[str, Mapping]) -> dict:
    event_rows = [item["event_metrics"] for item in methods.values()]
    coverages = [
        item["coverage"]["coverage"]
        for item in methods.values()
        if item["coverage"]["coverage"] is not None
    ]
    f1_values = [row["f1"] for row in event_rows if row["f1"] is not None]
    false_alarm_rates = [
        row["false_alarms_per_valid_hour"]
        for row in event_rows
        if row["false_alarms_per_valid_hour"] is not None
    ]
    latencies = [
        item["latency"]["mean_seconds"]
        for item in methods.values()
        if item["latency"]["mean_seconds"] is not None
    ]
    return {
        "method_count": len(methods),
        "total_tp": sum(row["tp"] for row in event_rows),
        "total_fp": sum(row["fp"] for row in event_rows),
        "total_fn": sum(row["fn"] for row in event_rows),
        "mean_f1": statistics.fmean(f1_values) if f1_values else None,
        "min_f1": min(f1_values) if f1_values else None,
        "min_coverage": min(coverages) if coverages else None,
        "max_false_alarms_per_valid_hour": (
            max(false_alarm_rates) if false_alarm_rates else None
        ),
        "mean_detected_latency_seconds": statistics.fmean(latencies) if latencies else None,
    }


def _finite(value) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def _required_finite(value, name: str) -> float:
    number = _finite(value)
    if number is None:
        raise ValueError(f"Invalid {name}")
    return number
