import csv
from pathlib import Path

import pytest

from drowsyalert.experiments.video_manifest import (
    VIDEO_MANIFEST_FIELDS,
    VideoMetadata,
    build_nitymed_manifest,
    video_manifest_sha256,
    write_video_manifest,
)


def _video(root: Path, category: str, sex: str, name: str, content: bytes) -> Path:
    path = root / category / sex / "HDTV720" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    return path


def _probe(path: Path) -> VideoMetadata:
    fps = 24.0 if path.name == "clip-24fps.mp4" else 25.0
    return VideoMetadata(
        duration_seconds=4.0,
        fps=fps,
        width=1280,
        height=720,
        frame_count=int(4 * fps),
        decodable=True,
    )


def _hash(path: Path) -> str:
    return {b"a": "a" * 64, b"b": "b" * 64, b"c": "c" * 64}[path.read_bytes()]


def test_manifest_is_privacy_safe_and_records_source_categories_without_event_labels(tmp_path):
    first = _video(tmp_path, "Yawning", "Male", "clip-a.mp4", b"a")
    _video(tmp_path, "Microsleep", "Female", "clip-b.mp4", b"b")

    rows = build_nitymed_manifest(
        tmp_path,
        retrieval_date="2026-10-26",
        probe_video=_probe,
        hash_file=_hash,
    )

    assert [row.clip_id for row in rows] == ["clip-a", "clip-b"]
    assert rows[0].relative_path == first.relative_to(tmp_path).as_posix()
    assert rows[0].source_category == "yawning"
    assert rows[1].source_category == "microsleep"
    assert rows[0].sex_group == "male"
    assert rows[0].subject_group == "unknown"
    assert rows[0].session_group == "unknown"
    assert rows[0].split == "unassigned"
    assert rows[0].temporal_ground_truth == "absent"
    assert rows[0].source_id == "nitymed-hdtv720"
    assert rows[0].license_id == "CC-BY"
    assert rows[0].retrieval_date == "2026-10-26"
    assert not Path(rows[0].relative_path).is_absolute()


def test_manifest_records_real_media_properties_including_nonstandard_fps(tmp_path):
    _video(tmp_path, "Yawning", "Male", "clip-24fps.mp4", b"a")
    row = build_nitymed_manifest(
        tmp_path,
        retrieval_date="2026-10-26",
        probe_video=_probe,
        hash_file=_hash,
    )[0]

    assert row.duration_seconds == 4.0
    assert row.fps == 24.0
    assert row.width == 1280 and row.height == 720
    assert row.frame_count == 96
    assert row.decodable
    assert row.size_bytes == 1


def test_manifest_identity_and_csv_are_stable(tmp_path):
    _video(tmp_path, "Microsleep", "Male", "clip-b.mp4", b"b")
    _video(tmp_path, "Yawning", "Female", "clip-a.mp4", b"a")
    rows = build_nitymed_manifest(
        tmp_path,
        retrieval_date="2026-10-26",
        probe_video=_probe,
        hash_file=_hash,
    )

    assert video_manifest_sha256(rows) == video_manifest_sha256(reversed(rows))
    destination = tmp_path / "manifest.csv"
    write_video_manifest(destination, rows)
    with destination.open(newline="", encoding="utf-8") as source:
        reader = csv.DictReader(source)
        assert tuple(reader.fieldnames or ()) == VIDEO_MANIFEST_FIELDS
        assert [item["clip_id"] for item in reader] == ["clip-a", "clip-b"]


def test_duplicate_content_or_clip_identity_is_rejected(tmp_path):
    _video(tmp_path, "Yawning", "Male", "same.mp4", b"a")
    _video(tmp_path, "Yawning", "Female", "different.mp4", b"a")
    with pytest.raises(ValueError, match="Duplicate video content"):
        build_nitymed_manifest(
            tmp_path,
            retrieval_date="2026-10-26",
            probe_video=_probe,
            hash_file=_hash,
        )

    (tmp_path / "Yawning" / "Female" / "HDTV720" / "different.mp4").unlink()
    _video(tmp_path, "Microsleep", "Female", "same.mp4", b"b")
    with pytest.raises(ValueError, match="Duplicate clip ID"):
        build_nitymed_manifest(
            tmp_path,
            retrieval_date="2026-10-26",
            probe_video=_probe,
            hash_file=_hash,
        )


def test_unexpected_layout_and_bad_media_are_rejected(tmp_path):
    _video(tmp_path, "Other", "Male", "clip.mp4", b"a")
    with pytest.raises(ValueError, match="Unsupported NITYMED path"):
        build_nitymed_manifest(
            tmp_path,
            retrieval_date="2026-10-26",
            probe_video=_probe,
            hash_file=_hash,
        )

    bad_root = tmp_path / "bad"
    _video(bad_root, "Yawning", "Male", "bad.mp4", b"c")

    def bad_probe(_path: Path) -> VideoMetadata:
        return VideoMetadata(0.0, 0.0, 0, 0, 0, False)

    with pytest.raises(ValueError, match="not decodable"):
        build_nitymed_manifest(
            bad_root,
            retrieval_date="2026-10-26",
            probe_video=bad_probe,
            hash_file=_hash,
        )


def test_empty_corpus_is_rejected(tmp_path):
    with pytest.raises(ValueError, match="No MP4 videos"):
        build_nitymed_manifest(
            tmp_path,
            retrieval_date="2026-10-26",
            probe_video=_probe,
            hash_file=_hash,
        )
