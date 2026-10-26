import csv

import pytest

from drowsyalert.experiments.annotation_review import (
    WORKLIST_FIELDS,
    DraftEvent,
    ReviewClip,
    add_draft_event,
    finalize_annotations,
    load_worklist,
    review_wait_delay_ms,
    write_draft_events,
    write_worklist,
)


def clip(**overrides):
    values = {
        "clip_id": "clip-1",
        "relative_path": "Yawning/Male/HDTV720/clip-1.mp4",
        "duration_seconds": 20.0,
        "source_category": "yawning",
        "sex_group": "male",
    }
    values.update(overrides)
    return ReviewClip(**values)


def test_worklist_is_stable_and_contains_review_gates(tmp_path):
    path = tmp_path / "worklist.csv"
    write_worklist(path, [clip()])
    with path.open(newline="", encoding="utf-8") as source:
        assert tuple(csv.DictReader(source).fieldnames or ()) == WORKLIST_FIELDS
    loaded = load_worklist(path)
    assert loaded == [clip()]
    assert loaded[0].subject_group == "unknown"
    assert loaded[0].split == "unassigned"
    assert loaded[0].review_status == "pending"


def test_review_playback_starts_blocking_and_uses_real_video_fps():
    assert review_wait_delay_ms(25.0, paused=True) == 0
    assert review_wait_delay_ms(25.0, paused=False) == 40
    assert review_wait_delay_ms(24.0, paused=False) == 42
    with pytest.raises(ValueError, match="FPS"):
        review_wait_delay_ms(0.0, paused=False)


def test_draft_events_enforce_labels_media_bounds_and_duplicates(tmp_path):
    events = add_draft_event(
        [],
        clip_id="clip-1",
        start_seconds=2.5,
        end_seconds=4.0,
        label="yawn",
        duration_seconds=20.0,
    )
    assert events == [DraftEvent("clip-1", 2.5, 4.0, "yawn")]
    write_draft_events(tmp_path / "draft.csv", events)
    with pytest.raises(ValueError, match="Duplicate"):
        add_draft_event(
            events,
            clip_id="clip-1",
            start_seconds=2.5,
            end_seconds=4.0,
            label="yawn",
            duration_seconds=20.0,
        )
    with pytest.raises(ValueError, match="bounds"):
        add_draft_event(
            [],
            clip_id="clip-1",
            start_seconds=19.0,
            end_seconds=21.0,
            label="yawn",
            duration_seconds=20.0,
        )
    with pytest.raises(ValueError, match="approved label"):
        add_draft_event(
            [],
            clip_id="clip-1",
            start_seconds=1.0,
            end_seconds=2.0,
            label="model_alert",
            duration_seconds=20.0,
        )


def test_final_export_requires_review_and_assigned_split():
    event = DraftEvent("clip-1", 2.5, 4.0, "yawn")
    kwargs = {
        "annotation_source": "independent_human_review",
        "annotator_id": "reviewer-1",
        "adjudication": "single_reviewer",
        "confidence": "high",
    }
    with pytest.raises(ValueError, match="not final"):
        finalize_annotations([event], [clip()], **kwargs)
    with pytest.raises(ValueError, match="not assigned"):
        finalize_annotations([event], [clip(review_status="reviewed")], **kwargs)


def test_final_export_uses_strict_annotation_contract_and_detects_group_leakage():
    events = [
        DraftEvent("clip-1", 2.5, 4.0, "yawn"),
        DraftEvent("clip-2", 6.0, 8.0, "microsleep"),
    ]
    worklist = [
        clip(
            review_status="reviewed",
            split="validation",
            subject_group="subject-1",
            session_group="session-1",
        ),
        clip(
            clip_id="clip-2",
            relative_path="Microsleep/Male/HDTV720/clip-2.mp4",
            source_category="microsleep",
            review_status="reviewed",
            split="validation",
            subject_group="subject-2",
            session_group="session-2",
        ),
    ]
    rows = finalize_annotations(
        events,
        worklist,
        annotation_source="independent_human_review",
        annotator_id="reviewer-1",
        adjudication="single_reviewer",
        confidence="high",
    )
    assert [row.label for row in rows] == ["yawn", "microsleep"]
    assert all(row.annotation_source == "independent_human_review" for row in rows)

    leaked_values = {
        **worklist[1].as_dict(),
        "subject_group": "subject-1",
        "split": "test",
    }
    leaked = [worklist[0], ReviewClip(**leaked_values)]
    with pytest.raises(ValueError, match="subject split leakage"):
        finalize_annotations(
            events,
            leaked,
            annotation_source="independent_human_review",
            annotator_id="reviewer-1",
            adjudication="single_reviewer",
            confidence="high",
        )
