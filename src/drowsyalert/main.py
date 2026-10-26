"""Thin CLI. Heavy backends are imported only after parsing and asset checks."""

import argparse
import json
import logging
from pathlib import Path


def build_parser():
    parser = argparse.ArgumentParser(description="DrowsyAlert webcam / video demo")
    parser.add_argument("--config", type=Path, help="YAML config; default configs/config.yaml")
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--camera", type=int, default=0)
    source.add_argument("--video", type=Path)
    parser.add_argument(
        "--eye-backend",
        choices=("ear", "cnn"),
        default="ear",
        help="EAR works immediately; CNN requires a trained checkpoint",
    )
    parser.add_argument("--checkpoint")
    parser.add_argument("--face-model")
    parser.add_argument(
        "--method", choices=("perclos", "perclos-yawn", "perclos-head-pose"), default="perclos"
    )
    parser.add_argument(
        "--download-model", action="store_true", help="Download face model and exit"
    )
    parser.add_argument("--headless", action="store_true", help="Process without opening a window")
    parser.add_argument("--max-frames", type=int)
    parser.add_argument("--log", type=Path, help="Write per-frame CSV")
    parser.add_argument("--record", type=Path, help="Write a versioned experiment JSON record")
    parser.add_argument("--dataset-id", help="Dataset/version identity for experiment provenance")
    parser.add_argument("--split-id", help="Split-manifest identity for experiment provenance")
    parser.add_argument("--seed", type=int, help="Random seed used by the experiment protocol")
    parser.add_argument("--code-revision", help="Source revision or commit identity")
    parser.add_argument("--mute", action="store_true")
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.max_frames is not None and args.max_frames <= 0:
        parser.error("--max-frames must be positive")
    if args.camera < 0:
        parser.error("--camera must be nonnegative")
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    try:
        from drowsyalert.utils.config import load_config

        config = load_config(args.config)
        if args.checkpoint:
            config.checkpoint = args.checkpoint
        if args.face_model:
            config.face_model = args.face_model
        if args.download_model:
            from drowsyalert.detection.face import download_model

            print(download_model(config.resource(config.face_model)))
            return 0
        from drowsyalert.pipeline.realtime import run

        result = run(
            config,
            camera=args.camera,
            video=args.video,
            backend=args.eye_backend,
            method=args.method,
            headless=args.headless,
            max_frames=args.max_frames,
            log_path=args.log,
            record_path=args.record,
            dataset_id=args.dataset_id,
            split_id=args.split_id,
            random_seed=args.seed,
            code_revision=args.code_revision,
            mute=args.mute,
        )
        print(json.dumps(result, indent=2))
        return 0
    except KeyboardInterrupt:
        return 130
    except (OSError, RuntimeError, ValueError, ImportError) as error:
        logging.error("%s", error)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
