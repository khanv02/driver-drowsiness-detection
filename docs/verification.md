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
| Dataset authority | Official CEW extraction, research/non-commercial terms, package layout, counts, pair groups, input tree hash, and manifest hash recorded; unknown-license Kaggle source rejected | Passed |
| Dataset preparation | Tests cover labels, ambiguity, unreadable input, exact duplicates, CEW folder mapping/pairs, group leakage, deterministic splits, manifest schema, hashes, and provenance | Passed |
| Training | Deterministic CEW run used train/validation only, expanded a boundary-limited 30-epoch pilot, stopped at epoch 39, and restored validation-selected epoch 34 | Passed |
| Held-out metrics | Frozen checkpoint/manifest/threshold evaluated once on 728 images; Accuracy, confusion matrix, and per-class Precision/Recall/F1 recorded | Passed; Accuracy 0.907967 |
| CNN inference | Tests cover per-eye probabilities, uncertainty band, bilateral policy, partial/invalid crops, checkpoint failures, explicit source identity, and runtime CSV provenance | Passed |

Commands executed from the repository root:

```powershell
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider -q
.\.venv\Scripts\python.exe -m ruff check src scripts demo tests
```

Observed result:

- `79 passed` in the full automated suite.
- Ruff reported `All checks passed!`.
- CEW preparation verified 4,846 readable eye patches and 2,423 pair groups.
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

### Real-data evidence

| Evidence | Result |
|---|---|
| Manifest | SHA-256 `42ebc450eba138301f13df4cd06736b31dab20b7d2fa55464251ed87c765c58f`; train 3,392, validation 726, test 728 |
| Selected checkpoint | Epoch 34; validation Accuracy 0.877410; macro F1 0.877056; SHA-256 `40f39307be277e61201c303c85dc2542dc81ab6593958f06c85b1a9bf8befd85` |
| Held-out confusion matrix | `[[340, 36], [31, 321]]` for open/closed actual rows and predicted columns |
| Held-out classification | Accuracy 0.907967; macro F1 0.907904; open F1 0.910308; closed F1 0.905501 |
| Required Accuracy target | >=0.90 met |

### G3 conclusion

G3 **passed**. All Phase 3 parent and leaf tasks are complete, the reproducible CEW
checkpoint exists locally, and the one-way held-out evaluation met the image Accuracy target.
This establishes CEW open/closed eye classification performance only; it does not establish
video-level drowsiness detection, alert latency, driver safety, or in-vehicle generalization.

## Phase 4 - Real-time drowsiness alert

**Date:** 2026-10-26

**Branch:** `phase/4-realtime-alert`

**Scope:** T-015-T-018 / G4

### Automated and headless evidence

| Area | Evidence | Result |
|---|---|---|
| Decision policy | Boundary, warm-up, unknown-evidence, sustained-closure, PERCLOS, and invalid-input tests | Passed |
| Overlay contract | Pure line-generation tests verify status, reason, observation/source identity, readiness/coverage, advisory, and controls | Passed |
| Audio controller | Injected tests cover first alert, cooldown boundary, recovery, re-alert, mute, missing sound, playback failure, and cleanup | Passed |
| Live integration | Fake live input traverses unknown, normal, alert, mute, camera-read failure, and cleanup paths | Passed |
| CLI integration | Tests verify argument forwarding/rejection and source, checkpoint, and audio metadata | Passed |
| Face model | MediaPipe loaded the ignored model asset and produced the expected `No face` observation for a blank frame | Passed |
| Physical camera smoke | Camera 0 processed five live CNN frames in muted/headless mode; input kind, checkpoint hash, and audio policy were reported | Passed (capture only) |

Physical camera smoke command:

```powershell
uv run drowsyalert --camera 0 --eye-backend cnn --checkpoint models/checkpoints/eye_cnn.pt --headless --mute --max-frames 5
```

Observed metadata: 5 frames, `live_monotonic`, `cnn_eye_classifier`, checkpoint SHA-256
`40f39307be277e61201c303c85dc2542dc81ab6593958f06c85b1a9bf8befd85`, audio policy
`muted`, zero playback failures. No frames or video were saved.

