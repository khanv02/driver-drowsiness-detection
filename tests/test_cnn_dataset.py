import csv
import hashlib
import json

import cv2
import numpy as np
import pytest

torch = pytest.importorskip("torch")

from drowsyalert.models.eye_cnn import (  # noqa: E402
    CNNBackend,
    EyeCNN,
    load_checkpoint,
    preprocess_eye,
    save_checkpoint,
)
from drowsyalert.types import FaceObservation  # noqa: E402


def test_preprocessing_and_checkpoint_round_trip(tmp_path):
    torch.set_num_threads(2)
    image = np.zeros((20, 30, 3), dtype=np.uint8)
    image[:, :, 0] = 255  # Blue BGR must become the blue RGB channel.
    tensor = preprocess_eye(image)
    assert tensor.shape == (3, 64, 64)
    assert tensor[0].sum() == 0 and tensor[2].min() == 1
    model = EyeCNN().eval()
    checkpoint = tmp_path / "eye.pt"
    save_checkpoint(checkpoint, model)
    loaded, metadata = load_checkpoint(checkpoint)
    with torch.inference_mode():
        assert torch.allclose(model(tensor.unsqueeze(0)), loaded(tensor.unsqueeze(0)))
    assert metadata["class_names"] == ["open", "closed"]
    prediction = CNNBackend(checkpoint).predict(FaceObservation(True, eye_crops=(image, image)))
    assert len(prediction.probabilities) == 2


def test_incompatible_checkpoint_is_rejected(tmp_path):
    checkpoint = tmp_path / "bad.pt"
    torch.save({"architecture": "Other"}, checkpoint)
    with pytest.raises(ValueError):
        load_checkpoint(checkpoint)


def test_dataset_splits_are_disjoint_and_duplicates_stay_together(tmp_path):
    pytest.importorskip("sklearn")
    from drowsyalert.models.dataset import prepare

    raw, processed = tmp_path / "raw", tmp_path / "processed"
    for label in ("Open", "Closed"):
        (raw / label).mkdir(parents=True)
        for index in range(16):
            seed = index + (100 if label == "Closed" else 0)
            image = np.random.default_rng(seed).integers(0, 256, (64, 64, 3), dtype=np.uint8)
            cv2.imwrite(str(raw / label / f"{index}.png"), image)
    duplicate = cv2.imread(str(raw / "Open/0.png"))
    cv2.imwrite(str(raw / "Open/duplicate.png"), duplicate)
    result = prepare(raw, processed)
    assert result["images"] == 32
    with (processed / "manifest.csv").open() as source:
        rows = list(csv.DictReader(source))
    groups = {
        split: {r["group_id"] for r in rows if r["split"] == split}
        for split in ("train", "val", "test")
    }
    assert not groups["train"] & groups["test"]
    assert not groups["train"] & groups["val"]
    assert not groups["val"] & groups["test"]
    for split in groups:
        assert {r["label"] for r in rows if r["split"] == split} == {"0", "1"}

    assert result["schema_version"] == 1
    assert result["class_names"] == {"0": "open", "1": "closed"}
    assert result["identity_separation"] is False
    assert result["warnings"]
    manifest_bytes = (processed / "manifest.csv").read_bytes()
    assert result["manifest_sha256"] == hashlib.sha256(manifest_bytes).hexdigest()
    assert set(rows[0]) == {
        "path",
        "label",
        "group_id",
        "source",
        "source_sha256",
        "sha256",
        "split",
    }


def test_preparation_is_deterministic_and_reports_provenance(tmp_path):
    pytest.importorskip("sklearn")
    from drowsyalert.models.dataset import prepare

    raw = tmp_path / "raw"
    for label in ("Open", "Closed"):
        (raw / label).mkdir(parents=True)
        for index in range(18):
            seed = index + (100 if label == "Closed" else 0)
            image = np.random.default_rng(seed).integers(0, 256, (30, 40, 3), dtype=np.uint8)
            cv2.imwrite(str(raw / label / f"{index}.png"), image)

    first = prepare(raw, tmp_path / "first", seed=9, dataset_name="synthetic")
    second = prepare(raw, tmp_path / "second", seed=9, dataset_name="synthetic")
    assert (tmp_path / "first/manifest.csv").read_bytes() == (
        tmp_path / "second/manifest.csv"
    ).read_bytes()
    assert first["splits"] == second["splits"]
    assert first["dataset"] == "synthetic"
    assert first["transformations"] == ["decode_bgr", "resize_64x64"]
    assert sum(item["images"] for item in first["splits"].values()) == first["images"]
    assert json.loads((tmp_path / "first/dataset.json").read_text()) == first


