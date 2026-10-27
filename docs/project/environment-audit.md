# Environment Audit

**Audit date:** 2026-10-26
**Scope:** T-002 / T-032–T-035
**Status:** Read-only environment and asset inventory; no dependency installation, model download, dataset download, webcam capture, or application test was performed.

## Runtime and platform

| Item | Observed value | Reproduce |
|---|---|---|
| Host Python | CPython 3.12.11 | `python --version` and `python -c "import platform; print(platform.python_implementation())"` |
| Project virtual-environment Python | 3.12.14 | `.venv\Scripts\python.exe --version` |
| `uv` | 0.12.10 | `uv --version` |
| Operating system | Windows 11 | `python -c "import platform; print(platform.system(), platform.release())"` |
| Architecture | AMD64 | `python -c "import platform; print(platform.machine())"` |

The observed Python versions satisfy the declared `>=3.12,<3.15` range in `pyproject.toml`. This audit intentionally omits hostname, account name, hardware serial numbers, and other unnecessary machine identifiers.

## Dependency and lock status

- `pyproject.toml` and `uv.lock` are present at the repository root.
- `uv lock --check --offline` resolved 64 locked packages successfully when `UV_CACHE_DIR` was set to the ignored project-local `.uv-cache` directory.
- The default global `uv` cache could not be used in the managed workspace because access to it was denied. This is an execution-environment limitation, not evidence that the lockfile is invalid.
- The existing `.venv` can import OpenCV, MediaPipe, Pillow, Matplotlib, pytest, and Ruff.
- The existing `.venv` cannot import PyTorch or scikit-learn. The CNN training environment is therefore incomplete. Use the declared `cnn` or `train` extras only after the dataset and training prerequisites are approved.

Recheck the locked dependency graph without downloading packages:

```powershell
$env:UV_CACHE_DIR = (Join-Path (Resolve-Path '.').Path '.uv-cache')
uv lock --check --offline
```

Recheck optional modules:

```powershell
.\.venv\Scripts\python.exe -c "import importlib.util; names=['torch','PIL','sklearn','matplotlib','pytest','ruff']; [print(n, importlib.util.find_spec(n) is not None) for n in names]"
```

## Local assets and fixtures

| Location | Observation | Readiness impact |
|---|---|---|
| `data/` | Documentation/placeholders only; no dataset samples | CNN preparation/training and held-out evaluation cannot begin |
| `models/` | Documentation/placeholders only; no face-landmarker asset or CNN checkpoint | Webcam/video landmark inference and CNN inference lack required local model assets |
| `demo/` | Contains `demo/app.py`; no non-personal video fixture | Repeatable recorded-video acceptance needs an approved fixture |

No personal recording or restricted dataset was inspected or created. Dataset availability, license suitability, labels, subject/session grouping, and temporal annotations remain unresolved research prerequisites.

## Version-control checkpoint

- Current branch observed during the audit: `master`.
- The worktree contains substantial pre-existing uncommitted restructuring, including root-level project files and removal of the former `my-project` path.
- Per the approved branch policy, do not create the feature/task branch chain until this starting state has been reviewed and preserved in an explicit baseline checkpoint.
- This audit does not classify the pre-existing changes as correct or complete.

**Checkpoint resolution:** After owner approval, the staged root migration was checked for whitespace errors, high-confidence secret patterns, private/generated paths, and staged blobs larger than 1 MiB. The reviewed baseline was committed as `3f717de` on `checkpoint/root-layout`; `feature/001-drowsyalert` was created from that commit and `master` was left unchanged.

## T-002 conclusion

The base Python/OpenCV/MediaPipe development environment is present and the lockfile is internally resolvable offline. CNN training is not ready because PyTorch and scikit-learn are unavailable in the current environment and no approved dataset exists. End-to-end landmark or CNN execution is also blocked by missing local model assets and the absence of an approved recorded-video fixture. These are recorded prerequisites, not successful implementation or evaluation results.

## T-003 dependency and layout review

The root project layout matches the approved plan: package code is under `src/drowsyalert/`, command wrappers are under `scripts/`, automated checks are under `tests/`, and local data/model/output areas are separated from tracked source. The CLI entry point and Hatch build target in `pyproject.toml` point to the same package layout.

Declared dependencies have a requirement-backed role:

| Dependency group | Declared packages | Observed responsibility | Review result |
|---|---|---|---|
| Runtime | NumPy, OpenCV, MediaPipe, PyYAML | Geometry/types, video and crops, face landmarks, YAML configuration | Retain |
| `cnn` extra | PyTorch | Optional CNN inference | Retain optional and lazily loaded |
| `train` extra | PyTorch, Pillow, scikit-learn, Matplotlib | Training, data preparation, metrics, figures | Retain outside the base runtime |
| Development | pytest, Ruff | Automated checks and linting | Retain |

No new dependency or project-layout change is justified in Phase 1. The following implementation gaps are expected work already represented by later tasks:

- `src/drowsyalert/experiments/` is only a package marker; experiment runner and metrics remain T-022/T-025 work.
- Focused source, pipeline, decision, CNN-inference, and experiment-metric test modules named by the plan are not all present yet.
- PyTorch and scikit-learn are not installed in the current `.venv`; installation waits for the approved CNN/data work.
- Model assets, a CNN checkpoint, approved datasets, and a repeatable non-personal video fixture are absent.
- Several current user-facing README files use Vietnamese while Constitution Principle VII requires consistent English documentation. This is a documentation-convergence item and must be corrected before final delivery; it does not justify architecture or dependency changes.
- Values in `configs/config.yaml` are provisional defaults and lack experiment provenance until the run-record work is implemented.

Phase 1 conventions are recorded in `docs/project/development-conventions.md`. The Git baseline still requires a reviewed checkpoint before feature/task branches or commits are created.

## Phase 4 asset update

**Update date:** 2026-10-26

This update records assets acquired or produced after the read-only Phase 1 audit above. It does
not alter the historical observations made during that audit.

| Asset | Local evidence | Provenance / readiness |
|---|---|---|
| MediaPipe Face Landmarker | `models/pretrained/face_landmarker.task`; 3,758,596 bytes; SHA-256 `64184e229b263107bc2b804c6625db1341ff2bb731874b0bcc2fe6544e0bc9ff` | Downloaded by `drowsyalert --download-model` from MediaPipe's configured Google Cloud Storage model URL (`face_landmarker/float16/latest/face_landmarker.task`). Loaded successfully by MediaPipe and returned the expected `No face` result for a synthetic blank frame. |
| CEW EyeCNN checkpoint | `models/checkpoints/eye_cnn.pt`; SHA-256 `40f39307be277e61201c303c85dc2542dc81ab6593958f06c85b1a9bf8befd85` | Locally trained and validation-selected in Phase 3; held-out CEW Accuracy 0.907967. |

Both files remain excluded from Git. The Face Landmarker URL contains `latest`, so reproducibility
depends on the recorded file hash rather than assuming that a future download has identical bytes.