Full verification commands:

```powershell
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider -q
uv run ruff check src scripts demo tests
```

Observed result: `112 passed` and `All checks passed!`. A concurrent `uv run pytest` launch first
encountered a Windows `uv trampoline failed to canonicalize script path` launcher error; executing
the same suite directly with the project virtual environment completed successfully.

### Real webcam and audio acceptance checklist

Run from the repository root in a stationary, safe indoor setting. This is a research prototype;
do not test it while driving. The display may show personal imagery, but the application does not
save webcam frames. Close unrelated camera applications first.

1. Start the visible but muted CNN flow:
   `uv run drowsyalert --camera 0 --eye-backend cnn --checkpoint models/checkpoints/eye_cnn.pt --mute`.
2. Confirm the window shows status and reason, eye source/state, closure time, PERCLOS readiness or
   value, the prototype advisory, and `Q/Esc` controls.
3. Keep both eyes visibly open and record the observed state. During the initial evidence window,
   `UNKNOWN` is valid; after sufficient valid coverage, the expected steady state is `NORMAL`.
4. Close both eyes for at least the configured 2 seconds while seated safely. Confirm `ALERT` and
   a sustained-closure reason. Reopen them and confirm recovery.
5. Press `Q` or `Esc` and confirm a clean exit.
6. Start the same command without `--mute`, lower the system volume first, and repeat step 4.
   Confirm one audible warning and that sound does not block or freeze the video.
7. Optional camera-loss check: with the muted command running, disable or disconnect the selected
   camera only if doing so is safe for the device. Confirm an explicit read error and clean exit;
   do not claim this item if it was not performed.

Evidence template (fill only from direct observation):

| Field | Observation |
|---|---|
| Date / reviewer | Pending |
| Camera index and description | Pending |
| Backend and checkpoint hash | `cnn_eye_classifier`; `40f39307be277e61201c303c85dc2542dc81ab6593958f06c85b1a9bf8befd85` |
| Visible `UNKNOWN` / reason | Pending |
| Visible `NORMAL` / reason | Pending |
| Visible `ALERT` / reason | Pending |
| Recovery to non-alert | Pending |
| Audible warning and nonblocking video | Pending |
| `Q` / `Esc` clean exit | Pending |
| Camera-loss result (optional) | Not performed |
| Notes / failures | Pending |

### G4 status

Automated decision, overlay, audio-controller, live-flow, CLI, asset-loading, and physical camera
capture checks pass. Final G4 reviewer acceptance remains **pending** because visible state changes
and real speaker playback require direct human observation. The headless smoke test is not described
as evidence of either display correctness or audible output. Generated/private boundary checks also
pass: the downloaded face model, trained checkpoint, CEW data, and result artifacts remain ignored.

## Phase 5 - Additional research features

**Date:** 2026-10-26

**Branch:** `phase/5-additional-research-features`

**Scope:** T-019-T-022 / G5

### Automated evidence

| Area | Evidence | Result |
|---|---|---|
| Yawn evidence | MAR shape/finite/width validation; exact ratio and duration boundaries; one event per continuous opening; closure, gap, invalid-observation and rolling-expiry behavior | Passed |
| Head-pose evidence | PnP input validation; positive-pitch convention; fixed and first-valid reference records; exact angle/duration boundaries; invalid-pose and gap resets | Passed |
| Method isolation | A ignores auxiliary cues; B consumes only valid yaw evidence; C consumes only valid pose evidence; shared PERCLOS settings have equal serialized values | Passed |
| Unknown handling | A required-but-unavailable Method B/C cue in the combined-PERCLOS band produces `UNKNOWN`, never unsupported normality | Passed |
| Experiment records | Versioned/deterministic identities, config hash, JSON round-trip, stable CSV fields, completion/error states, and overwrite refusal | Passed |
| Privacy/provenance | Raw-frame fields are rejected; video identity defaults to content hash; missing dataset/split/code IDs are explicit; private/generated paths remain ignored | Passed |

