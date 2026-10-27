"""Human-only temporal annotation worklists and draft event recording."""

import csv
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

from drowsyalert.experiments.annotations import (
    ANNOTATION_FIELDS,
    DEFAULT_LABELS,
    Annotation,
    validate_annotations,
)
from drowsyalert.experiments.split import SplitAssignment
from drowsyalert.experiments.video_manifest import VIDEO_MANIFEST_FIELDS, VideoManifestRow

WORKLIST_FIELDS = (
    "clip_id",
    "relative_path",
    "duration_seconds",
    "source_category",
    "sex_group",
    "subject_group",
    "session_group",
    "split",
    "glasses",
    "lighting",
    "head_movement",
    "review_status",
)
DRAFT_EVENT_FIELDS = ("clip_id", "start_seconds", "end_seconds", "label")
REVIEW_STATUSES = {"pending", "in_progress", "reviewed"}
REVIEW_SCHEDULE_FIELDS = (
    "stage",
    "batch_id",
    "batch_order",
    "clip_id",
    "source_category",
    "relative_path",
    "duration_seconds",
    "review_status",
)


def review_wait_delay_ms(fps: float, *, paused: bool) -> int:
    """Return OpenCV's blocking delay when paused or real-time frame delay when playing."""
    if paused:
        return 0
    if not math.isfinite(fps) or fps <= 0:
        raise ValueError("Review playback FPS must be finite and positive")
    return max(1, round(1000 / fps))


@dataclass(frozen=True)
class ReviewClip:
    clip_id: str
    relative_path: str
    duration_seconds: float
    source_category: str
    sex_group: str
    subject_group: str = "unknown"
    session_group: str = "unknown"
    split: str = "unassigned"
    glasses: str = "unknown"
    lighting: str = "unknown"
    head_movement: str = "unknown"
    review_status: str = "pending"

    def as_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class DraftEvent:
    clip_id: str
    start_seconds: float
    end_seconds: float
    label: str

    def as_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class ReviewScheduleRow:
    stage: str
    batch_id: str
    batch_order: int
    clip_id: str
    source_category: str
    relative_path: str
    duration_seconds: float
    review_status: str

    def as_dict(self) -> dict:
        return asdict(self)


def load_manifest_worklist(path: Path) -> list[ReviewClip]:
    with path.open(newline="", encoding="utf-8-sig") as source:
        reader = csv.DictReader(source)
        if tuple(reader.fieldnames or ()) != VIDEO_MANIFEST_FIELDS:
            raise ValueError("Video manifest columns do not match the versioned contract")
        rows = [
            ReviewClip(
                clip_id=row["clip_id"],
                relative_path=row["relative_path"],
                duration_seconds=float(row["duration_seconds"]),
                source_category=row["source_category"],
                sex_group=row["sex_group"],
                subject_group=row["subject_group"],
                session_group=row["session_group"],
                split=row["split"],
            )
            for row in reader
        ]
    _validate_worklist(rows)
    return rows


def load_worklist(path: Path) -> list[ReviewClip]:
    with path.open(newline="", encoding="utf-8-sig") as source:
        reader = csv.DictReader(source)
        if tuple(reader.fieldnames or ()) != WORKLIST_FIELDS:
            raise ValueError("Review worklist columns do not match the versioned contract")
        rows = [
            ReviewClip(
                **{
                    **row,
                    "duration_seconds": float(row["duration_seconds"]),
                }
            )
            for row in reader
        ]
    _validate_worklist(rows)
    return rows


def write_worklist(path: Path, rows: Iterable[ReviewClip], *, overwrite: bool = False) -> None:
    values = sorted(rows, key=lambda row: row.clip_id)
    _validate_worklist(values)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w" if overwrite else "x", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=WORKLIST_FIELDS)
        writer.writeheader()
        for row in values:
            writer.writerow(row.as_dict())


