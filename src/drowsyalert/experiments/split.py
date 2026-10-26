"""Deterministic clip-disjoint evaluation split construction."""

import csv
import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

from drowsyalert.experiments.video_manifest import VideoManifestRow

SPLIT_FIELDS = (
    "clip_id",
    "relative_path",
    "sha256",
    "source_category",
    "sex_group",
    "split",
    "locked_validation",
    "selection_seed",
    "selection_rank",
)
CATEGORIES = ("microsleep", "yawning")


@dataclass(frozen=True)
class SplitAssignment:
    clip_id: str
    relative_path: str
    sha256: str
    source_category: str
    sex_group: str
    split: str
    locked_validation: bool
    selection_seed: int
    selection_rank: int

    def as_dict(self) -> dict:
        return asdict(self)


def build_balanced_clip_split(
    manifest: Iterable[VideoManifestRow],
    *,
    validation_per_category: int,
    test_per_category: int,
    locked_validation_ids: set[str],
    seed: int,
) -> list[SplitAssignment]:
    rows = list(manifest)
    if validation_per_category <= 0 or test_per_category <= 0:
        raise ValueError("Validation and test category counts must be positive")
    _validate_manifest_identity(rows)
    by_id = {row.clip_id: row for row in rows}
    missing = locked_validation_ids - set(by_id)
    if missing:
        raise ValueError(f"Unknown locked validation clips: {sorted(missing)}")

    assignments = []
    for category in CATEGORIES:
        category_rows = [row for row in rows if row.source_category == category]
        required = validation_per_category + test_per_category
        if len(category_rows) < required:
            raise ValueError(
                f"Insufficient {category} clips: require {required}, found {len(category_rows)}"
            )
        locked = [row for row in category_rows if row.clip_id in locked_validation_ids]
        if len(locked) > validation_per_category:
            raise ValueError(f"Too many locked validation clips for {category}")
        locked = sorted(locked, key=lambda row: row.clip_id)
        candidates = [
            row for row in category_rows if row.clip_id not in locked_validation_ids
        ]
        validation_additions = _balanced_selection(
            candidates,
            validation_per_category - len(locked),
            seed=seed,
            initial=locked,
        )
        validation = [*locked, *validation_additions]
        validation_ids = {row.clip_id for row in validation}
        remaining = [row for row in candidates if row.clip_id not in validation_ids]
        test = _balanced_selection(remaining, test_per_category, seed=seed)
        selected = [*validation, *test]
        for rank, row in enumerate(selected, start=1):
            assignments.append(
                SplitAssignment(
                    clip_id=row.clip_id,
                    relative_path=row.relative_path,
                    sha256=row.sha256,
                    source_category=row.source_category,
                    sex_group=row.sex_group,
                    split="validation" if row in validation else "test",
                    locked_validation=row.clip_id in locked_validation_ids,
                    selection_seed=seed,
                    selection_rank=rank,
                )
            )
    split_order = {"validation": 0, "test": 1}
    return sorted(
        assignments,
        key=lambda row: (
            split_order[row.split],
            row.source_category,
            row.selection_rank,
            row.clip_id,
        ),
    )


def split_manifest_sha256(rows: Iterable[SplitAssignment]) -> str:
    serialized = sorted((row.as_dict() for row in rows), key=lambda row: row["clip_id"])
    canonical = json.dumps(serialized, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def write_split_manifest(
    path: Path, rows: Iterable[SplitAssignment], *, overwrite: bool = False
) -> None:
    values = list(rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w" if overwrite else "x", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=SPLIT_FIELDS)
        writer.writeheader()
        for row in values:
            writer.writerow(row.as_dict())


def load_split_manifest(path: Path) -> list[SplitAssignment]:
    with path.open(newline="", encoding="utf-8-sig") as source:
        reader = csv.DictReader(source)
        if tuple(reader.fieldnames or ()) != SPLIT_FIELDS:
            raise ValueError("Split manifest columns do not match the versioned contract")
        rows = []
        for line_number, row in enumerate(reader, start=2):
            try:
                if row["locked_validation"].casefold() not in {"true", "false"}:
                    raise ValueError("locked_validation must be true or false")
                rows.append(
                    SplitAssignment(
                        **{
                            **row,
                            "locked_validation": row["locked_validation"].casefold() == "true",
                            "selection_seed": int(row["selection_seed"]),
                            "selection_rank": int(row["selection_rank"]),
                        }
                    )
                )
            except (TypeError, ValueError) as error:
                raise ValueError(
                    f"Invalid split manifest at CSV line {line_number}: {error}"
                ) from error
    if not rows:
        raise ValueError("Split manifest is empty")
    return rows


def split_summary(rows: Iterable[SplitAssignment]) -> dict:
    values = list(rows)
    counts = {}
    for row in values:
        key = f"{row.split}/{row.source_category}"
        counts[key] = counts.get(key, 0) + 1
    return {
        "clips": len(values),
        "counts": dict(sorted(counts.items())),
        "locked_validation": sum(row.locked_validation for row in values),
        "split_sha256": split_manifest_sha256(values),
        "participant_mapping": "unavailable",
        "separation": "clip-disjoint",
    }


def _validate_manifest_identity(rows: list[VideoManifestRow]) -> None:
    clip_ids = set()
    hashes = set()
    for row in rows:
        if row.clip_id in clip_ids:
            raise ValueError(f"Duplicate clip ID: {row.clip_id}")
        if row.sha256 in hashes:
            raise ValueError(f"Duplicate content hash: {row.sha256}")
        clip_ids.add(row.clip_id)
        hashes.add(row.sha256)


def _selection_key(row: VideoManifestRow, seed: int) -> tuple[str, str]:
    value = f"{seed}:{row.source_category}:{row.clip_id}:{row.sha256}"
    return hashlib.sha256(value.encode("utf-8")).hexdigest(), row.clip_id


def _balanced_selection(
    rows: list[VideoManifestRow],
    count: int,
    *,
    seed: int,
    initial: list[VideoManifestRow] | None = None,
) -> list[VideoManifestRow]:
    if count == 0:
        return []
    queues = {
        sex: sorted(
            (row for row in rows if row.sex_group == sex),
            key=lambda row: _selection_key(row, seed),
        )
        for sex in ("female", "male")
    }
    if sum(len(queue) for queue in queues.values()) != len(rows):
        raise ValueError("Balanced split requires male/female source groups")
    selected = []
    selected_counts = {
        sex: sum(row.sex_group == sex for row in (initial or []))
        for sex in queues
    }
    for _index in range(count):
        available = [sex for sex, queue in queues.items() if queue]
        if not available:
            raise ValueError("Insufficient clips for balanced selection")
        sex = min(
            available,
            key=lambda value: (
                selected_counts[value],
                -len(queues[value]),
                value,
            ),
        )
        selected.append(queues[sex].pop(0))
        selected_counts[sex] += 1
    return selected
