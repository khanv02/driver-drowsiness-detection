import csv
import math

import pytest

from drowsyalert.experiments.annotations import (
    ANNOTATION_FIELDS,
    Annotation,
    annotation_manifest_sha256,
    load_annotations_csv,
    validate_annotations,
)


def annotation(**overrides):
    values = {
        "clip_id": "clip-001",
        "subject_group": "subject-01",
        "session_group": "session-01",
        "split": "validation",
        "start_seconds": 2.0,
        "end_seconds": 4.0,
        "label": "drowsy_event",
        "annotation_source": "provider_labels_v1",
        "annotator_id": "provider",
        "adjudication": "not_applicable",
        "confidence": "not_provided",
        "glasses": "unknown",
        "lighting": "unknown",
        "head_movement": "unknown",
    }
    values.update(overrides)
    return Annotation(**values)


def test_valid_annotations_have_order_independent_stable_identity():
    first = annotation()
    second = annotation(
        clip_id="clip-002",
        subject_group="subject-02",
        session_group="session-02",
        start_seconds=5.0,
        end_seconds=7.0,
        label="microsleep",
        glasses="present",
        lighting="low",
        head_movement="present",
    )
    durations = {"clip-001": 10.0, "clip-002": 8.0}
    assert validate_annotations([first, second], durations) == [first, second]
    assert annotation_manifest_sha256([first, second]) == annotation_manifest_sha256(
        [second, first]
    )


@pytest.mark.parametrize(
    ("start", "end", "duration"),
    [(-0.1, 1.0, 5.0), (1.0, 1.0, 5.0), (2.0, 1.0, 5.0), (1.0, 6.0, 5.0)],
)
def test_annotation_times_must_be_ordered_and_inside_media(start, end, duration):
    with pytest.raises(ValueError, match="time"):
        validate_annotations(
            [annotation(start_seconds=start, end_seconds=end)], {"clip-001": duration}
        )


@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf])
def test_annotation_times_and_media_duration_must_be_finite(value):
    with pytest.raises(ValueError, match="finite"):
        validate_annotations([annotation(start_seconds=value)], {"clip-001": 10.0})
    with pytest.raises(ValueError, match="finite"):
        validate_annotations([annotation()], {"clip-001": value})


def test_unknown_clip_duplicate_and_unapproved_label_are_rejected():
    row = annotation()
    with pytest.raises(ValueError, match="duration"):
        validate_annotations([row], {})
    with pytest.raises(ValueError, match="Duplicate"):
        validate_annotations([row, row], {"clip-001": 10.0})
    with pytest.raises(ValueError, match="label"):
        validate_annotations(
            [annotation(label="model_says_drowsy")], {"clip-001": 10.0}
        )


@pytest.mark.parametrize("source", ["drowsyalert", "model_prediction", "perclos_output"])
def test_algorithm_outputs_cannot_be_reference_annotation_sources(source):
    with pytest.raises(ValueError, match="independent"):
        validate_annotations(
            [annotation(annotation_source=source)], {"clip-001": 10.0}
        )


def test_pending_adjudication_is_not_final_evaluation_evidence():
    draft = annotation(adjudication="pending")
    assert validate_annotations([draft], {"clip-001": 10.0}, require_final=False)
    with pytest.raises(ValueError, match="final adjudication"):
        validate_annotations([draft], {"clip-001": 10.0})


@pytest.mark.parametrize("group_field", ["subject_group", "session_group"])
def test_subject_or_session_group_cannot_cross_splits(group_field):
    other = {
        "clip_id": "clip-002",
        "subject_group": "subject-02",
        "session_group": "session-02",
        "split": "test",
    }
    other[group_field] = getattr(annotation(), group_field)
    with pytest.raises(ValueError, match="split leakage"):
        validate_annotations(
            [annotation(), annotation(**other)],
            {"clip-001": 10.0, "clip-002": 10.0},
        )


def test_csv_loader_has_strict_stable_columns_and_parses_numbers(tmp_path):
    path = tmp_path / "annotations.csv"
    values = annotation().as_dict()
    with path.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=ANNOTATION_FIELDS)
        writer.writeheader()
        writer.writerow(values)
    loaded = load_annotations_csv(path)
    assert loaded == [annotation()]
    assert isinstance(loaded[0].start_seconds, float)

    invalid = tmp_path / "invalid.csv"
    with invalid.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=(*ANNOTATION_FIELDS, "prediction"))
        writer.writeheader()
        writer.writerow({**values, "prediction": "ALERT"})
    with pytest.raises(ValueError, match="columns"):
        load_annotations_csv(invalid)