def build_evaluation_worklist(
    manifest: Iterable[VideoManifestRow],
    split: Iterable[SplitAssignment],
    *,
    preserved_reviews: Iterable[ReviewClip] = (),
) -> list[ReviewClip]:
    manifest_by_id = {row.clip_id: row for row in manifest}
    preserved_by_id = {row.clip_id: row for row in preserved_reviews}
    rows = []
    seen = set()
    for assignment in split:
        if assignment.clip_id in seen:
            raise ValueError(f"Duplicate split assignment: {assignment.clip_id}")
        seen.add(assignment.clip_id)
        source = manifest_by_id.get(assignment.clip_id)
        if (
            source is None
            or source.relative_path != assignment.relative_path
            or source.sha256 != assignment.sha256
            or source.source_category != assignment.source_category
        ):
            raise ValueError(f"Split/manifest mismatch: {assignment.clip_id}")
        preserved = preserved_by_id.get(assignment.clip_id)
        if preserved is not None and preserved.split != assignment.split:
            raise ValueError(f"Preserved review changed split: {assignment.clip_id}")
        rows.append(
            ReviewClip(
                clip_id=source.clip_id,
                relative_path=source.relative_path,
                duration_seconds=source.duration_seconds,
                source_category=source.source_category,
                sex_group=source.sex_group,
                subject_group=preserved.subject_group if preserved else "unknown",
                session_group=preserved.session_group if preserved else "unknown",
                split=assignment.split,
                glasses=preserved.glasses if preserved else "unknown",
                lighting=preserved.lighting if preserved else "unknown",
                head_movement=preserved.head_movement if preserved else "unknown",
                review_status=preserved.review_status if preserved else "pending",
            )
        )
    _validate_worklist(rows)
    return sorted(rows, key=lambda row: (row.split, row.source_category, row.clip_id))


def build_review_schedule(
    worklist: Iterable[ReviewClip], *, batch_size: int = 4
) -> list[ReviewScheduleRow]:
    if batch_size <= 0:
        raise ValueError("Review batch size must be positive")
    rows = list(worklist)
    _validate_worklist(rows)
    schedule = []
    for stage in ("validation", "test"):
        pending = [
            row for row in rows if row.split == stage and row.review_status != "reviewed"
        ]
        ordered = _interleave_categories(pending)
        for batch_index, offset in enumerate(range(0, len(ordered), batch_size), start=1):
            batch_id = f"{stage}-{batch_index:02d}"
            for batch_order, row in enumerate(ordered[offset : offset + batch_size], start=1):
                schedule.append(
                    ReviewScheduleRow(
                        stage=stage,
                        batch_id=batch_id,
                        batch_order=batch_order,
                        clip_id=row.clip_id,
                        source_category=row.source_category,
                        relative_path=row.relative_path,
                        duration_seconds=row.duration_seconds,
                        review_status=row.review_status,
                    )
                )
    return schedule


