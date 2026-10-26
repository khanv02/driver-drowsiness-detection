import csv
import json

import numpy as np
import pytest

torch = pytest.importorskip("torch")

from drowsyalert.models.eye_cnn import EyeCNN, load_checkpoint  # noqa: E402
from drowsyalert.models.train import set_determinism, train  # noqa: E402


def test_manifest_rejects_group_leakage(tmp_path):
    from drowsyalert.models.dataset import MANIFEST_FIELDS, read_manifest

    manifest = tmp_path / "manifest.csv"
    with manifest.open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, MANIFEST_FIELDS)
        writer.writeheader()
        for index, split in enumerate(("train", "val", "test")):
            for label in (0, 1):
                writer.writerow(
                    {
                        "path": f"images/{split}-{label}.png",
                        "label": label,
                        "group_id": "leaked" if index < 2 and label == 0 else f"g-{split}-{label}",
                        "source": f"{split}/{label}.png",
                        "source_sha256": "a" * 64,
                        "sha256": "b" * 64,
                        "split": split,
                    }
                )
    with pytest.raises(ValueError, match="appears in both"):
        read_manifest(manifest)


def test_deterministic_seed_resets_python_numpy_and_torch():
    set_determinism(73)
    first_numpy = np.random.random(3)
    first_torch = torch.rand(3)
    set_determinism(73)
    assert np.array_equal(first_numpy, np.random.random(3))
    assert torch.equal(first_torch, torch.rand(3))


def test_training_selects_checkpoint_on_validation_only(tmp_path, monkeypatch):
    import drowsyalert.models.train as training

    requested_splits = []

    class TinyDataset(torch.utils.data.Dataset):
        def __init__(self, manifest, split, augment=False):
            requested_splits.append((split, augment))

        def __len__(self):
            return 4

        def __getitem__(self, index):
            return torch.full((3, 64, 64), index / 4), index % 2

    scores = iter((0.70, 0.60))

    def fake_measure(model, loader, device):
        score = next(scores)
        return {"accuracy": score, "macro_f1": score}

    monkeypatch.setattr(training, "EyeDataset", TinyDataset)
    monkeypatch.setattr(training, "measure", fake_measure)
    manifest = tmp_path / "manifest.csv"
    manifest.write_text("synthetic manifest\n", encoding="utf-8")
    checkpoint = tmp_path / "model.pt"
    output = tmp_path / "run"

    result = train(
        manifest,
        checkpoint,
        output,
        epochs=2,
        batch_size=2,
        patience=2,
        seed=11,
        device="cpu",
    )

    assert requested_splits == [("train", True), ("val", False)]
    assert result["selected_by"] == "validation_macro_f1"
    assert result["best_epoch"] == 1
    assert result["best_validation_macro_f1"] == pytest.approx(0.70)
    assert "test" not in json.dumps(result).lower()
    _, saved = load_checkpoint(checkpoint)
    assert saved["metadata"]["selected_by"] == "validation_macro_f1"
    assert saved["metadata"]["seed"] == 11
    run_config = json.loads((output / "run_config.json").read_text())
    assert run_config["seed"] == 11
    assert run_config["deterministic_algorithms"] is True
    assert json.loads((output / "history.json").read_text())[-1]["epoch"] == 2


def test_checkpoint_keeps_class_and_preprocessing_contract(tmp_path):
    from drowsyalert.models.eye_cnn import save_checkpoint

    path = tmp_path / "model.pt"
    save_checkpoint(path, EyeCNN(), seed=4, selected_by="validation_macro_f1")
    _, checkpoint = load_checkpoint(path)
    assert checkpoint["class_names"] == ["open", "closed"]
    assert checkpoint["image_size"] == 64
    assert checkpoint["metadata"] == {"seed": 4, "selected_by": "validation_macro_f1"}
