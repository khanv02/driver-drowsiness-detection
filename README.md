# DrowsyAlert

## What is it?

DrowsyAlert is a local research prototype for driver drowsiness cues from a webcam or recorded video. It detects facial landmarks, estimates eye state using EAR or an optional CNN, calculates time-based PERCLOS, and can add yawning or head-pose cues. Live use displays a status overlay and can play an audible warning; recorded video can be processed headlessly and logged for repeatable review.

This is an advisory research tool, not a certified driver-safety system or medical device. It does not replace safe driving practices or official vehicle safety measures. Accuracy ≥ 0.90 is a research goal, not an established result.

## Current capabilities and limits

- Local webcam and recorded-video input with timestamps.
- Face landmarks, eye-region extraction, and EAR-based eye-state estimation (default backend).
- Optional CNN eye-state inference, training, dataset preparation, and evaluation scripts.
- Time-weighted PERCLOS, prolonged eye-closure indication, and explicit unknown observations.
- Selectable decision methods: `perclos`, `perclos-yawn`, and `perclos-head-pose`.
- Visual overlay, optional CSV logging, and headless processing. Audible playback is currently supported on Windows.
- Automated tests for selected temporal, geometry, dataset preparation, configuration, and alert behavior.

The Face Landmarker asset and trained CNN checkpoint are not stored in Git. EAR mode does not require a CNN checkpoint. CNN mode requires a compatible checkpoint. Missing model assets are reported as errors rather than silently substituted.

## Requirements

- Python 3.12 is selected in `.python-version`; `pyproject.toml` permits Python `>=3.12,<3.15`.
- [uv](https://docs.astral.sh/uv/) for environment and dependency management.
- A webcam for live use; recorded video can be used without a camera.
- The Face Landmarker asset for video or webcam processing. Initial download requires network access; inference uses the local asset.
- PyTorch is optional for EAR use and required for CNN inference/training.

## Install and run

Run commands from the repository root:

```powershell
uv sync
uv run drowsyalert --download-model
uv run drowsyalert --camera 0 --eye-backend ear
```

To use a trained CNN checkpoint:

```powershell
uv sync --extra cnn
uv run drowsyalert --camera 0 --eye-backend cnn --checkpoint models/checkpoints/eye_cnn.pt
```

To process a video without opening a display window or playing audio:

```powershell
uv run drowsyalert --video path/to/video.mp4 --headless --log outputs/logs/run.csv
```

Available decision methods:

```powershell
uv run drowsyalert --camera 0 --method perclos
uv run drowsyalert --camera 0 --method perclos-yawn
uv run drowsyalert --camera 0 --method perclos-head-pose
```

The default configuration is `configs/config.yaml`. Its thresholds and temporal settings are configurable defaults, not experimentally validated driver-safety thresholds. Use `uv run drowsyalert --help` to see all command-line options.

## Prepare data and train the CNN

Review dataset availability, terms, provenance, labels, and intended use before training. The download helper targets a public Kaggle archive, but availability and permission to use or redistribute it are not guaranteed. Keep raw and processed data in the ignored `data/` directory.

```powershell
uv sync --extra train
uv run python scripts/download_dataset.py
uv run python scripts/prepare_dataset.py --input data/raw/kaggle --output data/processed --seed 42
uv run python scripts/train_model.py --manifest data/processed/manifest.csv --checkpoint models/checkpoints/eye_cnn.pt --output outputs/results/eye_cnn
```

If subject/session metadata is available, pass a `--groups` CSV with `source,group_id` columns. Without metadata, grouping by source and duplicate-image checks cannot guarantee subject-independent evaluation. Inspect labels, split report, and data quality before interpreting metrics. Use the test split only for final evaluation, not model or threshold selection.

## Configuration and generated files

`configs/config.yaml` contains model paths, EAR/CNN and auxiliary-feature thresholds, temporal-window settings, camera dimensions, and alert cooldown. `--config` selects another YAML file; supported command-line options can override runtime selections.

- `data/raw/` and `data/processed/`: local datasets and prepared eye samples.
- `data/volunteer/`: consented participant recordings; never commit these files.
- `models/pretrained/`: downloaded face model.
- `models/checkpoints/`: trained CNN checkpoints.
- `outputs/results/`, `outputs/figures/`, and `outputs/logs/`: generated experiment results.

The contents of these data, model, and output directories are ignored by Git; README files and `.gitkeep` placeholders are retained. Record dataset provenance, license, labels, split, model/configuration, thresholds, random seed, and evaluation protocol with reported results. Webcam processing is local by default. Do not publish participant recordings without consent and authorization.

## Tests and lint

```powershell
uv run ruff check src scripts demo tests
uv run pytest
```

Automated tests use synthetic fixtures for core behavior where possible. Passing tests do not establish real-world detection accuracy. Webcam and audio checks require local hardware and should be recorded separately from automated test results.

## Repository layout

```text
.
├── configs/                 # Runtime configuration
├── data/                    # Local data; ignored except guidance/placeholders
├── demo/                    # Optional demo entry point
├── docs/                    # Architecture and project documentation
├── models/                  # Local pretrained assets and checkpoints
├── outputs/                 # Generated results, figures, and logs
├── scripts/                 # Download, preparation, and training wrappers
├── src/drowsyalert/         # Application package
│   ├── detection/           # Face and landmark observations
│   ├── features/            # Geometry, PERCLOS, yawning, and pose
│   ├── models/              # EAR/CNN inference and training/data logic
│   ├── pipeline/            # Sources, decisions, alerts, orchestration
│   └── utils/               # Configuration and overlay
└── tests/                   # Automated tests
```

See [docs/architecture.md](docs/architecture.md) for module responsibilities and data flow.

## Research documents

- [Project #12 description](docs/de-tai-12-drowsyalert.md)
- [Official instructor brief](docs/PhieuMoTaDeTai_30DeTai_ThiGiacMayTinh_NCKH.docx)
- [Software requirements specification](specs/001-drowsyalert/spec.md)
- [Implementation task breakdown](specs/001-drowsyalert/tasks.md)
