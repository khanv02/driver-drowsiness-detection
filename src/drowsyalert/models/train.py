"""Validation-selected EyeCNN training, reusable from local scripts and Colab."""

import argparse
import hashlib
import json
import random
from pathlib import Path

import cv2
import numpy as np
import torch
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score
from torch.utils.data import DataLoader, Dataset

from drowsyalert.models.dataset import read_manifest
from drowsyalert.models.eye_cnn import (
    CLASS_NAMES,
    EyeCNN,
    preprocess_eye,
    save_checkpoint,
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while block := source.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def set_determinism(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    torch.use_deterministic_algorithms(True)


class EyeDataset(Dataset):
    def __init__(self, manifest: Path, split: str, augment: bool = False):
        if split not in {"train", "val", "test"}:
            raise ValueError(f"Unknown dataset split: {split}")
        self.root, self.augment = manifest.parent, augment
        self.rows = [row for row in read_manifest(manifest) if row["split"] == split]
        if not self.rows:
            raise ValueError(f"Empty dataset split: {split}")

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, index):
        row = self.rows[index]
        image = cv2.imread(str(self.root / row["path"]))
        if image is None:
            raise ValueError(f"Cannot read eye image: {row['path']}")
        if self.augment:
            image = np.clip(image.astype(np.float32) * random.uniform(0.8, 1.2), 0, 255).astype(
                np.uint8
            )
            height, width = image.shape[:2]
            matrix = cv2.getRotationMatrix2D((width / 2, height / 2), random.uniform(-8, 8), 1)
            image = cv2.warpAffine(image, matrix, (width, height), borderMode=cv2.BORDER_REFLECT)
        return preprocess_eye(image), int(row["label"])


def measure(model, loader, device):
    model.eval()
    truth, predicted = [], []
    with torch.inference_mode():
        for inputs, labels in loader:
            predicted.extend(model(inputs.to(device)).argmax(1).cpu().tolist())
            truth.extend(labels.tolist())
    if not truth:
        raise ValueError("Cannot measure an empty dataset")
    return {
        "images": len(truth),
        "accuracy": float(accuracy_score(truth, predicted)),
        "macro_f1": float(
            f1_score(truth, predicted, labels=[0, 1], average="macro", zero_division=0)
        ),
        "confusion_matrix": confusion_matrix(truth, predicted, labels=[0, 1]).tolist(),
        "classes": CLASS_NAMES,
    }


def _resolve_device(device: str) -> str:
    if device == "auto":
        return "cuda" if torch.cuda.is_available() else "cpu"
    if device == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA was requested but is not available")
    return device


def train(
    manifest: Path,
    checkpoint: Path,
    output: Path,
    epochs: int = 30,
    batch_size: int = 64,
    patience: int = 5,
    seed: int = 42,
    device: str = "auto",
    learning_rate: float = 1e-3,
):
    if min(epochs, batch_size, patience) <= 0 or learning_rate <= 0:
        raise ValueError("epochs, batch_size, patience, and learning_rate must be positive")
    set_determinism(seed)
    torch.set_num_threads(min(4, torch.get_num_threads()))
    target = _resolve_device(device)
    manifest_hash = _sha256(manifest)
    train_data = EyeDataset(manifest, "train", True)
    validation_data = EyeDataset(manifest, "val")
    generator = torch.Generator().manual_seed(seed)
    train_loader = DataLoader(
        train_data,
        batch_size,
        shuffle=True,
        generator=generator,
        num_workers=0,
    )
    validation_loader = DataLoader(validation_data, batch_size, num_workers=0)
    model = EyeCNN().to(target)
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    loss_fn = torch.nn.CrossEntropyLoss()
    best_score, best_epoch, stale, history = -1.0, 0, 0, []
    output.mkdir(parents=True, exist_ok=True)
    run_config = {
        "manifest": str(manifest.resolve()),
        "manifest_sha256": manifest_hash,
        "checkpoint": str(checkpoint.resolve()),
        "class_names": CLASS_NAMES,
        "seed": seed,
        "device": target,
        "epochs_requested": epochs,
        "batch_size": batch_size,
        "patience": patience,
        "learning_rate": learning_rate,
        "optimizer": "Adam",
        "selection_metric": "validation_macro_f1",
        "deterministic_algorithms": True,
        "train_images": len(train_data),
        "validation_images": len(validation_data),
        "augmentation": "brightness 0.8-1.2; rotation -8..8 degrees; train only",
    }
    (output / "run_config.json").write_text(
        json.dumps(run_config, indent=2) + "\n", encoding="utf-8"
    )

    for epoch in range(1, epochs + 1):
        model.train()
        total, count = 0.0, 0
        for inputs, labels in train_loader:
            inputs, labels = inputs.to(target), labels.to(target)
            optimizer.zero_grad()
            loss = loss_fn(model(inputs), labels)
            loss.backward()
            optimizer.step()
            total += float(loss.detach()) * len(labels)
            count += len(labels)
        metrics = measure(model, validation_loader, target)
        row = {
            "epoch": epoch,
            "train_loss": total / count,
            "validation_accuracy": metrics["accuracy"],
            "validation_macro_f1": metrics["macro_f1"],
        }
        history.append(row)
        print(json.dumps(row), flush=True)
        if metrics["macro_f1"] > best_score:
            best_score, best_epoch, stale = metrics["macro_f1"], epoch, 0
            save_checkpoint(
                checkpoint,
                model,
                seed=seed,
                epoch=epoch,
                device=target,
                selected_by="validation_macro_f1",
                validation_macro_f1=best_score,
                validation_accuracy=metrics["accuracy"],
                manifest=str(manifest.resolve()),
                manifest_sha256=manifest_hash,
                learning_rate=learning_rate,
                batch_size=batch_size,
                train_images=len(train_data),
                validation_images=len(validation_data),
            )
        else:
            stale += 1
            if stale >= patience:
                break
    (output / "history.json").write_text(
        json.dumps(history, indent=2) + "\n", encoding="utf-8"
    )
    return {
        "selected_by": "validation_macro_f1",
        "best_epoch": best_epoch,
        "best_validation_macro_f1": best_score,
        "epochs_completed": len(history),
        "checkpoint_sha256": _sha256(checkpoint),
        "manifest_sha256": manifest_hash,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Train EyeCNN using validation-only selection")
    parser.add_argument("--manifest", type=Path, default=Path("data/processed/manifest.csv"))
    parser.add_argument("--checkpoint", type=Path, default=Path("models/checkpoints/eye_cnn.pt"))
    parser.add_argument("--output", type=Path, default=Path("outputs/results/eye_cnn-training"))
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--patience", type=int, default=5)
    parser.add_argument("--learning-rate", type=float, default=1e-3)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--device", choices=("auto", "cpu", "cuda"), default="auto")
    args = parser.parse_args()
    try:
        result = train(
            args.manifest,
            args.checkpoint,
            args.output,
            args.epochs,
            args.batch_size,
            args.patience,
            args.seed,
            args.device,
            args.learning_rate,
        )
    except ValueError as error:
        parser.error(str(error))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
