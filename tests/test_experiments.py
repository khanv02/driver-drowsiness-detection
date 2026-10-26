import csv
import json

import pytest

from drowsyalert.experiments.records import (
    FRAME_FIELDS,
    build_run_record,
    canonical_sha256,
    finalize_run_record,
    read_run_record,
    write_frame_csv,
    write_run_record,
)


def base_record(**overrides):
    values = {
        "source_id": "clip-001.mp4",
        "source_kind": "video_media",
        "source_sha256": "a" * 64,
        "method": {"method_id": "B", "method": "perclos-yawn"},
        "resolved_config": {"window_seconds": 60.0, "yawn_count": 2},
        "model": {"eye_source": "landmark_ear", "checkpoint_sha256": None},
        "audio": {"enabled": False, "policy": "replay_silent"},
        "dataset_id": "dataset-v1",
        "split_id": "heldout-v1",
        "random_seed": 42,
        "code_revision": "abc123",
        "created_at_utc": "2026-10-26T00:00:00+00:00",
    }
    values.update(overrides)
    return build_run_record(**values)


def test_record_identity_is_deterministic_and_config_changes_are_detected():
    first = base_record()
    second = base_record()
    changed = base_record(resolved_config={"window_seconds": 30.0, "yawn_count": 2})
    assert first["run_id"] == second["run_id"]
    assert first["config_sha256"] == canonical_sha256(first["config"])
    assert changed["run_id"] != first["run_id"]
    assert changed["config_sha256"] != first["config_sha256"]


def test_missing_research_provenance_is_explicit_not_fabricated():
    record = base_record(dataset_id=None, split_id=None, code_revision=None)
    assert not record["provenance_complete"]
    assert record["missing_provenance"] == ["dataset_id", "split_id", "code_revision"]


def test_json_round_trip_and_overwrite_refusal(tmp_path):
    final = finalize_run_record(
        base_record(),
        [{"frame": 0, "timestamp": 0.0, "state": "NORMAL"}],
        status="completed",
        wall_seconds=0.5,
        audio={"enabled": False, "policy": "replay_silent"},
    )
    path = tmp_path / "run.json"
    write_run_record(path, final)
    assert read_run_record(path) == json.loads(json.dumps(final))
    with pytest.raises(FileExistsError):
        write_run_record(path, final)


@pytest.mark.parametrize("key", ["image", "raw_frame", "frame_data", "pixels"])
def test_raw_frame_fields_are_rejected(key):
    with pytest.raises(ValueError, match="Raw frame"):
        finalize_run_record(
            base_record(),
            [{"frame": 0, key: [[1, 2, 3]]}],
            status="completed",
            wall_seconds=1.0,
            audio={},
        )


def test_error_completion_preserves_failure_without_claiming_success():
    result = finalize_run_record(
        base_record(),
        [],
        status="error",
        wall_seconds=0.1,
        audio={"enabled": False},
        error="OSError: camera disconnected",
    )
    assert result["status"] == "error"
    assert result["error"] == "OSError: camera disconnected"
    assert result["summary"]["frames"] == 0


def test_csv_schema_is_stable_and_rejects_extra_fields(tmp_path):
    row = {field: None for field in FRAME_FIELDS}
    row.update(frame=0, timestamp=0.0, state="NORMAL")
    path = tmp_path / "frames.csv"
    write_frame_csv(path, [row])
    with path.open(newline="", encoding="utf-8") as source:
        reader = csv.DictReader(source)
        assert tuple(reader.fieldnames) == FRAME_FIELDS
        assert list(reader)[0]["state"] == "NORMAL"
    with pytest.raises(ValueError):
        write_frame_csv(tmp_path / "invalid.csv", [{**row, "unexpected": 1}])
