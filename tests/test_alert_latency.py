import pytest

from drowsyalert.experiments.annotations import Annotation
from drowsyalert.experiments.evaluation import EvaluationProtocol, evaluate_method_runs


def annotation(**overrides):
    values = {
        "clip_id": "clip-1",
        "subject_group": "subject-1",
        "session_group": "session-1",
        "split": "validation",
        "start_seconds": 1.0,
        "end_seconds": 2.0,
        "label": "microsleep",
        "annotation_source": "independent_human_review",
        "annotator_id": "reviewer-1",
        "adjudication": "single_reviewer",
        "confidence": "high",
        "glasses": "unknown",
        "lighting": "low",
        "head_movement": "unknown",
    }
    values.update(overrides)
    return Annotation(**values)


def run_record(clip_id="clip-1", method_id="A", frames=None, status="completed"):
    if frames is None:
        frames = [
            {
                "timestamp": 0.0,
                "state": "NORMAL",
                "reason": "below_threshold",
                "processing_ms": 10.0,
            },
            {
                "timestamp": 1.0,
                "state": "ALERT",
                "reason": "prolonged_closure",
                "processing_ms": 20.0,
            },
            {"timestamp": 2.0, "state": "UNKNOWN", "reason": "no_face", "processing_ms": 30.0},
            {
                "timestamp": 3.0,
                "state": "NORMAL",
                "reason": "below_threshold",
                "processing_ms": 40.0,
            },
        ]
    return {
        "schema_version": 1,
        "status": status,
        "source": {"id": clip_id, "kind": "video_media", "sha256": "a" * 64},
        "method": {"method_id": method_id},
        "summary": {"frames": len(frames), "wall_seconds": 1.0, "fps": len(frames)},
        "frames": frames,
    }


def protocol():
    return EvaluationProtocol(
        early_tolerance=1.0,
        late_tolerance=2.0,
        bin_seconds=1.0,
        positive_fraction=0.5,
        reference_labels=frozenset({"microsleep"}),
    )


def test_evaluator_keeps_event_latency_coverage_failure_and_processing_separate():
    result = evaluate_method_runs(
        "A",
        [annotation()],
        {"clip-1": 4.0},
        [run_record()],
        protocol(),
    )

    assert result["clips"] == 1
    assert result["reference_events"] == 1
    assert result["event_metrics"]["tp"] == 1
    assert result["event_metrics"]["fp"] == 0
    assert result["latency"]["values_seconds"] == [0.0]
    assert result["coverage"] == {
        "eligible_seconds": 4.0,
        "valid_seconds": 3.0,
        "unknown_seconds": 1.0,
        "coverage": 0.75,
        "eligible_hours": pytest.approx(4 / 3600),
        "valid_hours": pytest.approx(3 / 3600),
    }
    assert result["system_accuracy"]["accuracy"] == 0.75
    assert result["system_accuracy"]["observed_only_accuracy"] == 1.0
    assert result["observation_failures"] == {"no_face": {"intervals": 1, "seconds": 1.0}}
    assert result["processing"]["frames"] == 4
    assert result["processing"]["mean_processing_ms"] == 25.0
    assert result["processing"]["wall_seconds"] == 1.0


def test_evaluator_reports_condition_counts_without_inventing_missing_tags():
    result = evaluate_method_runs(
        "A", [annotation()], {"clip-1": 4.0}, [run_record()], protocol()
    )
    assert result["condition_counts"] == {
        "glasses": {"unknown": 1},
        "head_movement": {"unknown": 1},
        "lighting": {"low": 1},
    }


def test_evaluator_requires_complete_common_clip_runs_and_matching_method():
    with pytest.raises(ValueError, match="Run clips do not match"):
        evaluate_method_runs(
            "A",
            [annotation()],
            {"clip-1": 4.0, "clip-2": 2.0},
            [run_record()],
            protocol(),
        )
    with pytest.raises(ValueError, match="method"):
        evaluate_method_runs(
            "A", [annotation()], {"clip-1": 4.0}, [run_record(method_id="B")], protocol()
        )


@pytest.mark.parametrize(
    "record, message",
    [
        (run_record(status="error"), "not completed"),
        (run_record(frames=[]), "no frame records"),
        (
            run_record(frames=[{"timestamp": 0.0, "state": "NORMAL", "processing_ms": -1.0}]),
            "processing_ms",
        ),
    ],
)
def test_evaluator_rejects_incomplete_or_invalid_run_evidence(record, message):
    with pytest.raises(ValueError, match=message):
        evaluate_method_runs("A", [annotation()], {"clip-1": 4.0}, [record], protocol())


def test_nonprimary_annotations_do_not_become_reference_events():
    result = evaluate_method_runs(
        "A",
        [annotation(label="yawn")],
        {"clip-1": 4.0},
        [run_record()],
        protocol(),
    )
    assert result["reference_events"] == 0
    assert result["event_metrics"]["tp"] == 0
    assert result["event_metrics"]["fp"] == 1
    assert result["event_metrics"]["recall"] is None