Verification commands:

```powershell
uv sync --extra train
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider -q
uv run ruff check src scripts demo tests
git check-ignore -v outputs/results/phase5-run.json outputs/logs/phase5.csv `
  data/private/participant.mp4 models/checkpoints/private.pt
```

Observed result: `143 passed` in 26.56 seconds and Ruff reported `All checks passed!`.
The first full-suite collection attempt found that the local environment no longer had
the declared training extra installed (`scikit-learn`). `uv sync --extra train` restored
the locked dependencies. The next run exposed one old fixture that supplied auxiliary
counts without validity flags; the fixture was corrected to represent valid evidence,
and the final full suite passed.

Ignore checks matched all four representative private/generated paths. The tracked
entries under `data/`, `models/`, and `outputs/` are documentation or empty directory
placeholders; no raw recording, trained checkpoint, or generated result was added.

### G5 status

Phase 5 software behavior and automated acceptance evidence **pass**. T-019, T-020,
T-021, and all T-022 implementation leaves are complete. Numerical yawn/pose values
remain provisional configuration defaults and must be selected on validation material
and frozen under the Phase 6 protocol before any held-out comparison.

Formal G5 closure remains **pending** only because parent T-022 declares T-018 as a
dependency, while T-018/G4 still awaits the deferred human-visible webcam and real-speaker
acceptance check. This hardware limitation does not invalidate the automated Phase 5
implementation and no visual/audio success is inferred from it.

## Phase 6 - Experimental evaluation foundation

**Date:** 2026-10-26

**Branch:** `phase/6-experimental-evaluation`

**Status:** NITYMED acquired, Protocol v1 approved, and preparation/evaluation tooling
verified; independent labels, participant-safe split, and real results pending.

Completed preparatory evidence:

- Candidate temporal-video sources and current local inventory were audited without
  downloading or claiming a dataset.
- Evaluation Protocol `drowsyalert-video-eval-v1` freezes A/B/C controls, independent
  microsleep reference labels, secondary yaw reporting, subject/session separation,
  -1/+2-second matching, latency, false alarms, unknown coverage, 1-second system
  Accuracy, conditions, privacy, validation-only selection, and no volunteer collection.
- A strict annotation CSV loader validates finite media bounds, final adjudication,
  approved label/condition values, stable clip identities, duplicates, circular
  detector-derived labels, and subject/session leakage. It stores no frame pixels.
- Parameterized metrics validate intervals and compute chronological one-to-one matches,
  event TP/FP/FN, precision/recall/F1, false alarms per valid hour, signed latency
  distributions, misses, and observation coverage. Matching tolerances have no defaults.
- The acquired NITYMED HDTV720 tree contains 126 decode-verified videos and an ignored
  per-video hash/metadata manifest. The provider count discrepancy, 24 FPS outlier, lack
  of temporal labels, and missing participant mapping are recorded.
- A local annotation worklist/review tool records human-observed media-time intervals,
  refuses circular detector labels, and blocks final export until review/split metadata
  satisfies the strict annotation contract.
- Fixed-bin system Accuracy retains UNKNOWN in the primary denominator and reports
  observed-only Accuracy/coverage separately. Alert episode extraction and grouped
  condition calculations use explicit parameters.
- The evaluator joins annotations and run records into separate event, latency,
  coverage, failure, condition, and processing summaries.
- The resumable batch runner fixes a common clip set, landmark-EAR source, shared config,
  data/split/config/code identities, and forced headless/muted execution across A/B/C.
  It rejects incompatible existing outputs and requires a numeric frozen pose reference.

Verification commands:

```powershell
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider -q
uv run ruff check src scripts demo tests
```

Observed result after Protocol v1 approval: `210 passed` in 27.31 seconds and
Ruff reported `All checks passed!`.

This is software, corpus-integrity, and protocol-approval evidence only. T-024/T-139
still require reviewed participant grouping, split, and independent temporal annotations.
No A/B/C performance, alert latency, video Accuracy, or robustness result has been
measured.
