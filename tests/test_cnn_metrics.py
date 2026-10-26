import hashlib
import json

import pytest

torch = pytest.importorskip("torch")

from drowsyalert.experiments.eye_classifier import (  # noqa: E402
    classification_metrics,
    evaluate,
)


def test_known_confusion_matrix_and_per_class_metrics():
    metrics = classification_metrics([0, 0, 0, 1, 1], [0, 1, 0, 1, 0])
    assert metrics["images"] == 5
    assert metrics["accuracy"] == pytest.approx(0.6)
    assert metrics["confusion_matrix"] == [[2, 1], [1, 1]]
    assert metrics["per_class"]["open"] == {
        "precision": pytest.approx(2 / 3),
        "recall": pytest.approx(2 / 3),
        "f1": pytest.approx(2 / 3),
        "support": 3,
    }
    assert metrics["per_class"]["closed"] == {
        "precision": pytest.approx(1 / 2),
        "recall": pytest.approx(1 / 2),
        "f1": pytest.approx(1 / 2),
        "support": 2,
    }
    assert metrics["macro_f1"] == pytest.approx((2 / 3 + 1 / 2) / 2)


@pytest.mark.parametrize(
    ("truth", "predicted", "message"),
    [
        ([], [], "empty"),
        ([0], [], "same length"),
        ([0, 2], [0, 1], "binary"),
        ([0, 1], [0, -1], "binary"),
    ],
)
def test_metrics_reject_invalid_inputs(truth, predicted, message):
    with pytest.raises(ValueError, match=message):
        classification_metrics(truth, predicted)


def test_evaluator_records_frozen_identity_and_refuses_overwrite(tmp_path, monkeypatch):
    import drowsyalert.experiments.eye_classifier as evaluator

    manifest = tmp_path / "manifest.csv"
    manifest.write_text("frozen synthetic manifest\n", encoding="utf-8")
    manifest_hash = hashlib.sha256(manifest.read_bytes()).hexdigest()
    checkpoint = tmp_path / "eye.pt"
    checkpoint.write_bytes(b"synthetic checkpoint")

    class TinyDataset(torch.utils.data.Dataset):
        def __init__(self, path, split):
            assert path == manifest
            assert split == "test"

        def __len__(self):
            return 4

        def __getitem__(self, index):
            label = index % 2
            return torch.full((3, 64, 64), float(label)), label

    class FixedModel(torch.nn.Module):
        def forward(self, inputs):
            score = (inputs.mean(dim=(1, 2, 3)) - 0.5) * 10
            return torch.stack((-score, score), dim=1)

    metadata = {
        "metadata": {
            "manifest_sha256": manifest_hash,
            "selected_by": "validation_macro_f1",
            "epoch": 3,
        }
    }
    monkeypatch.setattr(evaluator, "EyeDataset", TinyDataset)
    monkeypatch.setattr(evaluator, "load_checkpoint", lambda path: (FixedModel(), metadata))
    output = tmp_path / "results"
    result = evaluate(checkpoint, manifest, output, batch_size=2, device="cpu", threshold=0.5)

    assert result["metrics"]["accuracy"] == 1.0
    assert result["accuracy_target"] == {"threshold": 0.9, "met": True}
    assert result["decision_rule"] == "closed_probability >= 0.5"
    assert result["manifest_sha256"] == manifest_hash
    assert json.loads((output / "metrics.json").read_text()) == result
    with pytest.raises(FileExistsError, match="already exists"):
        evaluate(checkpoint, manifest, output, device="cpu")


def test_evaluator_rejects_manifest_not_used_for_checkpoint(tmp_path, monkeypatch):
    import drowsyalert.experiments.eye_classifier as evaluator

    manifest = tmp_path / "manifest.csv"
    manifest.write_text("different manifest\n", encoding="utf-8")
    checkpoint = tmp_path / "eye.pt"
    checkpoint.write_bytes(b"checkpoint")
    monkeypatch.setattr(
        evaluator,
        "load_checkpoint",
        lambda path: (torch.nn.Identity(), {"metadata": {"manifest_sha256": "0" * 64}}),
    )
    with pytest.raises(ValueError, match="does not match"):
        evaluate(checkpoint, manifest, tmp_path / "results", device="cpu")
