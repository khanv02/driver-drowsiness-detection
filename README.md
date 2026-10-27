<h1 align="center">🚗💤 DrowsyAlert</h1>

<p align="center">CNN-based Driver Drowsiness Detection Research Prototype</p>

<p align="center"><a href="README.vi.md">Tiếng Việt</a> | <strong>English</strong></p>

## Overview

DrowsyAlert is a research application for exploring signs of driver drowsiness from a local webcam or video. It tracks eye state, estimates time-weighted PERCLOS, and supports comparison with yawning or head-pose cues. In live mode, it displays status and can play an audible alert.

This is a research prototype, not a certified safety device or medical diagnostic tool, and it does not replace official road-safety measures. On the CEW test set, the CNN achieved 0.907967 accuracy for eye-image classification. This is not video-based drowsiness detection performance, evidence of road safety, or proof of generalization to real drivers.

## Features

- Capture from a local webcam or read timestamped video.
- Detect faces and landmarks, then crop eye regions.
- Estimate eye state with EAR (default) or an optional CNN.
- Compute time-weighted PERCLOS, track prolonged eye closure, and preserve `UNKNOWN` when observation is lost.
- Select `perclos`, `perclos-yawn`, or `perclos-head-pose`.
- Display overlays, optionally write CSV logs, and run video headlessly.
- Play alerts on Windows; video replay does not play audio.

Face Landmarker assets and CNN checkpoints are not stored in Git. EAR does not require a CNN checkpoint. CNN mode requires PyTorch and a compatible checkpoint.

## Development status

- **Phase 1 — Foundation:** complete (G1).
- **Phase 2 — Landmarks and PERCLOS baseline:** complete (G2), including timestamped webcam/video processing, per-eye validity, `OPEN`/`CLOSED`/`UNKNOWN` EAR states, coverage/readiness, and reproducible headless replay.
- **Phase 3 — CNN eye classification:** complete (G3). The model was selected using validation and evaluated once on the frozen test set: 728 images, accuracy **0.907967**, macro F1 **0.907904**.
- **Phase 4 — Real-time alert:** implementation complete; G4 acceptance is pending direct hardware review. Automated checks reported 112 passed and Ruff passed. A five-frame headless/muted CNN webcam smoke check confirmed capture and metadata only, not the GUI or sound. Direct review must cover state transitions, recovery, stop controls, and audio.
- **Phase 5 — Additional research features:** software acceptance passed (G5). Includes timed yawning events, relative head pose, isolated A/B/C decision evidence, and experiment records with configuration, source, model/dataset provenance, JSON/CSV export, and no raw-frame storage by default. Automated checks reported 143 passed and Ruff passed. Live webcam/speaker acceptance remains a separate hardware check for G4 (T-018).
- **Phase 6 — Experimental evaluation:** in progress. Protocol v1.1, NITYMED source material, and a 12-clip validation set are prepared. Baseline A/B/C runs have low coverage. Configuration is not frozen and no held-out result has been published. Remaining work includes manifest/annotation review, validation-based selection, independent test-set review, a pilot, and final held-out A/B/C evaluation. CEW results measure eye-image classification only.

## Quick links

| Need | Document |
|---|---|
| Browse documentation | [Documentation index](docs/README.md) |
| Run A/B/C experiments | [Evaluation guide](docs/guides/evaluation-execution.md) |
| Current validation baseline | [Validation results v1.1](docs/research/validation-evaluation-v1.1.md) |
| Review test evidence and gates | [Verification record](docs/project/verification.md) |
| Track official work items | [Task list](specs/001-drowsyalert/tasks.md) |

## Technology

| Area | Technology | Purpose |
|---|---|---|
| Language | Python 3.12 | Application and research tools |
| Computer vision | OpenCV, MediaPipe | Video input, landmarks, eye processing |
| Computation | NumPy, PyYAML | Array operations and YAML configuration |
| Optional CNN | PyTorch | Train and run eye classification |
| Data preparation/evaluation | Pillow, scikit-learn, Matplotlib | Optional `train` extra |
| Development | uv, pytest, Ruff | Environment, tests, and linting |

Dependencies are declared in [`pyproject.toml`](pyproject.toml); the Python version is selected in [`.python-version`](.python-version).

## Install and run

