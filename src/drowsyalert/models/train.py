"""Single-model training and held-out evaluation, reusable from Colab and scripts."""

import argparse
import csv
import json
import random
from pathlib import Path

import cv2
import numpy as np
import torch
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from torch.utils.data import DataLoader, Dataset

from drowsyalert.models.eye_cnn import (
    CLASS_NAMES,
    EyeCNN,
    load_checkpoint,
    preprocess_eye,
    save_checkpoint,
)


class EyeDataset(Dataset):
    def __init__(self, manifest: Path, split: str, augment: bool = False):
        self.root, self.augment = manifest.parent, augment
        with manifest.open(encoding="utf-8", newline="") as file:
            self.rows = [row for row in csv.DictReader(file) if row["split"] == split]
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
    return {
        "accuracy": float(accuracy_score(truth, predicted)),
        "macro_f1": float(
            f1_score(truth, predicted, labels=[0, 1], average="macro", zero_division=0)
        ),
        "confusion_matrix": confusion_matrix(truth, predicted, labels=[0, 1]).tolist(),
        "classes": CLASS_NAMES,
        "report": classification_report(
            truth,
            predicted,
            labels=[0, 1],
            target_names=CLASS_NAMES,
            output_dict=True,
            zero_division=0,
        ),
    }


def write_metrics(metrics, destination: Path):
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    figure, axis = plt.subplots(figsize=(4, 4))
    matrix = np.array(metrics["confusion_matrix"])
    axis.imshow(matrix, cmap="Blues")
    axis.set(
        xticks=[0, 1],
        yticks=[0, 1],
        xticklabels=CLASS_NAMES,
        yticklabels=CLASS_NAMES,
        xlabel="Predicted",
        ylabel="Actual",
        title="Eye state confusion matrix",
    )
    for i in range(2):
        for j in range(2):
            axis.text(j, i, str(matrix[i, j]), ha="center", va="center")
    figure.tight_layout()
    figure.savefig(destination / "confusion_matrix.png", dpi=150)
    plt.close(figure)


def train(
    manifest: Path,
    checkpoint: Path,
    output: Path,
    epochs=30,
    batch_size=64,
    patience=5,
    seed=42,
    device="auto",
):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.set_num_threads(min(4, torch.get_num_threads()))
    target = (
        "cuda"
        if device == "auto" and torch.cuda.is_available()
        else ("cpu" if device == "auto" else device)
    )
    model = EyeCNN().to(target)
    train_loader = DataLoader(EyeDataset(manifest, "train", True), batch_size, shuffle=True)
    val_loader = DataLoader(EyeDataset(manifest, "val"), batch_size)
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    loss_fn = torch.nn.CrossEntropyLoss()
    best, stale, history = -1.0, 0, []
    output.mkdir(parents=True, exist_ok=True)
    for epoch in range(epochs):
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
        metrics = measure(model, val_loader, target)
        row = {
            "epoch": epoch + 1,
            "train_loss": total / count,
            "val_accuracy": metrics["accuracy"],
            "val_macro_f1": metrics["macro_f1"],
        }
        history.append(row)
        print(json.dumps(row), flush=True)
        if metrics["macro_f1"] > best:
            best, stale = metrics["macro_f1"], 0
            save_checkpoint(
                checkpoint,
                model,
                seed=seed,
                epoch=epoch + 1,
                device=target,
                validation_macro_f1=best,
                manifest=str(manifest),
                learning_rate=1e-3,
                batch_size=batch_size,
            )
        else:
            stale += 1
            if stale >= patience:
                break
    (output / "history.json").write_text(json.dumps(history, indent=2), encoding="utf-8")
    # Test is evaluated once, after selecting a checkpoint exclusively on validation.
    best_model, _ = load_checkpoint(checkpoint)
    result = measure(
        best_model.to(target), DataLoader(EyeDataset(manifest, "test"), batch_size), target
    )
    write_metrics(result, output)
    return result


def main():
    parser = argparse.ArgumentParser(description="Train or evaluate EyeCNN")
    parser.add_argument("--manifest", type=Path, default=Path("data/processed/manifest.csv"))
    parser.add_argument("--checkpoint", type=Path, default=Path("models/checkpoints/eye_cnn.pt"))
    parser.add_argument("--output", type=Path, default=Path("outputs/results/eye_cnn"))
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--patience", type=int, default=5)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--device", choices=("auto", "cpu", "cuda"), default="auto")
    parser.add_argument("--evaluate", action="store_true")
    args = parser.parse_args()
    if min(args.epochs, args.batch_size, args.patience) <= 0:
        parser.error("epochs, batch-size and patience must be positive")
    if args.evaluate:
        model, _ = load_checkpoint(args.checkpoint)
        result = measure(
            model, DataLoader(EyeDataset(args.manifest, "test"), args.batch_size), "cpu"
        )
        write_metrics(result, args.output)
    else:
        result = train(
            args.manifest,
            args.checkpoint,
            args.output,
            args.epochs,
            args.batch_size,
            args.patience,
            args.seed,
            args.device,
        )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
