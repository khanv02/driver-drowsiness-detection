"""Prepare deterministic, group-disjoint eye-image manifests."""

import argparse
import csv
import json
from hashlib import sha256
from pathlib import Path, PurePosixPath

import cv2
import numpy as np
from sklearn.model_selection import GroupShuffleSplit

LABELS = {"open": 0, "openeyes": 0, "closed": 1, "closedeyes": 1}
CLASS_NAMES = {0: "open", 1: "closed"}
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp"}
MANIFEST_FIELDS = [
    "path",
    "label",
    "group_id",
    "source",
    "source_sha256",
    "sha256",
    "split",
]


def _label_key(value: str) -> str:
    return value.lower().replace("_", "").replace("-", "").replace(" ", "")


def label_from_path(path: Path, root: Path) -> int | None:
    labels = {
        LABELS[key]
        for part in path.relative_to(root).parts[:-1]
        if (key := _label_key(part)) in LABELS
    }
    if len(labels) > 1:
        raise ValueError(f"Ambiguous eye-state label in path: {path.relative_to(root)}")
    return next(iter(labels), None)


def difference_hash(image: np.ndarray) -> int:
    gray = cv2.cvtColor(cv2.resize(image, (9, 8)), cv2.COLOR_BGR2GRAY)
    value = 0
    for bit in (gray[:, 1:] > gray[:, :-1]).ravel():
        value = (value << 1) | int(bit)
    return value


def _file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as source:
        while block := source.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def _normalise_source(value: str) -> str:
    source = value.strip().replace("\\", "/")
    parts = PurePosixPath(source).parts
    if not source or source.startswith("/") or ".." in parts:
        raise ValueError(f"Group source must be a relative dataset path: {value!r}")
    return PurePosixPath(source).as_posix()


def _load_groups(group_csv: Path | None) -> dict[str, str]:
    if group_csv is None:
        return {}
    if not group_csv.is_file():
        raise FileNotFoundError(f"Group CSV not found: {group_csv}")
    with group_csv.open(encoding="utf-8", newline="") as source:
        reader = csv.DictReader(source)
        if reader.fieldnames is None or not {"source", "group_id"}.issubset(reader.fieldnames):
            raise ValueError("Group CSV must contain source and group_id columns")
        groups: dict[str, str] = {}
        for line, row in enumerate(reader, start=2):
            key = _normalise_source(row["source"])
            group_id = row["group_id"].strip()
            if not group_id:
                raise ValueError(f"Empty group_id at group CSV line {line}")
            if key in groups and groups[key] != group_id:
                raise ValueError(f"Conflicting group_id values for {key}")
            groups[key] = group_id
    return groups


def _choose_splits(labels: np.ndarray, groups: np.ndarray, seed: int):
    indices = np.arange(len(labels))
    chosen = None
    # Candidate selection checks class presence only, never model performance.
    for train_ids, remainder in GroupShuffleSplit(
        n_splits=30, test_size=0.3, random_state=seed
    ).split(indices, labels, groups):
        try:
            candidates = GroupShuffleSplit(n_splits=30, test_size=0.5, random_state=seed + 1)
            for val_local, test_local in candidates.split(
                remainder, labels[remainder], groups[remainder]
            ):
                val_ids, test_ids = remainder[val_local], remainder[test_local]
                if all(len(set(labels[ids])) == 2 for ids in (train_ids, val_ids, test_ids)):
                    chosen = (train_ids, val_ids, test_ids)
                    break
        except ValueError:
            continue
        if chosen is not None:
            return chosen
    raise ValueError("Not enough independent groups to split both classes into train/val/test")


