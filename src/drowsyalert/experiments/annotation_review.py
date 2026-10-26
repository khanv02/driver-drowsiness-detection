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
from drowsyalert.experiments.video_manifest import VIDEO_MANIFEST_FIELDS

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
