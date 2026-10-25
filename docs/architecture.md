# DrowsyAlert Architecture

This document describes the current folder boundaries and data flow. The repository root is the Python application and Spec Kit workspace. Application code, research documents, and specifications share this root with clearly separated directories.

## Application layout

```text
repository-root/
├── pyproject.toml, uv.lock       # package, dependencies and locked environment
├── configs/                      # runtime YAML configuration
├── src/drowsyalert/               # reusable application code
│   ├── main.py                   # thin CLI entry point
│   ├── types.py                  # shared observation/result records
│   ├── detection/                # face detection and landmark adapter
│   ├── features/                 # EAR/MAR geometry, temporal features, extra cues
│   ├── models/                   # eye-state backends, CNN, training and dataset prep
│   ├── pipeline/                 # video source, orchestration, decisions and alerts
│   ├── experiments/              # experiment execution and comparison code
│   ├── utils/                    # configuration and presentation helpers
│   └── assets/                   # packaged runtime assets such as the alert sound
├── scripts/                      # thin preparation, download and training commands
│   └── manual/                   # exploratory/manual scripts, not automated tests
├── demo/                         # demo entry point and demo-only static assets
├── tests/                        # automated tests for the package
├── data/                         # local raw, processed and consented data
├── models/                       # local pretrained assets and trained checkpoints
├── outputs/                      # generated results, figures and logs
├── notebooks/                    # optional exploratory notebooks
└── docs/                         # application architecture and usage documentation
```

`src/drowsyalert/models/` contains Python code. The top-level `models/` contains downloaded model files and checkpoints only. Keeping those names distinct by their paths avoids mixing executable source with generated or third-party weights. Likewise, `src/drowsyalert/experiments/` is for tracked experiment code; `outputs/` is for generated artifacts.

## Responsibilities and dependency direction

| Area | Responsibility | Depends on |
| --- | --- | --- |
| `pipeline/source.py` | Read local camera/video frames and source timestamps | OpenCV |
| `detection/face.py` | Produce face landmarks, eye crops and geometric observations | MediaPipe adapter, geometry/types |
| `features/geometry.py` | Pure landmark geometry such as EAR and MAR | NumPy |
| `models/ear.py`, `models/eye_cnn.py` | Estimate eye state from landmark geometry or CNN crops | Types; CNN path additionally uses optional PyTorch |
| `features/temporal.py`, `features/extra.py` | Track time-weighted closure, PERCLOS, yawns and pose cues | Types, geometry and configuration |
| `pipeline/decision.py` | Convert temporal evidence into a status and reason | Feature records and config |
| `pipeline/alerts.py`, `utils/overlay.py` | Audio/display side effects | Decision and observation records |
| `pipeline/realtime.py` | Compose input, vision, features, decision and presentation | The modules above |
| `experiments/` | Run methods on specified data and write comparable records | Reusable detection/feature/decision modules; no UI/audio dependency |
| `scripts/` | Provide thin command wrappers for preparation/training/manual work | Installed `drowsyalert` package |

Algorithm modules should not open cameras, draw overlays or play sound. Presentation and experiment execution consume the same typed outputs so decisions can be tested without a webcam.

## Runtime data flow

```text
camera/video
  -> timestamped frame
  -> face and landmark observation
  -> eye regions + EAR geometry
       ├── landmark eye-state estimate -> primary PERCLOS research path
       └── CNN eye-state estimate      -> separately identified classifier path
  -> temporal features + optional yawn/head-pose cues
  -> named decision method (A/B/C)
       ├── live demo: status, overlay and optional audio
       └── experiment: per-frame/event records and metrics
```

A missing face, invalid crop, invalid landmark, uncertain prediction or excessive timestamp gap is unknown evidence. It is never silently converted to an open-eye observation. Live webcam timestamps use a monotonic clock; recorded-video timestamps use media time. The selected source and timebase are recorded with outputs.

## Data and generated artifacts

- `data/` holds local source/processed/volunteer material. Raw or personal recordings must not be committed.
- `models/pretrained/` holds acquired inference assets; `models/checkpoints/` holds locally trained model checkpoints. Their provenance/configuration belongs in metadata or documentation.
- `outputs/results/`, `outputs/figures/`, and `outputs/logs/` hold generated artifacts and remain outside version control by default.
- `src/drowsyalert/assets/` contains assets needed at runtime and packaged with the application. `demo/assets/` is reserved for demo-only resources.
- `tests/` holds automated checks; `scripts/manual/` holds exploratory scripts that require manual execution.

The `.gitignore` files preserve empty directory placeholders and README guidance while excluding local data, model weights, environments, caches and generated output.

## Maintenance rules

- Keep the `drowsyalert` package name and CLI entry point stable.
- Keep reusable algorithms under `src/drowsyalert/`; keep command wrappers under `scripts/` and UI/demo wiring under `demo/` or the pipeline composition root.
- Add experiment code under `src/drowsyalert/experiments/`; never place executable experiment logic in `outputs/`.
- Keep dependency groups proportionate: OpenCV/MediaPipe for runtime, PyTorch optional for CNN, and training-only libraries in the training extra.
- Update this document when folder responsibilities or data-flow contracts change.
