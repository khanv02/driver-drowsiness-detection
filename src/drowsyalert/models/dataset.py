"""Prepare reproducible group-disjoint image splits. Test images never receive augmentation."""

import argparse
import csv
import json
from hashlib import sha256
from pathlib import Path

import cv2
import numpy as np
from sklearn.model_selection import GroupShuffleSplit

LABELS = {"open": 0, "openeyes": 0, "closed": 1, "closedeyes": 1}


def label_from_path(path: Path, root: Path):
    for part in reversed(path.relative_to(root).parts[:-1]):
        key = part.lower().replace("_", "").replace("-", "").replace(" ", "")
        if key in LABELS:
            return LABELS[key]
    return None


def difference_hash(image):
    gray = cv2.cvtColor(cv2.resize(image, (9, 8)), cv2.COLOR_BGR2GRAY)
    value = 0
    for bit in (gray[:, 1:] > gray[:, :-1]).ravel():
        value = (value << 1) | int(bit)
    return value


def prepare(
    input_dir: Path,
    output: Path,
    seed: int = 42,
    group_csv: Path | None = None,
    face_model: Path | None = None,
):
    from drowsyalert.models.eye_cnn import IMAGE_SIZE

    if not input_dir.is_dir():
        raise FileNotFoundError(f"Dataset directory not found: {input_dir}")
    output.mkdir(parents=True, exist_ok=True)
    image_dir = output / "images"
    image_dir.mkdir(exist_ok=True)
    groups = {}
    if group_csv:
        with group_csv.open(encoding="utf-8", newline="") as source:
            groups = {
                row["source"].replace("\\", "/"): row["group_id"] for row in csv.DictReader(source)
            }
    detector = None
    if face_model:
        from drowsyalert.detection.face import FaceDetector

        detector = FaceDetector(face_model, image_mode=True)
    records, hashes, parent, skipped = [], {}, {}, 0

    def find(item):
        parent.setdefault(item, item)
        if parent[item] != item:
            parent[item] = find(parent[item])
        return parent[item]

    def union(a, b):
        parent[find(a)] = find(b)

    perceptual = []
    try:
        for image_path in sorted(input_dir.rglob("*")):
            if image_path.suffix.lower() not in (".jpg", ".jpeg", ".png", ".bmp"):
                continue
            label = label_from_path(image_path, input_dir)
            if label is None:
                continue
            image = cv2.imread(str(image_path))
            if image is None:
                skipped += 1
                continue
            source = image_path.relative_to(input_dir).as_posix()
            if group_csv and source not in groups:
                raise ValueError(f"Missing group_id for {source}")
            group = "subject:" + groups[source] if group_csv else "source:" + source
            crops = (image,)
            if detector:
                observation = detector.detect(image)
                if not observation.valid:
                    skipped += 1
                    continue
                crops = tuple(crop for crop in observation.eye_crops or () if crop is not None)
                if not crops:
                    skipped += 1
                    continue
            for eye_index, crop in enumerate(crops):
                resized = cv2.resize(crop, (IMAGE_SIZE, IMAGE_SIZE))
                digest = sha256(resized.tobytes()).hexdigest()
                if digest in hashes:
                    previous = hashes[digest]
                    if previous["label"] != label:
                        raise ValueError(f"Conflicting labels for duplicate image: {source}")
                    union(group, previous["group_id"])
                    continue
                phash = difference_hash(resized)
                for previous_hash, previous_group in perceptual:
                    if (phash ^ previous_hash).bit_count() <= 4:
                        union(group, previous_group)
                perceptual.append((phash, group))
                name = f"{digest}_{eye_index}.png"
                if not cv2.imwrite(str(image_dir / name), resized):
                    raise OSError(f"Cannot write processed image: {name}")
                row = {
                    "path": "images/" + name,
                    "label": label,
                    "group_id": group,
                    "source": source,
                    "sha256": digest,
                }
                records.append(row)
                hashes[digest] = row
    finally:
        if detector:
            detector.close()
    if len(records) < 12 or {r["label"] for r in records} != {0, 1}:
        raise ValueError("Need at least 12 usable images and both open/closed labels")
    labels = np.array([r["label"] for r in records])
    group_ids = np.array([find(r["group_id"]) for r in records])
    indices = np.arange(len(records))
    chosen = None
    # Choose splits only for class presence, never for model performance.
    for train_ids, remainder in GroupShuffleSplit(
        n_splits=30, test_size=0.3, random_state=seed
    ).split(indices, labels, group_ids):
        try:
            candidates = GroupShuffleSplit(n_splits=30, test_size=0.5, random_state=seed + 1)
            for val_local, test_local in candidates.split(
                remainder, labels[remainder], group_ids[remainder]
            ):
                val_ids, test_ids = remainder[val_local], remainder[test_local]
                if all(len(set(labels[ids])) == 2 for ids in (train_ids, val_ids, test_ids)):
                    chosen = (train_ids, val_ids, test_ids)
                    break
        except ValueError:
            continue
        if chosen is not None:
            break
    if chosen is None:
        raise ValueError("Not enough independent groups to split both classes into train/val/test")
    for split, ids in zip(("train", "val", "test"), chosen):
        for index in ids:
            records[index]["split"] = split
            records[index]["group_id"] = str(group_ids[index])
    manifest = output / "manifest.csv"
    with manifest.open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, ["path", "label", "group_id", "source", "sha256", "split"])
        writer.writeheader()
        writer.writerows(records)
    report = {
        "seed": seed,
        "input": str(input_dir.resolve()),
        "images": len(records),
        "skipped": skipped,
        "group_metadata": bool(group_csv),
        "grouping": "subject/session + exact/dHash duplicates"
        if group_csv
        else "source + exact/dHash duplicates; identity separation not guaranteed",
        "splits": {
            split: int(sum(r["split"] == split for r in records))
            for split in ("train", "val", "test")
        },
    }
    (output / "dataset.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def main():
    parser = argparse.ArgumentParser(description="Prepare open/closed eye dataset")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("data/processed"))
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--groups", type=Path, help="CSV with source,group_id; paths relative to input"
    )
    parser.add_argument("--face-model", type=Path, help="Use only for full-face images")
    args = parser.parse_args()
    print(
        json.dumps(
            prepare(args.input, args.output, args.seed, args.groups, args.face_model), indent=2
        )
    )


if __name__ == "__main__":
    main()