def write_review_schedule(
    path: Path, rows: Iterable[ReviewScheduleRow], *, overwrite: bool = False
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w" if overwrite else "x", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=REVIEW_SCHEDULE_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow(row.as_dict())


def load_draft_events(path: Path) -> list[DraftEvent]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8-sig") as source:
        reader = csv.DictReader(source)
        if tuple(reader.fieldnames or ()) != DRAFT_EVENT_FIELDS:
            raise ValueError("Draft event columns do not match the versioned contract")
        rows = [
            DraftEvent(
                clip_id=row["clip_id"],
                start_seconds=float(row["start_seconds"]),
                end_seconds=float(row["end_seconds"]),
                label=row["label"],
            )
            for row in reader
        ]
    return rows


def write_draft_events(
    path: Path, rows: Iterable[DraftEvent], *, overwrite: bool = False
) -> None:
    values = sorted(rows, key=lambda row: (row.clip_id, row.start_seconds, row.end_seconds))
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w" if overwrite else "x", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=DRAFT_EVENT_FIELDS)
        writer.writeheader()
        for row in values:
            writer.writerow(row.as_dict())


def add_draft_event(
    rows: Iterable[DraftEvent],
    *,
    clip_id: str,
    start_seconds: float,
    end_seconds: float,
    label: str,
    duration_seconds: float,
) -> list[DraftEvent]:
    values = list(rows)
    if not clip_id or label not in DEFAULT_LABELS:
        raise ValueError("Draft event requires a clip ID and approved label")
    if (
        any(not math.isfinite(value) for value in (start_seconds, end_seconds, duration_seconds))
        or not 0 <= start_seconds < end_seconds <= duration_seconds
    ):
        raise ValueError("Draft event is outside media bounds")
    candidate = DraftEvent(clip_id, start_seconds, end_seconds, label)
    if candidate in values:
        raise ValueError("Duplicate draft event")
    values.append(candidate)
    return sorted(values, key=lambda row: (row.clip_id, row.start_seconds, row.end_seconds))


def finalize_annotations(
    events: Iterable[DraftEvent],
    worklist: Iterable[ReviewClip],
    *,
    annotation_source: str,
    annotator_id: str,
    adjudication: str,
    confidence: str,
) -> list[Annotation]:
    clips = {row.clip_id: row for row in worklist}
    annotations = []
    for event in events:
        clip = clips.get(event.clip_id)
        if clip is None:
            raise ValueError(f"Draft event has no worklist clip: {event.clip_id}")
        if clip.review_status != "reviewed":
            raise ValueError(f"Clip review is not final: {event.clip_id}")
        if clip.split not in {"validation", "test"}:
            raise ValueError(f"Clip split is not assigned: {event.clip_id}")
        annotations.append(
            Annotation(
                clip_id=event.clip_id,
                subject_group=clip.subject_group,
                session_group=clip.session_group,
                split=clip.split,
                start_seconds=event.start_seconds,
                end_seconds=event.end_seconds,
                label=event.label,
                annotation_source=annotation_source,
                annotator_id=annotator_id,
                adjudication=adjudication,
                confidence=confidence,
                glasses=clip.glasses,
                lighting=clip.lighting,
                head_movement=clip.head_movement,
            )
        )
    durations = {row.clip_id: row.duration_seconds for row in clips.values()}
    return validate_annotations(annotations, durations, require_final=True)


def write_annotations(path: Path, rows: Iterable[Annotation], *, overwrite: bool = False) -> None:
    values = sorted(rows, key=lambda row: (row.clip_id, row.start_seconds, row.end_seconds))
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w" if overwrite else "x", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=ANNOTATION_FIELDS)
        writer.writeheader()
        for row in values:
            writer.writerow(row.as_dict())


def worklist_summary(rows: Iterable[ReviewClip]) -> str:
    values = list(rows)
    counts = {
        status: sum(row.review_status == status for row in values)
        for status in REVIEW_STATUSES
    }
    return json.dumps({"clips": len(values), "status_counts": counts}, sort_keys=True)


def _validate_worklist(rows: Iterable[ReviewClip]) -> None:
    seen = set()
    for row in rows:
        if not row.clip_id or row.clip_id in seen:
            raise ValueError(f"Missing or duplicate worklist clip ID: {row.clip_id}")
        seen.add(row.clip_id)
        if not row.relative_path or Path(row.relative_path).is_absolute():
            raise ValueError(f"Worklist path must be relative: {row.clip_id}")
        if not math.isfinite(row.duration_seconds) or row.duration_seconds <= 0:
            raise ValueError(f"Invalid worklist duration: {row.clip_id}")
        if row.review_status not in REVIEW_STATUSES:
            raise ValueError(f"Unsupported review status: {row.review_status}")


def _interleave_categories(rows: list[ReviewClip]) -> list[ReviewClip]:
    queues = {
        category: sorted(
            (row for row in rows if row.source_category == category),
            key=lambda row: row.clip_id,
        )
        for category in ("microsleep", "yawning")
    }
    if sum(len(queue) for queue in queues.values()) != len(rows):
        raise ValueError("Review schedule contains an unsupported source category")
    ordered = []
    while any(queues.values()):
        for category in ("microsleep", "yawning"):
            if queues[category]:
                ordered.append(queues[category].pop(0))
    return ordered
