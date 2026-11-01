import json
from dataclasses import asdict, replace

import pytest

from drowsyalert.experiments.annotations import Annotation
from drowsyalert.experiments.batch import (
    BatchClip,
    build_batch_plan,
    load_batch_plan,
)
from drowsyalert.experiments.evaluation import EvaluationProtocol
from drowsyalert.experiments.records import (
    build_run_record,
    finalize_run_record,
    write_run_record,
)
from drowsyalert.experiments.replay import (
    SweepAxis,
    config_sha256,
    iter_sweep_configs,
    replay_run_record,
    run_validation_sweep,
)
from drowsyalert.utils.config import Config

METHODS = {
    "A": ("perclos", None),
    "B": ("perclos-yawn", "yawn"),
    "C": ("perclos-head-pose", "head_pose"),
}


def make_config(**overrides):
    config = replace(
        Config(head_pose_reference_degrees=0.0),
        **overrides,
    )
    config.validate()
    return config


def make_record(config, frames, method_id="A"):
    method, cue = METHODS[method_id]
    record = build_run_record(
        source_id="clip-1",
        source_kind="video_media",
        source_sha256="a" * 64,
        method={
            "method_id": method_id,
            "method": method,
            "auxiliary_cue": cue,
            "auxiliary_settings": {},
            "common_settings": {},
            "eye_source": "landmark_ear",
        },
        resolved_config=asdict(config),
        model={"eye_source": "landmark_ear", "checkpoint_sha256": None},
        audio={"enabled": False, "policy": "replay_silent"},
        dataset_id="dataset-v1",
        split_id="split-v1",
        random_seed=42,
        code_revision="abc123",
        created_at_utc="2026-10-27T00:00:00+00:00",
    )
    return finalize_run_record(
        record,
        frames,
        status="completed",
        wall_seconds=1.0,
        audio={"enabled": False, "policy": "replay_silent"},
    )


def frame(index, **overrides):
    values = {
        "frame": index,
        "timestamp": index * 0.1,
        "processing_ms": 1.0,
        "valid": True,
        "observation_reason": "",
        "ear_left": 0.3,
        "ear_right": 0.3,
        "mar": None,
        "pitch": None,
        "eye_state": "OPEN",
        "closed_seconds": 0.0,
        "state": "UNKNOWN",
    }
    values.update(overrides)
    return values


def open_frames(count, **overrides):
    return [frame(index, **overrides) for index in range(count)]


def test_replay_recomputes_eye_state_without_mutating_the_stored_record():
    source = make_config(
        ear_threshold=0.2,
        closed_seconds=0.4,
        window_seconds=10.0,
        min_valid_seconds=1.0,
        min_coverage=0.5,
    )
    frames = open_frames(8)
    record = make_record(source, frames)
    candidate = replace(source, ear_threshold=0.4)

    replayed = replay_run_record(record, candidate)

    assert {item["eye_state"] for item in replayed["frames"]} == {"CLOSED"}
    assert replayed["frames"][-1]["state"] == "ALERT"
    assert record["frames"][0]["eye_state"] == "OPEN"
    assert record["frames"][0]["closed_seconds"] == 0.0
    assert replayed["replay"]["replay_config_sha256"] == config_sha256(candidate)


def test_replay_uses_stored_mouth_observations_for_the_yawn_cue():
    source = make_config(
        window_seconds=10.0,
        min_valid_seconds=1.0,
        min_coverage=0.5,
        yawn_threshold=0.6,
        yawn_seconds=0.5,
        yawn_count=1,
    )
    frames = open_frames(12, mar=0.8)
    record = make_record(source, frames, "B")

    detected = replay_run_record(record, source)
    rejected = replay_run_record(record, replace(source, yawn_threshold=0.9))

    assert detected["frames"][-1]["yawns"] == 1
    assert any(item["yawn_event"] for item in detected["frames"])
    assert rejected["frames"][-1]["yawns"] == 0
    assert not any(item["yawn_event"] for item in rejected["frames"])


def test_replay_rebases_stored_head_pitch_against_the_candidate_reference():
    source = make_config(
        head_pose_reference_degrees=0.0,
        head_down_degrees=20.0,
        head_down_seconds=0.5,
        window_seconds=10.0,
        min_valid_seconds=1.0,
        min_coverage=0.5,
    )
    frames = open_frames(12, pitch=25.0)
    record = make_record(source, frames, "C")

    detected = replay_run_record(record, source)
    rebased = replay_run_record(record, replace(source, head_pose_reference_degrees=10.0))

    assert detected["frames"][-1]["head_down"] is True
    assert detected["frames"][-1]["pitch"] == pytest.approx(25.0)
    assert rebased["frames"][-1]["head_down"] is False
    assert rebased["frames"][-1]["pitch"] == pytest.approx(15.0)


