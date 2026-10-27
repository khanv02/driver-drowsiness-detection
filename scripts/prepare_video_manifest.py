"""Build a local, ignored NITYMED HDTV720 inventory manifest."""

import argparse
import json
from pathlib import Path

from drowsyalert.experiments.video_manifest import (
    build_nitymed_manifest,
    manifest_summary,
    write_video_manifest,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True, help="Extracted DSM_Dataset-HDTV720")
    parser.add_argument("--output", type=Path, required=True, help="Local CSV manifest path")
    parser.add_argument(
        "--retrieval-date", required=True, help="Dataset retrieval date (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--overwrite", action="store_true", help="Replace only the requested manifest"
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    rows = build_nitymed_manifest(args.root, retrieval_date=args.retrieval_date)
    write_video_manifest(args.output, rows, overwrite=args.overwrite)
    print(json.dumps(manifest_summary(rows), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
