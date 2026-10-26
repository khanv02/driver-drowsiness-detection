"""Versioned, privacy-safe records for reproducible experiment runs."""

import csv
import hashlib
import json
import platform
import sys
from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable, Mapping

SCHEMA_VERSION = 1
RAW_FRAME_KEYS = {"image", "raw_frame", "frame_data", "pixels"}
FRAME_FIELDS = (
    "frame",
    "timestamp",
    "input_kind",
    "method",
    "method_id",
    "auxiliary_cue",
    "eye_source",
    "eye_threshold",
    "eye_uncertainty_margin",
    "checkpoint_sha256",
    "valid",
    "observation_reason",
    "eye_state",
    "eye_reason",
    "ear_left",
    "ear_right",
    "p_closed_left",
    "p_closed_right",
    "closed_seconds",
    "perclos",
    "coverage",
    "valid_seconds",
    "ready",
    "window_seconds",
    "window_start",
    "window_end",
    "yawns",
    "mar",
    "yawn_valid",
    "yawn_event",
    "yawn_active_seconds",
    "yawn_reason",
    "pitch",
    "head_down_seconds",
    "head_down",
    "head_pose_valid",
    "pose_reference_pitch",
    "head_pose_reason",
    "state",
    "reason",
    "processing_ms",
)


def canonical_sha256(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while block := source.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def _assert_json_safe(value: Any, location: str = "record") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            if not isinstance(key, str):
                raise ValueError(f"{location} keys must be strings")
            if key.lower() in RAW_FRAME_KEYS:
                raise ValueError(f"Raw frame field is prohibited: {location}.{key}")
            _assert_json_safe(child, f"{location}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            _assert_json_safe(child, f"{location}[{index}]")
    elif value is not None and not isinstance(value, (str, int, float, bool)):
        raise ValueError(f"{location} contains non-JSON value {type(value).__name__}")


def build_run_record(
    *,
    source_id: str,
    source_kind: str,
    source_sha256: str | None,
    method: Mapping[str, Any],
    resolved_config: Mapping[str, Any],
    model: Mapping[str, Any],
    audio: Mapping[str, Any],
    dataset_id: str | None = None,
    split_id: str | None = None,
    random_seed: int | None = None,
    code_revision: str | None = None,
    created_at_utc: str | None = None,
) -> dict[str, Any]:
    if not source_id or not source_kind:
        raise ValueError("source_id and source_kind are required")
    created_at_utc = created_at_utc or datetime.now(UTC).isoformat()
    config = dict(resolved_config)
    missing = [
        name
        for name, value in (
            ("dataset_id", dataset_id),
            ("split_id", split_id),
            ("code_revision", code_revision),
        )
        if value in (None, "")
    ]
    identity = {
        "created_at_utc": created_at_utc,
        "source_id": source_id,
        "source_sha256": source_sha256,
        "method": method,
        "config_sha256": canonical_sha256(config),
        "model": model,
        "dataset_id": dataset_id,
        "split_id": split_id,
        "random_seed": random_seed,
        "code_revision": code_revision,
    }
    record = {
        "schema_version": SCHEMA_VERSION,
        "run_id": f"run-{canonical_sha256(identity)[:16]}",
        "created_at_utc": created_at_utc,
        "status": "started",
        "provenance_complete": not missing,
        "missing_provenance": missing,
        "code": {"package": "drowsyalert", "version": "0.2.0", "revision": code_revision},
        "environment": {
            "python": platform.python_version(),
            "implementation": platform.python_implementation(),
            "platform": sys.platform,
        },
        "data": {"dataset_id": dataset_id, "split_id": split_id},
        "source": {"id": source_id, "kind": source_kind, "sha256": source_sha256},
        "method": dict(method),
        "config": config,
        "config_sha256": identity["config_sha256"],
        "model": dict(model),
        "random_seed": random_seed,
        "audio": dict(audio),
        "summary": None,
        "frames": [],
        "error": None,
    }
    _assert_json_safe(record)
    return record


def finalize_run_record(
    record: Mapping[str, Any],
    frames: Iterable[Mapping[str, Any]],
    *,
    status: str,
    wall_seconds: float,
    audio: Mapping[str, Any],
    error: str | None = None,
) -> dict[str, Any]:
    if status not in {"completed", "error"}:
        raise ValueError("Run status must be completed or error")
    output = deepcopy(dict(record))
    output["status"] = status
    output["audio"] = dict(audio)
    output["frames"] = [dict(frame) for frame in frames]
    output["summary"] = {
        "frames": len(output["frames"]),
        "wall_seconds": wall_seconds,
        "fps": len(output["frames"]) / wall_seconds if wall_seconds else 0.0,
    }
    output["error"] = error
    _assert_json_safe(output)
    return output


def write_run_record(path: Path, record: Mapping[str, Any]) -> None:
    _assert_json_safe(record)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as destination:
        json.dump(record, destination, indent=2, sort_keys=True)
        destination.write("\n")


def read_run_record(path: Path) -> dict[str, Any]:
    record = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(record, dict) or record.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("Unsupported experiment record schema")
    _assert_json_safe(record)
    return record


def write_frame_csv(path: Path, frames: Iterable[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="") as destination:
        writer = csv.DictWriter(destination, fieldnames=FRAME_FIELDS, extrasaction="raise")
        writer.writeheader()
        for frame in frames:
            _assert_json_safe(frame, "frame")
            writer.writerow(frame)
