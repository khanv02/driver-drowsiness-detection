"""Create the frozen balanced NITYMED clip-disjoint evaluation split."""

import argparse
import json
from pathlib import Path

from drowsyalert.experiments.split import (
    build_balanced_clip_split,
    split_summary,
    write_split_manifest,
)
from drowsyalert.experiments.video_manifest import load_video_manifest


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--validation-per-category", type=int, default=6)
    parser.add_argument("--test-per-category", type=int, default=13)
    parser.add_argument("--lock-validation", action="append", default=[])
    parser.add_argument("--overwrite", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    rows = build_balanced_clip_split(
        load_video_manifest(args.manifest),
        validation_per_category=args.validation_per_category,
        test_per_category=args.test_per_category,
        locked_validation_ids=set(args.lock_validation),
        seed=args.seed,
    )
    write_split_manifest(args.output, rows, overwrite=args.overwrite)
    print(json.dumps(split_summary(rows), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
