import json

import pytest

from drowsyalert.experiments.batch import (
    BatchClip,
    batch_plan_sha256,
    build_batch_plan,
    validate_batch_plan,
)


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
            "window_seconds": 60.0,
            "perclos_threshold": 0.2,
            "combined_perclos_threshold": 0.1,
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
    changed_config = plan(
        resolved_config={
            "window_seconds": 30.0,
            "perclos_threshold": 0.2,
            "combined_perclos_threshold": 0.1,
        }
    )
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
