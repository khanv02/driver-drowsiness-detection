"""Comparable, resumable headless execution plans for methods A, B, and C."""

import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable, Iterable, Mapping

from drowsyalert.experiments.records import canonical_sha256, read_run_record

EXPECTED_METHODS = (
    ("A", "perclos", None),
    ("B", "perclos-yawn", "yawn"),
    ("C", "perclos-head-pose", "head_pose"),
)
REQUIRED_SHARED_CONFIG = {
    "ear_threshold",
    "closed_seconds",
    "max_gap_seconds",
    "window_seconds",
    "min_valid_seconds",
    "min_coverage",
    "perclos_threshold",
    "combined_perclos_threshold",
    "yawn_threshold",
    "yawn_seconds",
    "yawn_count",
    "head_pose_reference_degrees",
    "head_down_degrees",
    "head_down_seconds",
}


@dataclass(frozen=True)
class BatchMethod:
    method_id: str
    method: str
    auxiliary_cue: str | None


@dataclass(frozen=True)
class BatchClip:
    clip_id: str
    relative_path: str
    sha256: str
    duration_seconds: float
    partition: str


@dataclass(frozen=True)
class BatchPlan:
    dataset_id: str
    split_id: str
    manifest_sha256: str
    code_revision: str
    random_seed: int
    partition: str
    eye_source: str
    shared_config: dict
    clips: tuple[BatchClip, ...]
    methods: tuple[BatchMethod, ...]

    def as_dict(self) -> dict:
        return {
            **asdict(self),
            "clips": [asdict(item) for item in self.clips],
            "methods": [asdict(item) for item in self.methods],
        }


def build_batch_plan(
    *,
    dataset_id: str,
    split_id: str,
    manifest_sha256: str,
    code_revision: str,
    random_seed: int,
    partition: str,
    eye_source: str,
    resolved_config: Mapping,
    clips: Iterable[BatchClip],
) -> BatchPlan:
    plan = BatchPlan(
        dataset_id=dataset_id,
        split_id=split_id,
        manifest_sha256=manifest_sha256,
        code_revision=code_revision,
        random_seed=random_seed,
        partition=partition,
        eye_source=eye_source,
        shared_config=dict(resolved_config),
        clips=tuple(sorted(clips, key=lambda item: item.clip_id)),
        methods=tuple(BatchMethod(*values) for values in EXPECTED_METHODS),
    )
    validate_batch_plan(plan)
    return plan


def validate_batch_plan(plan: BatchPlan) -> None:
    if not plan.dataset_id or not plan.split_id:
        raise ValueError("Dataset and split identities are required")
    if len(plan.manifest_sha256) != 64:
        raise ValueError("A full manifest SHA-256 is required")
    if not plan.code_revision:
        raise ValueError("A code revision is required")
    if plan.partition not in {"validation", "test"}:
        raise ValueError("Batch partition must be validation or test")
    if plan.eye_source != "landmark_ear":
        raise ValueError("Primary A/B/C comparison requires landmark_ear")
    actual_methods = tuple(
        (item.method_id, item.method, item.auxiliary_cue) for item in plan.methods
    )
    if actual_methods != EXPECTED_METHODS:
        raise ValueError("Batch plan must contain comparable methods A, B, and C")
    if not plan.clips:
        raise ValueError("Batch plan requires at least one clip")
    missing_config = REQUIRED_SHARED_CONFIG - set(plan.shared_config)
    if missing_config:
        raise ValueError(f"Shared config is incomplete: {sorted(missing_config)}")
    if plan.shared_config["head_pose_reference_degrees"] is None:
        raise ValueError("Controlled method C requires a frozen head-pose reference")
    seen = set()
    for clip in plan.clips:
        if clip.clip_id in seen:
            raise ValueError(f"Duplicate clip: {clip.clip_id}")
        seen.add(clip.clip_id)
        if (
            not clip.clip_id
            or not clip.relative_path
            or Path(clip.relative_path).is_absolute()
            or len(clip.sha256) != 64
            or any(character not in "0123456789abcdef" for character in clip.sha256)
            or not math.isfinite(clip.duration_seconds)
            or clip.duration_seconds <= 0
        ):
            raise ValueError(f"Invalid batch clip: {clip.clip_id}")
        if clip.partition != plan.partition:
            raise ValueError(f"Clip partition does not match plan: {clip.clip_id}")


def batch_plan_sha256(plan: BatchPlan) -> str:
    validate_batch_plan(plan)
    return canonical_sha256(plan.as_dict())


