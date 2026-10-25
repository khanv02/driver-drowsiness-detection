# Verification Record

This record separates automated evidence from hardware/model/data checks that were unavailable. A skipped manual check is not reported as passed.

## Phase 2 — Landmark and PERCLOS baseline

**Date:** 2026-10-26

**Branch:** `phase/2-landmark-perclos`

**Scope:** T-005–T-009 / G2

### Automated evidence

| Area | Evidence | Result |
|---|---|---|
| Webcam/video source contract | Fake OpenCV capture tests cover open failure, video EOF, camera read failure, cleanup, live monotonic time, media time, and FPS fallback | Passed |
| Face and eye validity | Landmark fixtures cover malformed landmarks, no face, multiple faces, out-of-frame/degenerate eyes, and independent left/right validity | Passed |
| Landmark eye state | Tests cover bilateral closure, threshold equality, one-eye invalid policies, invalid/non-finite EAR, source identity, and reason text | Passed |
| Timestamp PERCLOS | Hand-calculated sequences cover irregular intervals, rolling-window clipping, unknown/gap exclusion, coverage/readiness, closure reset, invalid timestamps, and metadata | Passed |
| Baseline integration | Fake replay connects timestamped frames, face observations, landmark EAR, temporal tracking, decisions, silent replay, and CSV records | Passed |

Commands executed from the repository root:

```powershell
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
.\.venv\Scripts\ruff.exe check src scripts demo tests
```

Observed result:

- `41 passed, 1 skipped` in the automated suite.
- Ruff reported `All checks passed!`.
- The skipped test is the optional CNN/PyTorch path; Phase 2 uses landmark EAR and makes no CNN accuracy claim.

### Traceable Phase 2 behavior

- `FrameSample.source_kind` distinguishes `live_monotonic` from `video_media` time.
- Camera read failure raises an input error and cannot reuse a stale frame; recorded-video EOF ends normally.
- No face and multiple faces are explicit invalid observations.
- Each eye has independent crop, box, EAR, and validity state.
- Landmark EAR evidence identifies its source as `landmark_ear`.
- Bilateral closure requires both valid eyes below the configured threshold. One valid open eye establishes open; one closed eye with the other invalid remains unknown.
- PERCLOS uses valid timestamp intervals, excludes unknown/gaps, reports valid seconds and coverage, and includes source and window bounds.
- Headless replay is silent and exports input kind, method, eye source, observation/eye reasons, valid seconds, coverage, readiness, and window metadata.

### Manual and asset-dependent checks

| Check | Status | Reason / follow-up |
|---|---|---|
| Physical webcam start/stop/disconnect | Not run | No hardware acceptance was requested or available in this execution environment; perform under T-018/T-028 on the declared demo machine. |
| Real MediaPipe Face Landmarker inference | Not run | `models/pretrained/face_landmarker.task` is absent; downloading remains an explicit user-authorized action. |
| Real recorded-video codec replay | Not run | No approved non-personal fixture is present. T-024 governs evaluation videos; a small permitted integration fixture may be added earlier with provenance. |
| Audible alert | Not run | Belongs to Phase 4 T-017/T-018 and requires a real audio environment. |

### G2 conclusion

The deterministic landmark/PERCLOS baseline passes its automated normal, boundary, invalid, and integration checks. G2 is accepted for code progression with the asset-dependent checks above explicitly pending. This gate establishes implementation behavior only; it does not demonstrate real-world accuracy, model quality, alert effectiveness, or achievement of the `>=0.90` research targets.

## Phase 3 — CNN eye classification

**Date:** 2026-10-26

**Branch:** `phase/3-cnn-eye-classification`

**Scope:** T-010–T-014 / G3

### Automated evidence

| Area | Evidence | Result |
|---|---|---|
| Dataset authority | CEW research/non-commercial acquisition and no-redistribution procedure documented; unknown-license Kaggle source rejected | Code/documentation complete; local CEW files pending |
| Dataset preparation | Synthetic tests cover labels, ambiguity, unreadable input, exact duplicates, group leakage, deterministic splits, manifest schema, hashes, and provenance | Passed |
| Training | Tests cover deterministic seeds, strict manifest loading, validation-only selection, early checkpoint metadata, and a tiny synthetic training/checkpoint smoke path | Passed |
| Held-out metrics | Known confusion matrices cover counts, Accuracy, per-class Precision/Recall/F1, macro F1, invalid inputs, frozen checkpoint/manifest identity, and overwrite prevention | Passed |
| CNN inference | Tests cover per-eye probabilities, uncertainty band, bilateral policy, partial/invalid crops, checkpoint failures, explicit source identity, and runtime CSV provenance | Passed |

Commands executed from the repository root:

```powershell
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider -q
.\.venv\Scripts\python.exe -m ruff check src scripts demo tests
```

Observed result:

- `78 passed` in the full automated suite.
- Ruff reported `All checks passed!`.
- `data/raw/cew/` was not present.
- Git ignore checks confirmed raw data, checkpoints, and generated results remain excluded.

### Completed code paths

- A manually acquired CEW archive can be hashed without any automatic download or extraction.
- Preparation emits deterministic group-disjoint train/validation/test manifests, source and
  processed hashes, split/class counts, transformations, and explicit identity-separation
  warnings.
- Training uses train/validation only and selects checkpoints strictly by validation macro F1.
- Held-out evaluation verifies the exact checkpoint/manifest identity, records the frozen
  probability threshold, refuses result overwrite, and reports the required aggregate metrics.
- Runtime CNN evidence is named `cnn_eye_classifier`, keeps nullable per-eye probabilities,
  withholds uncertain/unilateral-closed evidence, and records threshold, uncertainty margin,
  and checkpoint SHA-256. Landmark evidence remains separately named `landmark_ear`.

### Dataset-dependent checks

| Task | Status | Required follow-up |
|---|---|---|
| T-075 | Blocked | Owner downloads the CEW eye-patch archive from the official page and extracts it under `data/raw/cew/`; then record archive identity, actual layout, counts, duplicate/group statistics, and manifest hashes. |
| Real-data T-012 | Blocked | Prepare verified CEW, train with the documented fixed protocol, and retain the ignored checkpoint/run artifacts. |
| T-086 | Blocked | Freeze the checkpoint and threshold, evaluate the real held-out split once, and report actual metrics and whether Accuracy >=0.90. |

### G3 conclusion

The Phase 3 software path passes all automated checks, but G3 is **blocked on real-data
evidence**. Eighteen of twenty Phase 3 leaf tasks are complete; T-075 and T-086 require the
owner-provided CEW archive. No trained CEW checkpoint, held-out CEW metric, accuracy claim,
or real-world drowsiness-performance claim exists yet.
