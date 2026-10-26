"""Prepare deterministic, group-disjoint eye-image manifests."""

import argparse
import csv
import json
import re
from hashlib import sha256
from pathlib import Path, PurePosixPath

import cv2
import numpy as np
from sklearn.model_selection import GroupShuffleSplit

LABELS = {
    "open": 0,
    "openeyes": 0,
    "openlefteyes": 0,
    "openrighteyes": 0,
    "closed": 1,
    "closedeyes": 1,
    "closedlefteyes": 1,
    "closedrighteyes": 1,
}
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


def read_manifest(manifest: Path) -> list[dict[str, str]]:
    """Read and validate the full split manifest before a model can consume it."""
    if not manifest.is_file():
        raise FileNotFoundError(f"Manifest not found: {manifest}")
    with manifest.open(encoding="utf-8", newline="") as source:
        reader = csv.DictReader(source)
        missing = set(MANIFEST_FIELDS) - set(reader.fieldnames or ())
        if missing:
            raise ValueError(f"Manifest is missing columns: {', '.join(sorted(missing))}")
        rows = list(reader)
    if not rows:
        raise ValueError("Manifest is empty")
    paths: set[str] = set()
    group_splits: dict[str, str] = {}
    split_labels = {split: set() for split in ("train", "val", "test")}
    for line, row in enumerate(rows, start=2):
        path = _normalise_source(row["path"])
        source = _normalise_source(row["source"])
        split = row["split"]
        group_id = row["group_id"].strip()
        if path in paths:
            raise ValueError(f"Duplicate manifest path at line {line}: {path}")
        if split not in split_labels:
            raise ValueError(f"Invalid split at line {line}: {split!r}")
        if row["label"] not in {"0", "1"}:
            raise ValueError(f"Invalid label at line {line}: {row['label']!r}")
        if not group_id:
            raise ValueError(f"Empty group_id at manifest line {line}")
        for field in ("source_sha256", "sha256"):
            value = row[field].lower()
            if len(value) != 64 or any(character not in "0123456789abcdef" for character in value):
                raise ValueError(f"Invalid {field} at manifest line {line}")
        prior_split = group_splits.setdefault(group_id, split)
        if prior_split != split:
            raise ValueError(
                f"Group {group_id!r} appears in both {prior_split!r} and {split!r} splits"
            )
        paths.add(path)
        split_labels[split].add(row["label"])
        row["path"], row["source"] = path, source
    for split, labels in split_labels.items():
        if labels != {"0", "1"}:
            raise ValueError(f"Split {split!r} must contain both open and closed labels")
    return rows


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


def _cew_pair_group(source: str, label: int) -> str:
    """Group the left/right CEW patches cropped from the same face."""
    stem = Path(source).stem
    paired_stem = re.sub(r"_[LR]$", "", stem, flags=re.IGNORECASE)
    if paired_stem == stem:
        raise ValueError(f"CEW eye filename does not end in _L or _R: {source}")
    return f"cew-pair:{label}:{paired_stem}"


def _tree_sha256(source_hashes: dict[str, str]) -> str:
    digest = sha256()
    for source, source_digest in sorted(source_hashes.items()):
        digest.update(source.encode("utf-8"))
        digest.update(b"\0")
        digest.update(source_digest.encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


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
    group_strategy: str = "source",
):
    from drowsyalert.models.eye_cnn import IMAGE_SIZE

    if not input_dir.is_dir():
        raise FileNotFoundError(f"Dataset directory not found: {input_dir}")
    if not dataset_name.strip():
        raise ValueError("dataset_name must not be empty")
    if group_strategy not in {"source", "cew-paired-eyes"}:
        raise ValueError(f"Unknown group strategy: {group_strategy}")
    if group_csv and group_strategy != "source":
        raise ValueError("Use either group_csv or a built-in group strategy, not both")
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
    source_hashes: dict[str, str] = {}
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
            if group_csv:
                raw_group = "subject:" + declared_groups[source]
            elif group_strategy == "cew-paired-eyes":
                raw_group = _cew_pair_group(source, label)
            else:
                raw_group = "source:" + source
            source_digest = _file_sha256(image_path)
            source_hashes[source] = source_digest
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
    if not group_csv and group_strategy == "source":
        warnings.append(
            "No subject/session metadata: source and duplicate groups do not prove "
            "identity-disjoint splits."
        )
    if group_strategy == "cew-paired-eyes":
        warnings.append(
            "CEW left/right patches are grouped by filename; identities beyond each "
            "published one-subject pair cannot be independently verified."
        )
    report = {
        "schema_version": 1,
        "dataset": dataset_name,
        "source_url": source_url,
        "input_tree_sha256": _tree_sha256(source_hashes),
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
        "paired_eye_separation": group_strategy == "cew-paired-eyes",
        "group_strategy": group_strategy,
        "grouping": (
            "subject/session plus exact/dHash duplicate linkage"
            if group_csv
            else (
                "CEW filename pair plus exact/dHash duplicate linkage"
                if group_strategy == "cew-paired-eyes"
                else "source plus exact/dHash duplicate linkage"
            )
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
        "--group-strategy",
        choices=("source", "cew-paired-eyes"),
        default="source",
        help="Built-in grouping when no --groups CSV is available",
    )
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
                args.group_strategy,
            ),
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
