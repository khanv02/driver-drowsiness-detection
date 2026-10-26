"""Read-only NITYMED inventory and privacy-safe manifest records."""

import csv
import hashlib
import json
import math
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import Callable, Iterable

from drowsyalert.experiments.records import file_sha256

VIDEO_MANIFEST_FIELDS = (
    "clip_id",
    "relative_path",
    "sha256",
    "source_id",
    "source_category",
    "sex_group",
    "subject_group",
    "session_group",
    "split",
    "temporal_ground_truth",
    "duration_seconds",
    "fps",
    "width",
    "height",
    "frame_count",
    "size_bytes",
    "decodable",
    "license_id",
    "retrieval_date",
)


@dataclass(frozen=True)
class VideoMetadata:
    duration_seconds: float
    fps: float
    width: int
    height: int
    frame_count: int
    decodable: bool


@dataclass(frozen=True)
class VideoManifestRow:
    clip_id: str
    relative_path: str
    sha256: str
    source_id: str
    source_category: str
    sex_group: str
    subject_group: str
    session_group: str
    split: str
    temporal_ground_truth: str
    duration_seconds: float
    fps: float
    width: int
    height: int
    frame_count: int
    size_bytes: int
    decodable: bool
    license_id: str
    retrieval_date: str

    def as_dict(self) -> dict:
        return asdict(self)


def probe_video(path: Path) -> VideoMetadata:
    """Read container metadata and decode one frame without retaining pixels."""
    import cv2

    capture = cv2.VideoCapture(str(path))
    try:
        opened = capture.isOpened()
        fps = float(capture.get(cv2.CAP_PROP_FPS)) if opened else 0.0
        width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH)) if opened else 0
        height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT)) if opened else 0
        frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT)) if opened else 0
        decoded, _frame = capture.read() if opened else (False, None)
    finally:
        capture.release()
    duration = frame_count / fps if fps > 0 else 0.0
    return VideoMetadata(duration, fps, width, height, frame_count, bool(opened and decoded))


def build_nitymed_manifest(
    root: Path,
    *,
    retrieval_date: str,
    probe_video: Callable[[Path], VideoMetadata] = probe_video,
    hash_file: Callable[[Path], str] = file_sha256,
) -> list[VideoManifestRow]:
    """Inventory the extracted HDTV720 tree without moving or modifying videos."""
    _validate_retrieval_date(retrieval_date)
    root = Path(root)
    paths = sorted(root.rglob("*.mp4"), key=lambda item: item.as_posix().casefold())
    if not paths:
        raise ValueError(f"No MP4 videos found below {root}")

    rows: list[VideoManifestRow] = []
    clip_ids: set[str] = set()
    content_hashes: dict[str, str] = {}
    for path in paths:
        relative = path.relative_to(root)
        category, sex = _parse_nitymed_path(relative)
        clip_id = path.stem
        if clip_id in clip_ids:
            raise ValueError(f"Duplicate clip ID: {clip_id}")
        clip_ids.add(clip_id)

        digest = hash_file(path)
        if len(digest) != 64 or any(character not in "0123456789abcdef" for character in digest):
            raise ValueError(f"Invalid SHA-256 for {relative.as_posix()}")
        previous = content_hashes.setdefault(digest, clip_id)
        if previous != clip_id:
            raise ValueError(f"Duplicate video content: {previous} and {clip_id}")

        metadata = probe_video(path)
        _validate_metadata(metadata, clip_id)
        rows.append(
            VideoManifestRow(
                clip_id=clip_id,
                relative_path=relative.as_posix(),
                sha256=digest,
                source_id="nitymed-hdtv720",
                source_category=category,
                sex_group=sex,
                subject_group="unknown",
                session_group="unknown",
                split="unassigned",
                temporal_ground_truth="absent",
                duration_seconds=metadata.duration_seconds,
                fps=metadata.fps,
                width=metadata.width,
                height=metadata.height,
                frame_count=metadata.frame_count,
                size_bytes=path.stat().st_size,
                decodable=metadata.decodable,
                license_id="CC-BY",
                retrieval_date=retrieval_date,
            )
        )
    return sorted(rows, key=lambda row: row.clip_id)


def video_manifest_sha256(rows: Iterable[VideoManifestRow]) -> str:
    serialized = sorted((row.as_dict() for row in rows), key=lambda row: row["clip_id"])
    canonical = json.dumps(serialized, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def write_video_manifest(
    path: Path, rows: Iterable[VideoManifestRow], *, overwrite: bool = False
) -> None:
    serialized = sorted(rows, key=lambda row: row.clip_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = "w" if overwrite else "x"
    with path.open(mode, newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=VIDEO_MANIFEST_FIELDS)
        writer.writeheader()
        for row in serialized:
            writer.writerow(row.as_dict())


def manifest_summary(rows: Iterable[VideoManifestRow]) -> dict:
    values = list(rows)
    category_counts: dict[str, int] = {}
    group_counts: dict[str, int] = {}
    for row in values:
        category_counts[row.source_category] = category_counts.get(row.source_category, 0) + 1
        key = f"{row.source_category}/{row.sex_group}"
        group_counts[key] = group_counts.get(key, 0) + 1
    return {
        "dataset_id": "nitymed-hdtv720",
        "videos": len(values),
        "bytes": sum(row.size_bytes for row in values),
        "duration_seconds": sum(row.duration_seconds for row in values),
        "decodable_videos": sum(row.decodable for row in values),
        "category_counts": dict(sorted(category_counts.items())),
        "group_counts": dict(sorted(group_counts.items())),
        "manifest_sha256": video_manifest_sha256(values),
        "temporal_ground_truth": "absent",
        "subject_grouping": "unknown",
        "split": "unassigned",
    }


def _parse_nitymed_path(relative: Path) -> tuple[str, str]:
    parts = relative.parts
    if len(parts) != 4:
        raise ValueError(f"Unsupported NITYMED path: {relative.as_posix()}")
    category, sex, resolution, _filename = parts
    categories = {"Yawning": "yawning", "Microsleep": "microsleep"}
    sexes = {"Male": "male", "Female": "female"}
    if category not in categories or sex not in sexes or resolution != "HDTV720":
        raise ValueError(f"Unsupported NITYMED path: {relative.as_posix()}")
    return categories[category], sexes[sex]


def _validate_metadata(metadata: VideoMetadata, clip_id: str) -> None:
    numeric = (metadata.duration_seconds, metadata.fps)
    dimensions = (metadata.width, metadata.height, metadata.frame_count)
    if (
        not metadata.decodable
        or any(not math.isfinite(value) or value <= 0 for value in numeric)
        or any(value <= 0 for value in dimensions)
    ):
        raise ValueError(f"Video is not decodable or has invalid metadata: {clip_id}")


def _validate_retrieval_date(value: str) -> None:
    try:
        date.fromisoformat(value)
    except ValueError as error:
        raise ValueError("retrieval_date must use YYYY-MM-DD") from error