Requires Python 3.12 and [uv](https://docs.astral.sh/uv/). Run from the repository root:

```powershell
uv sync
uv run drowsyalert --download-model
uv run drowsyalert --camera 0 --eye-backend ear
```

The first Face Landmarker download requires network access. Webcam processing then uses the local model.

### Run with the CNN

```powershell
uv sync --extra cnn
uv run drowsyalert --camera 0 --eye-backend cnn --checkpoint models/checkpoints/eye_cnn.pt
```

### Process video and choose a method

```powershell
uv run drowsyalert --video path/to/video.mp4 --headless --log outputs/logs/run.csv
uv run drowsyalert --camera 0 --method perclos
uv run drowsyalert --camera 0 --method perclos-yawn
uv run drowsyalert --camera 0 --method perclos-head-pose
```

Default settings are in [`configs/config.yaml`](configs/config.yaml). Its thresholds are initial configuration values and have not been validated as driver-safety thresholds. Run `uv run drowsyalert --help` for other options.

### Live states and controls

- `NORMAL`: valid observation, the PERCLOS window is ready, and no alert threshold has been reached.
- `ALERT`: eyes have remained closed long enough or PERCLOS reached its threshold; the reason is shown in the window.
- `UNKNOWN`: face/eyes are missing, prediction is uncertain, timestamps are invalid, or the window is warming up. `UNKNOWN` is not treated as `NORMAL`.
- Press `Q` or `Esc` to stop. Use `--mute` to silence audio without changing decisions.
- Webcam frames are processed locally and are not saved by the demo. `--log` writes measurement/status CSV only, not video.

The overlay shows eye-state source, status/reason, PERCLOS/coverage, stop controls, and the research-prototype notice.

## Prepare data and train the CNN

Check dataset provenance, terms, labels, and structure before training. The project does not download datasets automatically. Manually obtain the CEW eye-patch dataset from its [official page](https://parnec.nuaa.edu.cn/_upload/tpl/02/db/731/template731/pages/xtan/ClosedEyeDatabases.html), follow its research/non-commercial/no-redistribution terms, and extract it under `data/raw/cew/`. Do not commit datasets or personal data.

```powershell
uv sync --extra train
uv run python scripts/download_dataset.py --archive C:\path\to\CEW-eye-patches.rar
uv run python scripts/prepare_dataset.py --input data/raw/cew/dataset_B_Eye_Images --output data/processed --dataset-name CEW --source-url "https://parnec.nuaa.edu.cn/_upload/tpl/02/db/731/template731/pages/xtan/ClosedEyeDatabases.html" --group-strategy cew-paired-eyes --seed 42
uv run python scripts/train_model.py --manifest data/processed/manifest.csv --checkpoint models/checkpoints/eye_cnn.pt --output outputs/results/eye_cnn-training
```

If person/session metadata exists, pass `--groups` with a CSV containing `source,group_id`. Without it, source grouping and duplicate detection cannot guarantee participant-independent splits. Training uses train/validation only and does not read the test set. Read the [training guide](docs/guides/training.md) before final evaluation.

## Checks

```powershell
uv run ruff check src scripts demo tests
uv run pytest
```

Automated checks cover selected geometry, timing, configuration, data, and alert cases. Passing tests do not establish real-world accuracy. Webcam and audio checks require physical devices and should be recorded separately.

## Project layout

```text
configs/       Runtime configuration
data/          Local datasets; data is not committed
demo/          Demo entry point
docs/          Documentation index, guides, project and research records
models/        Downloaded models and local checkpoints
outputs/       Generated results, figures and logs
scripts/       Data acquisition/preparation and training
src/drowsyalert/ Detection, features, models, pipeline and utilities
tests/         Automated checks
specs/         Official specification, plan and task breakdown
```

## Documentation and privacy

- [Documentation index](docs/README.md)
- [Project 12 description](docs/reference/de-tai-12-drowsyalert.md)
- [Application architecture](docs/project/architecture.md)
- [Project Constitution](.specify/memory/constitution.md)
- [Implementation plan](specs/001-drowsyalert/plan.md)
- [Research decisions](specs/001-drowsyalert/research.md)
- [Requirements specification](specs/001-drowsyalert/spec.md)
- [Task list](specs/001-drowsyalert/tasks.md)

Data under `data/`, models under `models/`, and outputs under `outputs/` are excluded from Git; only README files and `.gitkeep` files are retained. Webcam frames are processed locally by default. Volunteer video collection requires consent and compliance with the responsible institution's guidance.

## Contributing and support

- Read [contribution guidelines](CONTRIBUTING.md) before creating a branch or pull request.
- Follow the [code of conduct](CODE_OF_CONDUCT.md) in discussions and reviews.
- Report bugs or suggestions using the templates in **Issues**.
- Report security vulnerabilities through the [Security Policy](SECURITY.md), not in a public issue.

## Team

| Member | Role | Main responsibilities |
|---|---|---|
| Huỳnh Vĩnh Lợi | Team lead | Guide research questions, scope and priorities; assign and track work; coordinate decisions and review results against the project brief. |
| Cao Thanh Hùng | Secretary | Record meetings, decisions and tasks; maintain documents and activity records; prompt progress updates. |
| Phạm Nguyễn Phúc Khang | Developer | Maintain the repository and configuration; implement and integrate the pipeline/demo; maintain source structure and run instructions. |
| Dương Công Khoa | Testing and data lead | Check requirements, plan and run checks, record defects; track dataset sources/licenses, inspect labels, prepare data, and reduce split leakage. |

Roles may be shared or adjusted. The data lead should document sources, labels, preprocessing, and splits. Volunteer data requires consent and must not be committed.

## License

Released under the [MIT License](LICENSE).
