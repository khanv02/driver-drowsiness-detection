import csv

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
