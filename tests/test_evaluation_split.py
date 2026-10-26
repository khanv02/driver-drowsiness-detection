from dataclasses import replace

import pytest

from drowsyalert.experiments.split import (
    SPLIT_FIELDS,
    build_balanced_clip_split,
    load_split_manifest,
    split_manifest_sha256,
    write_split_manifest,
)
from drowsyalert.experiments.video_manifest import VideoManifestRow


def video(index: int, category: str) -> VideoManifestRow:
    clip_id = f"{category}-{index:03d}"
    digest = f"{index + (0 if category == 'microsleep' else 1000):064x}"
    return VideoManifestRow(
        clip_id=clip_id,
        relative_path=f"{category}/Male/HDTV720/{clip_id}.mp4",
        sha256=digest,
        source_id="nitymed-hdtv720",
        source_category=category,
        sex_group="male" if index % 2 == 0 else "female",
        subject_group="unknown",
        session_group="unknown",
        split="unassigned",
        temporal_ground_truth="absent",
        duration_seconds=120.0 if category == "microsleep" else 25.0,
        fps=25.0,
        width=1280,
        height=720,
        frame_count=3000 if category == "microsleep" else 625,
        size_bytes=100,
        decodable=True,
        license_id="CC-BY",
        retrieval_date="2026-10-26",
    )


def corpus():
    return [
        *[video(index, "microsleep") for index in range(19)],
        *[video(index, "yawning") for index in range(30)],
    ]


def build(rows=None, locked=None):
    return build_balanced_clip_split(
        corpus() if rows is None else rows,
        validation_per_category=6,
        test_per_category=13,
        locked_validation_ids=(
            {
                "microsleep-000",
                "microsleep-001",
                "yawning-000",
                "yawning-001",
            }
            if locked is None
            else locked
        ),
        seed=42,
    )


def test_balanced_split_has_exact_counts_and_locks_viewed_clips_to_validation():
    rows = build()
    counts = {}
    for row in rows:
        counts[(row.split, row.source_category)] = (
            counts.get((row.split, row.source_category), 0) + 1
        )
    assert counts == {
        ("validation", "microsleep"): 6,
        ("validation", "yawning"): 6,
        ("test", "microsleep"): 13,
        ("test", "yawning"): 13,
    }
    locked = {row.clip_id for row in rows if row.locked_validation}
    assert locked == {
        "microsleep-000",
        "microsleep-001",
        "yawning-000",
        "yawning-001",
    }
    assert all(row.split == "validation" for row in rows if row.locked_validation)
    assert {row.clip_id for row in rows if row.source_category == "microsleep"} == {
        f"microsleep-{index:03d}" for index in range(19)
    }
    for category in ("microsleep", "yawning"):
        validation_sexes = [
            row.sex_group
            for row in rows
            if row.source_category == category and row.split == "validation"
        ]
        assert validation_sexes.count("male") == 3
        assert validation_sexes.count("female") == 3
    yawning_test_sexes = [
        row.sex_group
        for row in rows
        if row.source_category == "yawning" and row.split == "test"
    ]
    assert abs(yawning_test_sexes.count("male") - yawning_test_sexes.count("female")) == 1


def test_split_is_deterministic_under_input_reordering_and_has_stable_identity():
    first = build()
    second = build(list(reversed(corpus())))
    assert first == second
    assert split_manifest_sha256(first) == split_manifest_sha256(second)
    changed = build_balanced_clip_split(
        corpus(),
        validation_per_category=6,
        test_per_category=13,
        locked_validation_ids={
            "microsleep-000",
            "microsleep-001",
            "yawning-000",
            "yawning-001",
        },
        seed=43,
    )
    assert split_manifest_sha256(first) != split_manifest_sha256(changed)


def test_split_csv_round_trip_preserves_versioned_columns(tmp_path):
    rows = build()
    path = tmp_path / "split.csv"
    write_split_manifest(path, rows)
    assert load_split_manifest(path) == rows
    assert tuple(path.read_text(encoding="utf-8").splitlines()[0].split(",")) == SPLIT_FIELDS


def test_split_rejects_duplicate_clip_or_content_hash():
    rows = corpus()
    with pytest.raises(ValueError, match="Duplicate clip"):
        build([*rows, rows[0]])
    duplicated = replace(rows[-1], sha256=rows[0].sha256)
    with pytest.raises(ValueError, match="Duplicate content"):
        build([*rows[:-1], duplicated])


def test_split_rejects_unknown_or_excess_locked_validation_membership():
    with pytest.raises(ValueError, match="Unknown locked"):
        build(locked={"missing"})
    with pytest.raises(ValueError, match="Too many locked"):
        build(locked={f"microsleep-{index:03d}" for index in range(7)})


def test_split_rejects_insufficient_category_membership():
    rows = [row for row in corpus() if row.source_category == "yawning"]
    with pytest.raises(ValueError, match="microsleep"):
        build(rows, locked={"yawning-000", "yawning-001"})