def test_ambiguous_labels_and_conflicting_duplicates_are_rejected(tmp_path):
    pytest.importorskip("sklearn")
    from drowsyalert.models.dataset import label_from_path, prepare

    ambiguous = tmp_path / "Open/Closed/image.png"
    with pytest.raises(ValueError, match="Ambiguous eye-state label"):
        label_from_path(ambiguous, tmp_path)

    raw = tmp_path / "raw"
    (raw / "Open").mkdir(parents=True)
    (raw / "Closed").mkdir(parents=True)
    image = np.full((20, 20, 3), 127, dtype=np.uint8)
    cv2.imwrite(str(raw / "Open/same.png"), image)
    cv2.imwrite(str(raw / "Closed/same.png"), image)
    with pytest.raises(ValueError, match="Conflicting labels"):
        prepare(raw, tmp_path / "processed")


def test_group_manifest_is_strict_and_preserves_identity_groups(tmp_path):
    pytest.importorskip("sklearn")
    from drowsyalert.models.dataset import prepare

    raw = tmp_path / "raw"
    rows = []
    for label in ("Open", "Closed"):
        (raw / label).mkdir(parents=True)
        for index in range(18):
            source = f"{label}/{index}.png"
            image = np.random.default_rng(index + (100 if label == "Closed" else 0)).integers(
                0, 256, (32, 32, 3), dtype=np.uint8
            )
            cv2.imwrite(str(raw / source), image)
            rows.append({"source": source, "group_id": f"person-{index}"})

    incomplete = tmp_path / "incomplete.csv"
    with incomplete.open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, ["source", "group_id"])
        writer.writeheader()
        writer.writerows(rows[:-1])
    with pytest.raises(ValueError, match="Missing group_id"):
        prepare(raw, tmp_path / "bad", group_csv=incomplete)

    groups = tmp_path / "groups.csv"
    with groups.open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, ["source", "group_id"])
        writer.writeheader()
        writer.writerows(rows)
    result = prepare(raw, tmp_path / "good", group_csv=groups)
    assert result["identity_separation"] is True
    assert not result["warnings"]


def test_cew_folders_are_labeled_and_paired_eyes_stay_in_one_split(tmp_path):
    pytest.importorskip("sklearn")
    from drowsyalert.models.dataset import prepare

    raw = tmp_path / "dataset_B_Eye_Images"
    folders = {
        "openLeftEyes": (0, "L"),
        "openRightEyes": (0, "R"),
        "closedLeftEyes": (1, "L"),
        "closedRightEyes": (1, "R"),
    }
    for folder, (label, side) in folders.items():
        (raw / folder).mkdir(parents=True)
        for index in range(20):
            seed = index + label * 100
            image = np.random.default_rng(seed).integers(0, 256, (24, 24, 3), dtype=np.uint8)
            cv2.imwrite(str(raw / folder / f"subject_{label}_{index:02d}_{side}.jpg"), image)

    result = prepare(
        raw,
        tmp_path / "processed",
        dataset_name="CEW",
        group_strategy="cew-paired-eyes",
    )
    with (tmp_path / "processed/manifest.csv").open(encoding="utf-8", newline="") as source:
        rows = list(csv.DictReader(source))
    by_group = {}
    for row in rows:
        by_group.setdefault(row["group_id"], set()).add(row["split"])
    assert len(rows) == 40  # Exact left/right synthetic copies are deduplicated.
    assert all(len(splits) == 1 for splits in by_group.values())
    assert {row["label"] for row in rows} == {"0", "1"}
    assert result["paired_eye_separation"] is True
    assert result["identity_separation"] is False
    assert len(result["input_tree_sha256"]) == 64
