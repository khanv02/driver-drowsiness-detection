"""Strict temporal-reference annotations, independent of detector predictions."""

import csv
import hashlib
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Mapping

ANNOTATION_FIELDS = (
    "clip_id",
    "subject_group",
    "session_group",
    "split",
    "start_seconds",
    "end_seconds",
    "label",
    "annotation_source",
    "annotator_id",
    "adjudication",
    "confidence",
    "glasses",
    "lighting",
    "head_movement",
)
DEFAULT_LABELS = {
    "drowsy_event",
    "microsleep",
    "prolonged_eye_closure",
    "yawn",
    "head_nod",
}
FINAL_ADJUDICATION = {"provider", "agreed", "resolved", "single_reviewer", "not_applicable"}
ADJUDICATION = FINAL_ADJUDICATION | {"pending"}
SPLITS = {"validation", "test"}
CONDITION_VALUES = {
    "glasses": {"present", "absent", "unknown"},
    "lighting": {"normal", "low", "unknown"},
    "head_movement": {"present", "absent", "unknown"},
}
PROHIBITED_REFERENCE_SOURCES = {"drowsyalert", "model_prediction", "perclos_output"}


@dataclass(frozen=True)
class Annotation:
    clip_id: str
    subject_group: str
    session_group: str
    split: str
    start_seconds: float
    end_seconds: float
    label: str
    annotation_source: str
    annotator_id: str
    adjudication: str
    confidence: str
    glasses: str
    lighting: str
    head_movement: str

    def as_dict(self) -> dict:
        return asdict(self)


def load_annotations_csv(path: Path) -> list[Annotation]:
    with path.open(newline="", encoding="utf-8-sig") as source:
        reader = csv.DictReader(source)
        if tuple(reader.fieldnames or ()) != ANNOTATION_FIELDS:
            raise ValueError(f"Annotation columns must exactly match {ANNOTATION_FIELDS}")
        rows = []
        for line_number, row in enumerate(reader, start=2):
            try:
                row["start_seconds"] = float(row["start_seconds"])
                row["end_seconds"] = float(row["end_seconds"])
                rows.append(Annotation(**row))
            except (TypeError, ValueError) as error:
                raise ValueError(
                    f"Invalid annotation at CSV line {line_number}: {error}"
                ) from error
    return rows


def validate_annotations(
    annotations: Iterable[Annotation],
    media_durations: Mapping[str, float],
    *,
    allowed_labels: set[str] | None = None,
    require_final: bool = True,
) -> list[Annotation]:
    rows = list(annotations)
    labels = DEFAULT_LABELS if allowed_labels is None else allowed_labels
    seen = set()
    clip_identity: dict[str, tuple[str, str, str]] = {}
    subject_splits: dict[str, str] = {}
    session_splits: dict[str, str] = {}
    for row in rows:
        _validate_row(row, media_durations, labels, require_final)
        identity = tuple(row.as_dict()[field] for field in ANNOTATION_FIELDS)
        if identity in seen:
            raise ValueError(f"Duplicate annotation for {row.clip_id} at {row.start_seconds}")
        seen.add(identity)
        current = (row.subject_group, row.session_group, row.split)
        previous = clip_identity.setdefault(row.clip_id, current)
        if previous != current:
            raise ValueError(f"Clip identity is inconsistent for {row.clip_id}")
        _record_group(subject_splits, row.subject_group, row.split, "subject")
        _record_group(session_splits, row.session_group, row.split, "session")
    return rows


def _validate_row(
    row: Annotation,
    media_durations: Mapping[str, float],
    labels: set[str],
    require_final: bool,
) -> None:
    for field in ("clip_id", "subject_group", "session_group", "annotation_source", "annotator_id"):
        if not getattr(row, field).strip():
            raise ValueError(f"Annotation {field} must not be empty")
    duration = media_durations.get(row.clip_id)
    if duration is None:
        raise ValueError(f"No media duration supplied for clip {row.clip_id}")
    if not all(math.isfinite(value) for value in (row.start_seconds, row.end_seconds, duration)):
        raise ValueError(f"Annotation and media times must be finite for {row.clip_id}")
    if duration <= 0:
        raise ValueError(f"Media duration must be positive for {row.clip_id}")
    if not 0 <= row.start_seconds < row.end_seconds <= duration:
        raise ValueError(f"Annotation time is outside media bounds for {row.clip_id}")
    if row.split not in SPLITS:
        raise ValueError(f"Unsupported annotation split: {row.split}")
    if row.label not in labels:
        raise ValueError(f"Unapproved annotation label: {row.label}")
    if row.annotation_source.casefold() in PROHIBITED_REFERENCE_SOURCES:
        raise ValueError("Reference annotations must be independent of algorithm outputs")
    if row.adjudication not in ADJUDICATION:
        raise ValueError(f"Unsupported adjudication state: {row.adjudication}")
    if require_final and row.adjudication not in FINAL_ADJUDICATION:
        raise ValueError(f"Annotation lacks final adjudication: {row.clip_id}")
    for field, allowed in CONDITION_VALUES.items():
        if getattr(row, field) not in allowed:
            raise ValueError(f"Unsupported {field} condition: {getattr(row, field)}")


def _record_group(target: dict[str, str], group: str, split: str, kind: str) -> None:
    if group == "unknown":
        return
    previous = target.setdefault(group, split)
    if previous != split:
        raise ValueError(f"{kind} split leakage: {group} appears in {previous} and {split}")


def annotation_manifest_sha256(annotations: Iterable[Annotation]) -> str:
    serialized = sorted(
        (row.as_dict() for row in annotations),
        key=lambda row: (row["clip_id"], row["start_seconds"], row["end_seconds"], row["label"]),
    )
    canonical = json.dumps(serialized, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
