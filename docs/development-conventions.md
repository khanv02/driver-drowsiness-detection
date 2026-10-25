# Development Conventions

This document defines the Phase 1 conventions for configuration, tests, local data, generated artifacts, and recoverable task execution. It does not approve research thresholds or claim that datasets, model assets, or results exist.

## Configuration

- `configs/config.yaml` contains local runtime defaults. Numeric values are starting values for development and demonstrations; they are not validated safety thresholds or measured research findings.
- `src/drowsyalert/utils/config.py` is the typed configuration boundary. Unknown fields, non-finite/non-positive numbers, fractions outside `(0, 1]`, invalid integer fields, and inconsistent window settings must be rejected.
- Paths in configuration are resolved from the repository root. Credentials, participant identifiers, absolute personal-data paths, and machine-specific secrets must not be added to tracked configuration.
- An experiment must serialize its fully resolved configuration, including method, eye-state source, thresholds, windows, gap/coverage rules, timestamp policy, event-matching rule, audio state, and data/model/code identifiers.
- Display, headless, and mute options may change side effects but must not change algorithmic decisions.

## Test organization

| Behavior | Primary test location | Required coverage |
|---|---|---|
| Configuration and alert side effects | `tests/test_alerts_config.py` | Invalid config, missing assets, mute, cooldown, stop behavior |
| Geometry, landmark EAR, and validity | `tests/test_detection.py` | Normal, boundary, malformed, no-face, and invalid-eye evidence |
| Timestamp temporal behavior and decisions | `tests/test_temporal.py` | Irregular timestamps, gaps, coverage, closure duration, thresholds, unknown state |
| CNN data and inference boundaries | `tests/test_cnn_dataset.py` plus focused files added by Phase 3 | Label mapping, splits, preprocessing, checkpoint compatibility, uncertainty |
| Source and pipeline integration | `tests/test_source.py`, `tests/test_pipeline.py` when added | Camera/video abstraction, EOF/failure, timestamps, repeatable replay |
| Experiment measures | `tests/test_metrics.py` when added | Event matching, false alarms, misses, coverage, latency |

Core behavior tests must include normal, boundary, and invalid inputs. Hardware-dependent webcam/audio checks are recorded separately in `docs/verification.md`; a skipped manual check is never reported as passed. Training runs and held-out research evaluation are not part of the fast unit-test path.

## Data, models, and outputs

- `data/raw/` stores acquired source material; `data/processed/` stores derived samples/manifests; `data/volunteer/` stores consented participant material. Raw/private media remains outside Git.
- `models/pretrained/` stores acquired face/vision assets; `models/checkpoints/` stores trained checkpoints plus metadata; `models/exported/` stores distributable exports where licensing permits.
- `outputs/results/`, `outputs/figures/`, and `outputs/logs/` store generated artifacts. Reported results must remain traceable to immutable run/config/data/model identifiers.
- Tracked README files describe placement and provenance. `.gitkeep` files preserve empty structure. Neither is evidence that the associated data or model exists.
- Volunteer collection requires the consent and governance decision recorded as G0-09 before capture. Dataset use requires a verified source, license, labels, and split protocol.

The root `.gitignore` excludes local environments, credentials, raw/processed/volunteer data, downloaded/trained model assets, generated outputs, caches, and experiment trackers while allowing README and `.gitkeep` documentation.

## Task and branch workflow

- Decompose each parent work package into small leaf tasks before implementation.
- A leaf task identifies its parent, dependencies, affected paths, verification, and recovery branch.
- After the dirty starting worktree is reviewed and checkpointed, create `feature/001-drowsyalert`, then use `task/T-###-slug` branches for leaf tasks.
- Review the focused diff and verification evidence before merging a task branch.
- Recover by abandoning an unmerged task branch or reverting its commit. Do not rewrite shared history or use destructive resets as routine recovery.

## Phase 1 verification commands

These commands inspect policy without creating private data:

```powershell
git check-ignore -v data/private-placeholder.mp4
git check-ignore -v models/checkpoints/private-placeholder.pt
git check-ignore -v outputs/results/private-placeholder.csv
```

All three paths must be ignored by the root `.gitignore`.

**Verified 2026-10-26:** `git check-ignore -v` matched `data/private-placeholder.mp4` to `/data/**`, `models/checkpoints/private-placeholder.pt` to `/models/**`, and `outputs/results/private-placeholder.csv` to `/outputs/**`. No placeholder file was created.
