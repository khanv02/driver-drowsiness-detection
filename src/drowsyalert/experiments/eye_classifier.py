"""One-way held-out evaluation for a frozen EyeCNN checkpoint and manifest."""

import argparse
import hashlib
import json
from pathlib import Path

import torch
from sklearn.metrics import accuracy_score, confusion_matrix, precision_recall_fscore_support
from torch.utils.data import DataLoader

from drowsyalert.models.eye_cnn import CLASS_NAMES, load_checkpoint
from drowsyalert.models.train import EyeDataset


def _sha256(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while block := source.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def classification_metrics(truth: list[int], predicted: list[int]) -> dict:
    if not truth:
        raise ValueError("Cannot calculate metrics for empty inputs")
    if len(truth) != len(predicted):
        raise ValueError("Truth and predicted inputs must have the same length")
    if not set(truth + predicted).issubset({0, 1}):
        raise ValueError("Eye-state metrics require binary labels 0 and 1")
    precision, recall, f1, support = precision_recall_fscore_support(
        truth, predicted, labels=[0, 1], zero_division=0
    )
    per_class = {
        name: {
            "precision": float(precision[index]),
            "recall": float(recall[index]),
            "f1": float(f1[index]),
            "support": int(support[index]),
        }
        for index, name in enumerate(CLASS_NAMES)
    }
    return {
        "images": len(truth),
        "accuracy": float(accuracy_score(truth, predicted)),
        "macro_f1": float(f1.mean()),
        "confusion_matrix": confusion_matrix(truth, predicted, labels=[0, 1]).tolist(),
        "classes": CLASS_NAMES,
        "per_class": per_class,
    }


def _device_name(device: str) -> str:
    if device == "auto":
        return "cuda" if torch.cuda.is_available() else "cpu"
    if device == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA was requested but is not available")
    return device


def evaluate(
    checkpoint_path: Path,
    manifest: Path,
    output: Path,
    batch_size: int = 64,
    device: str = "auto",
    threshold: float = 0.5,
) -> dict:
    if batch_size <= 0:
        raise ValueError("batch_size must be positive")
    if not 0 < threshold < 1:
        raise ValueError("threshold must be between 0 and 1")
    result_path = output / "metrics.json"
    if result_path.exists():
        raise FileExistsError(
            f"Held-out result already exists: {result_path}. Refusing to overwrite it."
        )
    manifest_hash = _sha256(manifest)
    checkpoint_hash = _sha256(checkpoint_path)
    model, checkpoint = load_checkpoint(checkpoint_path)
    metadata = checkpoint.get("metadata", {})
    if metadata.get("manifest_sha256") != manifest_hash:
        raise ValueError("Checkpoint manifest identity does not match the evaluation manifest")
    if metadata.get("selected_by") != "validation_macro_f1":
        raise ValueError("Checkpoint does not record validation-only model selection")
    target = _device_name(device)
    model = model.to(target).eval()
    loader = DataLoader(EyeDataset(manifest, "test"), batch_size=batch_size, num_workers=0)
    truth: list[int] = []
    predicted: list[int] = []
    with torch.inference_mode():
        for inputs, labels in loader:
            closed_probabilities = model(inputs.to(target)).softmax(dim=1)[:, 1]
            predicted.extend((closed_probabilities >= threshold).int().cpu().tolist())
            truth.extend(labels.tolist())
    metrics = classification_metrics(truth, predicted)
    result = {
        "schema_version": 1,
        "protocol": "frozen checkpoint; held-out test split; aggregate metrics only",
        "checkpoint_sha256": checkpoint_hash,
        "manifest_sha256": manifest_hash,
        "selected_by": metadata["selected_by"],
        "selected_epoch": metadata.get("epoch"),
        "decision_rule": f"closed_probability >= {threshold:g}",
        "device": target,
        "accuracy_target": {"threshold": 0.9, "met": metrics["accuracy"] >= 0.9},
        "metrics": metrics,
    }
    output.mkdir(parents=True, exist_ok=True)
    result_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate a frozen EyeCNN test split once")
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--threshold", type=float, default=0.5)
    parser.add_argument("--device", choices=("auto", "cpu", "cuda"), default="auto")
    args = parser.parse_args()
    try:
        result = evaluate(
            args.checkpoint,
            args.manifest,
            args.output,
            args.batch_size,
            args.device,
            args.threshold,
        )
    except (ValueError, FileExistsError) as error:
        parser.error(str(error))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
