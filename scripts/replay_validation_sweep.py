"""Replay stored validation observations over a bounded configuration sweep."""

import argparse
import json
from pathlib import Path

from drowsyalert.experiments.annotations import load_annotations_csv
from drowsyalert.experiments.batch import load_batch_plan
from drowsyalert.experiments.evaluation import EvaluationProtocol
from drowsyalert.experiments.replay import (
    DEFAULT_MAX_CANDIDATES,
    run_validation_sweep,
    write_sweep_result,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--output-root", type=Path)
    parser.add_argument("--annotations", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-candidates", type=int, default=DEFAULT_MAX_CANDIDATES)
    parser.add_argument("--early-tolerance", type=float, required=True)
    parser.add_argument("--late-tolerance", type=float, required=True)
    parser.add_argument("--bin-seconds", type=float, required=True)
    parser.add_argument("--positive-fraction", type=float, required=True)
    parser.add_argument("--reference-label", action="append", required=True)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    plan = load_batch_plan(args.plan)
    output_root = args.output_root or args.plan.parent
    protocol = EvaluationProtocol(
        early_tolerance=args.early_tolerance,
        late_tolerance=args.late_tolerance,
        bin_seconds=args.bin_seconds,
        positive_fraction=args.positive_fraction,
        reference_labels=frozenset(args.reference_label),
    )
    result = run_validation_sweep(
        plan,
        output_root=output_root,
        annotations=load_annotations_csv(args.annotations),
        protocol=protocol,
        max_candidates=args.max_candidates,
    )
    write_sweep_result(args.output, result)
    print(
        json.dumps(
            {
                "candidates": len(result["candidates"]),
                "sweep_sha256": result["sweep_sha256"],
                "output": str(args.output),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