def test_bounded_sweep_is_deterministic_and_skips_invalid_configurations():
    base = make_config()
    axes = (
        SweepAxis("window_seconds", (10.0, 40.0)),
        SweepAxis("min_valid_seconds", (30.0, 5.0)),
        SweepAxis("ear_threshold", (0.2, 0.3)),
    )
    first = [
        config_sha256(item)
        for item in iter_sweep_configs(base, axes=axes, max_candidates=8)
    ]
    second = [
        config_sha256(item)
        for item in iter_sweep_configs(base, axes=axes, max_candidates=8)
    ]

    assert len(first) == 6
    assert len(set(first)) == 6
    assert first == second
    with pytest.raises(ValueError, match="max_candidates"):
        list(iter_sweep_configs(base, axes=axes, max_candidates=7))


def test_plan_json_loader_round_trips(tmp_path):
    config = make_config()
    plan = build_batch_plan(
        dataset_id="dataset-v1",
        split_id="split-v1",
        manifest_sha256="b" * 64,
        code_revision="abc123",
        random_seed=42,
        partition="validation",
        eye_source="landmark_ear",
        resolved_config=asdict(config),
        clips=[BatchClip("clip-1", "clip.mp4", "a" * 64, 2.0, "validation")],
    )
    path = tmp_path / "batch-plan.json"
    path.write_text(json.dumps(plan.as_dict()), encoding="utf-8")

    assert load_batch_plan(path) == plan


def test_validation_sweep_runs_from_stored_records_and_reports_hashes(tmp_path):
    config = make_config(
        window_seconds=2.0,
        min_valid_seconds=0.5,
        min_coverage=0.5,
        closed_seconds=2.0,
    )
    plan = build_batch_plan(
        dataset_id="dataset-v1",
        split_id="split-v1",
        manifest_sha256="b" * 64,
        code_revision="abc123",
        random_seed=42,
        partition="validation",
        eye_source="landmark_ear",
        resolved_config=asdict(config),
        clips=[BatchClip("clip-1", "clip.mp4", "a" * 64, 2.0, "validation")],
    )
    frames = open_frames(20, mar=0.8, pitch=25.0)
    for method_id in METHODS:
        record = make_record(config, frames, method_id)
        write_run_record(tmp_path / "runs" / method_id / "clip-1.json", record)
    annotations = [
        Annotation(
            clip_id="clip-1",
            subject_group="group-1",
            session_group="session-1",
            split="validation",
            start_seconds=0.5,
            end_seconds=1.0,
            label="microsleep",
            annotation_source="independent_human_review",
            annotator_id="reviewer-1",
            adjudication="single_reviewer",
            confidence="not_provided",
            glasses="unknown",
            lighting="unknown",
            head_movement="unknown",
        )
    ]
    protocol = EvaluationProtocol(
        early_tolerance=1.0,
        late_tolerance=2.0,
        bin_seconds=1.0,
        positive_fraction=0.5,
        reference_labels=frozenset({"microsleep"}),
    )

    result = run_validation_sweep(
        plan,
        output_root=tmp_path,
        annotations=annotations,
        protocol=protocol,
        base_config=config,
        axes=(SweepAxis("ear_threshold", (0.2, 0.3)),),
        max_candidates=2,
    )

    assert result["partition"] == "validation"
    assert len(result["candidates"]) == 2
    assert set(result["candidates"][0]["methods"]) == {"A", "B", "C"}
    assert len(result["sweep_sha256"]) == 64
    assert result["annotations_sha256"]
    assert result["clip_ids"] == ["clip-1"]


def test_validation_sweep_refuses_test_plans_and_test_annotations(tmp_path):
    config = make_config()
    plan = build_batch_plan(
        dataset_id="dataset-v1",
        split_id="split-v1",
        manifest_sha256="b" * 64,
        code_revision="abc123",
        random_seed=42,
        partition="test",
        eye_source="landmark_ear",
        resolved_config=asdict(config),
        clips=[BatchClip("clip-1", "clip.mp4", "a" * 64, 2.0, "test")],
    )
    protocol = EvaluationProtocol(
        early_tolerance=1.0,
        late_tolerance=2.0,
        bin_seconds=1.0,
        positive_fraction=0.5,
        reference_labels=frozenset({"microsleep"}),
    )

    with pytest.raises(ValueError, match="validation partition"):
        run_validation_sweep(
            plan,
            output_root=tmp_path,
            annotations=[],
            protocol=protocol,
            base_config=config,
        )
