"""Create and review independent media-time annotations without model predictions."""

import argparse
import json
from pathlib import Path

from drowsyalert.experiments.annotation_review import (
    DraftEvent,
    add_draft_event,
    finalize_annotations,
    load_draft_events,
    load_manifest_worklist,
    load_worklist,
    worklist_summary,
    write_annotations,
    write_draft_events,
    write_worklist,
)

LABEL_KEYS = {
    ord("1"): "drowsy_event",
    ord("2"): "microsleep",
    ord("3"): "yawn",
    ord("4"): "prolonged_eye_closure",
    ord("5"): "head_nod",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    initialize = commands.add_parser("init", help="Create an editable review worklist")
    initialize.add_argument("--manifest", type=Path, required=True)
    initialize.add_argument("--worklist", type=Path, required=True)

    add = commands.add_parser("add", help="Add one independently observed event")
    add.add_argument("--worklist", type=Path, required=True)
    add.add_argument("--draft", type=Path, required=True)
    add.add_argument("--clip-id", required=True)
    add.add_argument("--start", type=float, required=True)
    add.add_argument("--end", type=float, required=True)
    add.add_argument("--label", required=True)

    review = commands.add_parser("review", help="Review one clip with OpenCV controls")
    review.add_argument("--root", type=Path, required=True)
    review.add_argument("--worklist", type=Path, required=True)
    review.add_argument("--draft", type=Path, required=True)
    review.add_argument("--clip-id", required=True)

    export = commands.add_parser("export", help="Validate and export final annotations")
    export.add_argument("--worklist", type=Path, required=True)
    export.add_argument("--draft", type=Path, required=True)
    export.add_argument("--output", type=Path, required=True)
    export.add_argument("--annotation-source", default="independent_human_review")
    export.add_argument("--annotator-id", required=True)
    export.add_argument("--adjudication", required=True)
    export.add_argument("--confidence", default="not_provided")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "init":
        rows = load_manifest_worklist(args.manifest)
        write_worklist(args.worklist, rows)
        print(worklist_summary(rows))
        return 0
    if args.command == "add":
        clips = {row.clip_id: row for row in load_worklist(args.worklist)}
        clip = clips.get(args.clip_id)
        if clip is None:
            raise ValueError(f"Unknown clip ID: {args.clip_id}")
        events = add_draft_event(
            load_draft_events(args.draft),
            clip_id=clip.clip_id,
            start_seconds=args.start,
            end_seconds=args.end,
            label=args.label,
            duration_seconds=clip.duration_seconds,
        )
        write_draft_events(args.draft, events, overwrite=args.draft.exists())
        print(json.dumps({"draft_events": len(events)}, sort_keys=True))
        return 0
    if args.command == "review":
        return _review_clip(args.root, args.worklist, args.draft, args.clip_id)

    annotations = finalize_annotations(
        load_draft_events(args.draft),
        load_worklist(args.worklist),
        annotation_source=args.annotation_source,
        annotator_id=args.annotator_id,
        adjudication=args.adjudication,
        confidence=args.confidence,
    )
    write_annotations(args.output, annotations)
    print(json.dumps({"annotations": len(annotations)}, sort_keys=True))
    return 0


def _review_clip(root: Path, worklist_path: Path, draft_path: Path, clip_id: str) -> int:
    import cv2

    clips = {row.clip_id: row for row in load_worklist(worklist_path)}
    clip = clips.get(clip_id)
    if clip is None:
        raise ValueError(f"Unknown clip ID: {clip_id}")
    video_path = root / Path(clip.relative_path)
    capture = cv2.VideoCapture(str(video_path))
    if not capture.isOpened():
        raise OSError(f"Could not open video for review: {clip.relative_path}")

    events = load_draft_events(draft_path)
    active_label = None
    active_start = None
    paused = False
    frame = None
    window = f"DrowsyAlert independent review - {clip_id}"
    try:
        while True:
            if not paused or frame is None:
                ok, frame = capture.read()
                if not ok:
                    break
            timestamp = max(0.0, capture.get(cv2.CAP_PROP_POS_MSEC) / 1000.0)
            display = frame.copy()
            lines = [
                f"{clip_id}  {timestamp:.3f}s / {clip.duration_seconds:.3f}s",
                "SPACE pause | A/D seek 1s | U undo clip | Q save/quit",
                "1 drowsy | 2 microsleep | 3 yawn | 4 eye closure | 5 head nod",
                (
                    f"active: {active_label or '-'} at "
                    f"{active_start if active_start is not None else '-'}"
                ),
            ]
            for index, line in enumerate(lines):
                cv2.putText(
                    display,
                    line,
                    (12, 28 + index * 28),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.62,
                    (0, 255, 255),
                    2,
                    cv2.LINE_AA,
                )
            cv2.imshow(window, display)
            key = cv2.waitKey(0 if paused else 1) & 0xFF
            if key == ord("q"):
                break
            if key == ord(" "):
                paused = not paused
            elif key in (ord("a"), ord("d")):
                delta = -1.0 if key == ord("a") else 1.0
                target = min(max(timestamp + delta, 0.0), clip.duration_seconds)
                capture.set(cv2.CAP_PROP_POS_MSEC, target * 1000.0)
                ok, candidate = capture.read()
                if ok:
                    frame = candidate
                paused = True
            elif key == ord("u"):
                indices = [index for index, event in enumerate(events) if event.clip_id == clip_id]
                if indices:
                    events.pop(indices[-1])
                    _save_draft(draft_path, events)
            elif key in LABEL_KEYS:
                selected = LABEL_KEYS[key]
                if active_label is None:
                    active_label, active_start, paused = selected, timestamp, True
                elif active_label != selected:
                    active_label, active_start = selected, timestamp
                elif active_start is not None and timestamp > active_start:
                    events = add_draft_event(
                        events,
                        clip_id=clip_id,
                        start_seconds=active_start,
                        end_seconds=timestamp,
                        label=active_label,
                        duration_seconds=clip.duration_seconds,
                    )
                    _save_draft(draft_path, events)
                    active_label = active_start = None
    finally:
        capture.release()
        cv2.destroyAllWindows()
    _save_draft(draft_path, events)
    print(json.dumps({"clip_id": clip_id, "draft_events": len(events)}, sort_keys=True))
    return 0


def _save_draft(path: Path, events: list[DraftEvent]) -> None:
    write_draft_events(path, events, overwrite=path.exists())


if __name__ == "__main__":
    raise SystemExit(main())