def prepare(
    input_dir: Path,
    output: Path,
    seed: int = 42,
    group_csv: Path | None = None,
    face_model: Path | None = None,
    dataset_name: str = "unspecified",
    source_url: str | None = None,
):
    from drowsyalert.models.eye_cnn import IMAGE_SIZE

    if not input_dir.is_dir():
        raise FileNotFoundError(f"Dataset directory not found: {input_dir}")
    if not dataset_name.strip():
        raise ValueError("dataset_name must not be empty")
    output.mkdir(parents=True, exist_ok=True)
    image_dir = output / "images"
    image_dir.mkdir(exist_ok=True)
    declared_groups = _load_groups(group_csv)
    detector = None
    if face_model:
        from drowsyalert.detection.face import FaceDetector

        detector = FaceDetector(face_model, image_mode=True)
    records: list[dict] = []
    hashes: dict[str, dict] = {}
    parent: dict[str, str] = {}
    perceptual: list[tuple[int, str]] = []
    candidates = unlabeled = unreadable = duplicates_removed = 0

    def find(item: str) -> str:
        parent.setdefault(item, item)
        if parent[item] != item:
            parent[item] = find(parent[item])
        return parent[item]

    def union(first: str, second: str) -> None:
        parent[find(first)] = find(second)

    try:
        for image_path in sorted(input_dir.rglob("*")):
            if image_path.suffix.lower() not in IMAGE_SUFFIXES:
                continue
            candidates += 1
            label = label_from_path(image_path, input_dir)
            if label is None:
                unlabeled += 1
                continue
            source = image_path.relative_to(input_dir).as_posix()
            if group_csv and source not in declared_groups:
                raise ValueError(f"Missing group_id for {source}")
            raw_group = (
                "subject:" + declared_groups[source]
                if group_csv
                else "source:" + source
            )
            image = cv2.imread(str(image_path))
            if image is None:
                unreadable += 1
                continue
            crops = (image,)
            if detector:
                observation = detector.detect(image)
                if not observation.valid:
                    unreadable += 1
                    continue
                crops = tuple(crop for crop in observation.eye_crops or () if crop is not None)
                if not crops:
                    unreadable += 1
                    continue
            source_digest = _file_sha256(image_path)
            for eye_index, crop in enumerate(crops):
                resized = cv2.resize(crop, (IMAGE_SIZE, IMAGE_SIZE))
                digest = sha256(resized.tobytes()).hexdigest()
                if digest in hashes:
                    previous = hashes[digest]
                    if previous["label"] != label:
                        raise ValueError(f"Conflicting labels for duplicate image: {source}")
                    union(raw_group, previous["group_id"])
                    duplicates_removed += 1
                    continue
                phash = difference_hash(resized)
                for previous_hash, previous_group in perceptual:
                    if (phash ^ previous_hash).bit_count() <= 4:
                        union(raw_group, previous_group)
                perceptual.append((phash, raw_group))
                name = f"{digest}_{eye_index}.png"
                if not cv2.imwrite(str(image_dir / name), resized):
                    raise OSError(f"Cannot write processed image: {name}")
                row = {
                    "path": "images/" + name,
                    "label": label,
                    "group_id": raw_group,
                    "source": source,
                    "source_sha256": source_digest,
                    "sha256": digest,
                }
                records.append(row)
                hashes[digest] = row
    finally:
        if detector:
            detector.close()

    if len(records) < 12 or {row["label"] for row in records} != {0, 1}:
        raise ValueError("Need at least 12 usable images and both open/closed labels")
    labels = np.array([row["label"] for row in records])
    group_ids = np.array([find(row["group_id"]) for row in records])
    chosen = _choose_splits(labels, group_ids, seed)
    for split, ids in zip(("train", "val", "test"), chosen, strict=True):
        for index in ids:
            records[index]["split"] = split
            records[index]["group_id"] = str(group_ids[index])

    manifest = output / "manifest.csv"
    with manifest.open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, MANIFEST_FIELDS)
        writer.writeheader()
        writer.writerows(records)

    split_report = {}
    for split in ("train", "val", "test"):
        rows = [row for row in records if row["split"] == split]
        split_report[split] = {
            "images": len(rows),
            "groups": len({row["group_id"] for row in rows}),
            "open": sum(row["label"] == 0 for row in rows),
            "closed": sum(row["label"] == 1 for row in rows),
        }
    warnings = []
    if not group_csv:
        warnings.append(
            "No subject/session metadata: source and duplicate groups do not prove "
            "identity-disjoint splits."
        )
    report = {
        "schema_version": 1,
        "dataset": dataset_name,
        "source_url": source_url,
        "seed": seed,
        "input": str(input_dir.resolve()),
        "image_size": IMAGE_SIZE,
        "class_names": {"0": CLASS_NAMES[0], "1": CLASS_NAMES[1]},
        "transformations": [
            "decode_bgr",
            "face_eye_crop" if face_model else f"resize_{IMAGE_SIZE}x{IMAGE_SIZE}",
        ],
        "candidates": candidates,
        "images": len(records),
        "excluded": {"unlabeled": unlabeled, "unreadable_or_invalid": unreadable},
        "duplicates_removed": duplicates_removed,
        "group_metadata": bool(group_csv),
        "identity_separation": bool(group_csv),
        "grouping": (
            "subject/session plus exact/dHash duplicate linkage"
            if group_csv
            else "source plus exact/dHash duplicate linkage"
        ),
        "splits": split_report,
        "manifest_sha256": _file_sha256(manifest),
        "warnings": warnings,
    }
    (output / "dataset.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare open/closed eye dataset")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("data/processed"))
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--dataset-name", required=True)
    parser.add_argument("--source-url")
    parser.add_argument(
        "--groups", type=Path, help="CSV with source,group_id; paths relative to input"
    )
    parser.add_argument("--face-model", type=Path, help="Use only for full-face images")
    args = parser.parse_args()
    print(
        json.dumps(
            prepare(
                args.input,
                args.output,
                args.seed,
                args.groups,
                args.face_model,
                args.dataset_name,
                args.source_url,
            ),
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
