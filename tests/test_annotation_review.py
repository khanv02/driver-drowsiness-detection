import csv

import pytest

from drowsyalert.experiments.annotation_review import (
    WORKLIST_FIELDS,
    DraftEvent,
    ReviewClip,
    add_draft_event,
    build_evaluation_worklist,
    build_review_schedule,
    finalize_annotations,
    load_worklist,
    review_wait_delay_ms,
    write_draft_events,
    write_worklist,
)
from drowsyalert.experiments.split import SplitAssignment
from drowsyalert.experiments.video_manifest import VideoManifestRow


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


def manifest_row(clip_id, category, digest):
    return VideoManifestRow(
        clip_id=clip_id,
        relative_path=f"{category}/Male/HDTV720/{clip_id}.mp4",
        sha256=digest,
        source_id="nitymed-hdtv720",
        source_category=category,
        sex_group="male",
        subject_group="unknown",
        session_group="unknown",
        split="unassigned",
        temporal_ground_truth="absent",
        duration_seconds=10.0,
        fps=25.0,
        width=1280,
        height=720,
        frame_count=250,
        size_bytes=100,
        decodable=True,
        license_id="CC-BY",
        retrieval_date="2026-10-26",
    )


def split_row(source, split):
    return SplitAssignment(
        source.clip_id,
        source.relative_path,
        source.sha256,
        source.source_category,
        source.sex_group,
        split,
        False,
        42,
        1,
    )


def test_evaluation_worklist_preserves_reviewed_pilot_and_frozen_split():
    first = manifest_row("micro-reviewed", "microsleep", "a" * 64)
    second = manifest_row("yawn-pending", "yawning", "b" * 64)
    preserved = ReviewClip(
        first.clip_id,
        first.relative_path,
        first.duration_seconds,
        first.source_category,
        first.sex_group,
        split="validation",
        review_status="reviewed",
    )
    rows = build_evaluation_worklist(
        [first, second],
        [split_row(first, "validation"), split_row(second, "test")],
        preserved_reviews=[preserved],
    )
    by_id = {row.clip_id: row for row in rows}
    assert by_id["micro-reviewed"].review_status == "reviewed"
    assert by_id["micro-reviewed"].split == "validation"
    assert by_id["yawn-pending"].review_status == "pending"
    assert by_id["yawn-pending"].split == "test"


def test_review_schedule_puts_validation_first_and_balances_four_clip_batches():
    rows = []
    for split in ("validation", "test"):
        for category in ("microsleep", "yawning"):
            for index in range(3):
                rows.append(
                    ReviewClip(
                        f"{split}-{category}-{index}",
                        f"{category}/Male/HDTV720/{index}.mp4",
                        10.0,
                        category,
                        "male",
                        split=split,
                    )
                )
    schedule = build_review_schedule(rows, batch_size=4)
    assert [row.stage for row in schedule[:6]] == ["validation"] * 6
    assert [row.source_category for row in schedule[:4]] == [
        "microsleep",
        "yawning",
        "microsleep",
        "yawning",
    ]
    assert {row.batch_id for row in schedule[:4]} == {"validation-01"}
    assert schedule[6].stage == "test"
