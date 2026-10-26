"""Run or evaluate a frozen, common-clip NITYMED A/B/C batch plan."""

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from drowsyalert.experiments.annotation_review import load_worklist
from drowsyalert.experiments.annotations import load_annotations_csv, validate_annotations
from drowsyalert.experiments.batch import (
    BatchClip,
    build_batch_plan,
    export_batch_comparison,
    run_batch,
)
from drowsyalert.experiments.evaluation import EvaluationProtocol
from drowsyalert.experiments.video_manifest import (
    load_video_manifest,
    video_manifest_sha256,
)
from drowsyalert.utils.config import load_config


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--worklist", type=Path, required=True)
    parser.add_argument("--video-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--partition", choices=("validation", "test"), required=True)
    parser.add_argument("--split-id", required=True)
    parser.add_argument("--code-revision", required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--annotations", type=Path)
    parser.add_argument("--early-tolerance", type=float)
    parser.add_argument("--late-tolerance", type=float)
    parser.add_argument("--bin-seconds", type=float)
    parser.add_argument("--positive-fraction", type=float)
    parser.add_argument("--reference-label", action="append")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    manifest = load_video_manifest(args.manifest)
    manifest_by_clip = {row.clip_id: row for row in manifest}
    worklist = load_worklist(args.worklist)
    selected = [
        row
        for row in worklist
        if row.split == args.partition and row.review_status == "reviewed"
    ]
    if not selected:
        raise ValueError(f"No reviewed clips assigned to {args.partition}")
    batch_clips = []
    for review in selected:
        source = manifest_by_clip.get(review.clip_id)
        if source is None or source.relative_path != review.relative_path:
            raise ValueError(f"Worklist/manifest mismatch: {review.clip_id}")
        batch_clips.append(
            BatchClip(
                review.clip_id,
                source.relative_path,
                source.sha256,
                source.duration_seconds,
                args.partition,
            )
        )
    config = load_config(args.config)
    plan = build_batch_plan(
        dataset_id="nitymed-hdtv720",
        split_id=args.split_id,
        manifest_sha256=video_manifest_sha256(manifest),
        code_revision=args.code_revision,
        random_seed=args.seed,
        partition=args.partition,
        eye_source="landmark_ear",
        resolved_config=asdict(config),
        clips=batch_clips,
    )
    status = run_batch(
        plan,
        config=config,
        video_root=args.video_root,
        output_root=args.output,
    )
    print(json.dumps(status, indent=2, sort_keys=True))
    if args.annotations is not None:
        _export_comparison(args, manifest, plan)
    return 2 if status["failed"] else 0


def _export_comparison(args, manifest, plan) -> None:
    required = {
        "early_tolerance": args.early_tolerance,
        "late_tolerance": args.late_tolerance,
        "bin_seconds": args.bin_seconds,
        "positive_fraction": args.positive_fraction,
        "reference_label": args.reference_label,
    }
    missing = [name for name, value in required.items() if value is None]
    if missing:
        raise ValueError(f"Comparison protocol arguments are missing: {missing}")
    durations = {row.clip_id: row.duration_seconds for row in manifest}
    annotations = validate_annotations(load_annotations_csv(args.annotations), durations)
    selected = [row for row in annotations if row.split == args.partition]
    protocol = EvaluationProtocol(
        early_tolerance=args.early_tolerance,
        late_tolerance=args.late_tolerance,
        bin_seconds=args.bin_seconds,
        positive_fraction=args.positive_fraction,
        reference_labels=frozenset(args.reference_label),
    )
    export_batch_comparison(
        plan,
        annotations=selected,
        protocol=protocol,
        output_root=args.output,
        destination=args.output / "comparison.json",
    )


if __name__ == "__main__":
    raise SystemExit(main())
