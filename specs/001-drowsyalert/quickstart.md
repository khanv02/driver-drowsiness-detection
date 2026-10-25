# DrowsyAlert Validation Quickstart

This guide describes validation paths for the local CLI and planned research workflow; it does not claim assets, datasets or measured results already exist. Run commands from the repository root.

## Prerequisites

Use a Python version allowed by `pyproject.toml` and `uv`. The face-landmarker asset is needed for analysis; CNN mode also needs a compatible trained checkpoint. Data and outputs stay local.

```powershell
uv sync
uv run pytest
uv run ruff check src scripts demo tests
uv run drowsyalert --download-model
```

Do not train until dataset source/version, license, labels, grouping and split manifest have been reviewed. The current downloader URL is a candidate, not an approved source.

## Repeatable recorded-video check

With a permitted clip and face asset, process the same video twice under the same configuration. Verify media timestamps, method/source, coverage/readiness, status/reason and run metadata. Offline replay must not play audio.

```powershell
uv run drowsyalert --video <local-video> --headless --log outputs/logs/replay-a.csv
uv run drowsyalert --video <local-video> --headless --log outputs/logs/replay-b.csv
```

The runs should use matching media-time inputs and configuration. Explain any differences before treating them as experimental evidence.

## Webcam acceptance

After recorded processing is stable, verify camera start/stop, visible normal/warning/unavailable states, audible warning/cooldown and `--mute` behavior. A live demo is not held-out evaluation.

```powershell
uv run drowsyalert --camera 0
uv run drowsyalert --camera 0 --mute
```

## Research validation gates

1. Record data provenance and verify group-disjoint splits, class counts, labels, invalid files and duplicates.
2. Train only after eye labels are checked; select using validation; report held-out confusion matrix and class metrics.
3. Confirm annotations contain temporal onset/end on clip timebase. Without these, do not claim event latency/recall.
4. Replay each held-out clip under A/B/C with frozen shared protocol; export event matches, misses, false alarms, latency and valid/unknown coverage.
5. Stratify robustness only when condition/sample counts support interpretation. Preserve config, split, data/model IDs and environment.

See [contracts/cli.md](contracts/cli.md) for the interface and [data-model.md](data-model.md) for records. Dataset-specific prep/experiment commands must be finalized after dataset and annotation decisions, before TASKS.