def run_batch(
    plan: BatchPlan,
    *,
    config,
    video_root: Path,
    output_root: Path,
    runner: Callable | None = None,
) -> dict:
    """Run every planned method/clip once; valid existing records are resumed."""
    from drowsyalert.pipeline.realtime import run as realtime_run

    validate_batch_plan(plan)
    if asdict(config) != plan.shared_config:
        raise ValueError("Runtime config does not match the frozen batch plan")
    runner = realtime_run if runner is None else runner
    output_root.mkdir(parents=True, exist_ok=True)
    _write_or_verify_plan(output_root / "batch-plan.json", plan)
    completed = []
    skipped = []
    failed = []
    for method in plan.methods:
        for clip in plan.clips:
            record_path = output_root / "runs" / method.method_id / f"{clip.clip_id}.json"
            if record_path.exists():
                _validate_existing_record(record_path, method, clip)
                skipped.append(f"{method.method_id}/{clip.clip_id}")
                continue
            video_path = video_root / Path(clip.relative_path)
            if not video_path.is_file():
                failed.append(
                    {"run": f"{method.method_id}/{clip.clip_id}", "error": "video missing"}
                )
                continue
            record_path.parent.mkdir(parents=True, exist_ok=True)
            try:
                runner(
                    config,
                    video=video_path,
                    backend="ear",
                    method=method.method,
                    headless=True,
                    record_path=record_path,
                    dataset_id=plan.dataset_id,
                    split_id=plan.split_id,
                    random_seed=plan.random_seed,
                    code_revision=plan.code_revision,
                    mute=True,
                    source_id=clip.clip_id,
                )
                _validate_existing_record(record_path, method, clip)
                completed.append(f"{method.method_id}/{clip.clip_id}")
            except (OSError, RuntimeError, ValueError, ImportError) as error:
                failed.append(
                    {
                        "run": f"{method.method_id}/{clip.clip_id}",
                        "error": f"{type(error).__name__}: {error}",
                    }
                )
    return {
        "plan_sha256": batch_plan_sha256(plan),
        "planned_runs": len(plan.methods) * len(plan.clips),
        "completed": completed,
        "skipped": skipped,
        "failed": failed,
    }


def export_batch_comparison(
    plan: BatchPlan,
    *,
    annotations: Iterable,
    protocol,
    output_root: Path,
    destination: Path,
) -> dict:
    """Recalculate A/B/C summaries from the exact planned records and clip set."""
    from drowsyalert.experiments.evaluation import evaluate_method_runs

    validate_batch_plan(plan)
    media_durations = {item.clip_id: item.duration_seconds for item in plan.clips}
    results = {}
    for method in plan.methods:
        records = []
        for clip in plan.clips:
            path = output_root / "runs" / method.method_id / f"{clip.clip_id}.json"
            _validate_existing_record(path, method, clip)
            records.append(read_run_record(path))
        results[method.method_id] = evaluate_method_runs(
            method.method_id,
            annotations,
            media_durations,
            records,
            protocol,
        )
    comparison = {
        "plan_sha256": batch_plan_sha256(plan),
        "dataset_id": plan.dataset_id,
        "split_id": plan.split_id,
        "partition": plan.partition,
        "clip_ids": [item.clip_id for item in plan.clips],
        "methods": results,
    }
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("x", encoding="utf-8", newline="\n") as output:
        json.dump(comparison, output, indent=2, sort_keys=True, allow_nan=False)
        output.write("\n")
    return comparison


def _write_or_verify_plan(path: Path, plan: BatchPlan) -> None:
    expected = plan.as_dict()
    if path.exists():
        if json.loads(path.read_text(encoding="utf-8")) != expected:
            raise ValueError("Existing batch plan does not match requested plan")
        return
    with path.open("x", encoding="utf-8", newline="\n") as destination:
        json.dump(expected, destination, indent=2, sort_keys=True, allow_nan=False)
        destination.write("\n")


def _validate_existing_record(path: Path, method: BatchMethod, clip: BatchClip) -> None:
    record = read_run_record(path)
    if (
        record.get("status") != "completed"
        or record.get("source", {}).get("id") != clip.clip_id
        or record.get("source", {}).get("sha256") != clip.sha256
        or record.get("method", {}).get("method_id") != method.method_id
        or record.get("model", {}).get("eye_source") != "landmark_ear"
        or record.get("audio", {}).get("enabled") is not False
    ):
        raise ValueError(f"Existing run record is incompatible: {path.name}")
