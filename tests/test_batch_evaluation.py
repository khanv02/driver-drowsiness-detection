import json
from dataclasses import asdict

import pytest

from drowsyalert.experiments.batch import (
    BatchClip,
    batch_plan_sha256,
    build_batch_plan,
    run_batch,
    validate_batch_plan,
)
from drowsyalert.experiments.records import file_sha256
from drowsyalert.utils.config import Config


def clips():
    return [
        BatchClip("clip-b", "Yawning/Male/HDTV720/clip-b.mp4", "b" * 64, 4.0, "validation"),
        BatchClip(
            "clip-a",
            "Microsleep/Female/HDTV720/clip-a.mp4",
            "a" * 64,
            8.0,
            "validation",
        ),
    ]


def plan(**overrides):
    values = {
        "dataset_id": "nitymed-hdtv720",
        "split_id": "validation-v1",
        "manifest_sha256": "c" * 64,
        "code_revision": "abc123",
        "random_seed": 42,
        "partition": "validation",
        "eye_source": "landmark_ear",
        "resolved_config": {
            "ear_threshold": 0.21,
            "closed_seconds": 2.0,
            "max_gap_seconds": 0.25,
            "window_seconds": 60.0,
            "min_valid_seconds": 30.0,
            "min_coverage": 0.8,
            "perclos_threshold": 0.2,
            "combined_perclos_threshold": 0.1,
            "yawn_threshold": 0.6,
            "yawn_seconds": 1.5,
            "yawn_count": 2,
            "head_pose_reference_degrees": 0.0,
            "head_down_degrees": 20.0,
            "head_down_seconds": 1.5,
        },
        "clips": clips(),
    }
    values.update(overrides)
    return build_batch_plan(**values)


def test_plan_fixes_common_clips_eye_source_base_config_and_named_methods():
    result = plan()
    assert [item.clip_id for item in result.clips] == ["clip-a", "clip-b"]
    assert result.eye_source == "landmark_ear"
    assert [(item.method_id, item.method, item.auxiliary_cue) for item in result.methods] == [
        ("A", "perclos", None),
        ("B", "perclos-yawn", "yawn"),
        ("C", "perclos-head-pose", "head_pose"),
    ]
    assert result.shared_config["window_seconds"] == 60.0
    assert result.dataset_id == "nitymed-hdtv720"
    assert result.partition == "validation"


def test_plan_identity_is_stable_and_changes_with_config_or_membership():
    first = plan()
    reordered = plan(clips=list(reversed(clips())))
    changed_values = dict(first.shared_config)
    changed_values["window_seconds"] = 30.0
    changed_config = plan(resolved_config=changed_values)
    changed_clips = plan(clips=clips()[:1])
    assert batch_plan_sha256(first) == batch_plan_sha256(reordered)
    assert batch_plan_sha256(first) != batch_plan_sha256(changed_config)
    assert batch_plan_sha256(first) != batch_plan_sha256(changed_clips)
    json.dumps(first.as_dict(), allow_nan=False)


@pytest.mark.parametrize(
    "overrides, message",
    [
        ({"eye_source": "cnn"}, "landmark_ear"),
        ({"clips": []}, "clip"),
        ({"clips": [clips()[0], clips()[0]]}, "Duplicate clip"),
        ({"clips": [BatchClip("clip", "x.mp4", "a" * 64, 1.0, "test")]}, "partition"),
        ({"manifest_sha256": "bad"}, "manifest SHA-256"),
        ({"code_revision": ""}, "code revision"),
    ],
)
def test_plan_rejects_noncomparable_or_incomplete_inputs(overrides, message):
    with pytest.raises(ValueError, match=message):
        plan(**overrides)


def test_plan_validation_detects_tampered_method_set():
    result = plan()
    object.__setattr__(result, "methods", result.methods[:2])
    with pytest.raises(ValueError, match="A, B, and C"):
        validate_batch_plan(result)


def test_batch_runner_forces_headless_silent_ear_and_resumes_valid_records(tmp_path):
    video_root = tmp_path / "videos"
    video_root.mkdir()
    video = video_root / "clip.mp4"
    video.write_bytes(b"permitted fixture")
    config = Config(head_pose_reference_degrees=0.0)
    result_plan = build_batch_plan(
        dataset_id="dataset-v1",
        split_id="validation-v1",
        manifest_sha256="c" * 64,
        code_revision="abc123",
        random_seed=42,
        partition="validation",
        eye_source="landmark_ear",
        resolved_config=asdict(config),
        clips=[
            BatchClip("clip", "clip.mp4", file_sha256(video), 1.0, "validation")
        ],
    )
    calls = []

    def fake_runner(_config, **kwargs):
        calls.append(kwargs)
        assert kwargs["headless"] is True
        assert kwargs["mute"] is True
        assert kwargs["backend"] == "ear"
        assert kwargs["source_id"] == "clip"
        method_id = {"perclos": "A", "perclos-yawn": "B", "perclos-head-pose": "C"}[
            kwargs["method"]
        ]
        record = {
            "schema_version": 1,
            "status": "completed",
            "source": {"id": "clip", "sha256": file_sha256(video)},
            "method": {"method_id": method_id},
            "model": {"eye_source": "landmark_ear"},
            "audio": {"enabled": False},
        }
        kwargs["record_path"].write_text(json.dumps(record), encoding="utf-8")

    output = tmp_path / "results"
    first = run_batch(
        result_plan,
        config=config,
        video_root=video_root,
        output_root=output,
        runner=fake_runner,
    )
    second = run_batch(
        result_plan,
        config=config,
        video_root=video_root,
        output_root=output,
        runner=fake_runner,
    )
    assert len(calls) == 3
    assert len(first["completed"]) == 3 and not first["failed"]
    assert len(second["skipped"]) == 3 and not second["failed"]
    assert (output / "batch-plan.json").is_file()
