# Implementation Plan: DrowsyAlert

**Branch**: `phase/6-experimental-evaluation` | **Date**: 2026-10-26 | **Spec**: [spec.md](spec.md)

**Development branch policy**: `main` is the clean shared baseline. Each implementation phase uses a recoverable `phase/<number>-<slug>` branch, and each small leaf task uses `task/T-###-short-description` based on the active phase branch. Verify and review every focused diff, commit it, then merge it into the phase branch. Merge a phase into `main` only after its acceptance gate passes. If a task goes wrong, abandon/recreate its task branch or revert its task commit; do not reset shared branches or start from an uncommitted worktree.

**Input**: Approved behavior in `specs/001-drowsyalert/spec.md`; official Project #12 brief; repository inspection.

## Summary

Deliver a local single-person webcam and recorded-video system with two explicitly separate eye-state sources: 2D landmark EAR for primary PERCLOS research and a lightweight CNN for required eye-image classification and optional secondary integration. Use timestamp-weighted temporal features and explicit unknown states. Compare PERCLOS, PERCLOS+yawning and PERCLOS+head pose on the same held-out, temporally labelled videos. Keep experiments separate from live display/audio. Existing package boundaries and dependencies suffice; verify and fill evaluation gaps without wholesale restructuring.

## Technical Context

**Language/Version**: Python 3.12+ as declared (`>=3.12,<3.15`); above instructor minimum >=3.9, but no claim of 3.9 support.

**Primary Dependencies**: OpenCV for local capture/crops/display; MediaPipe Face Landmarker for face landmarks; PyTorch for the small CNN; NumPy and PyYAML for calculations/configuration. Keep `uv` and `uv.lock`. Training-only extras include Pillow, scikit-learn and Matplotlib. No TensorFlow, dlib, server, database, cloud runtime or frontend framework.

**Storage**: Local YAML configuration, dataset manifests/annotations, model checkpoints, CSV per-frame/event records and summary outputs. Raw/private data and generated results remain outside version control.

**Testing**: pytest and Ruff. Unit-test geometry, temporal aggregation, decisions and event metrics; add focused adapter/CLI integration tests with supplied frames/videos or fakes. Camera acceptance is manual.

**Target Platform**: Student workstation on an OS supported by locked dependencies; local webcam and CPU baseline. Record optional accelerator and audio platform.

**Project Type**: Single Python package with CLI demo and separate research scripts.

**Performance Goals**: Measure throughput and end-to-end warning latency on declared hardware/resolution. SPEC/instructor give no binding FPS/latency threshold; make no real-time guarantee without measurements.

**Constraints**: Local inference after model assets are available; one selected subject; no personal data upload/retention by default; identify landmark/CNN sources separately; unknown observations cannot become normal; model/threshold selection uses validation only.

**Scale/Scope**: Undergraduate study, one subject per run, three required comparison methods, one eye CNN, local datasets, 35–45 page report and slides. Larger volunteer studies and personalized thresholds are optional.

### Technology assessment

| Choice | Responsibility and fit | Alternatives and trade-offs |
| --- | --- | --- |
| Python + uv | Retain current packaging, lockfile and scripts. | Python >=3.9 is a floor; 3.9 support would require compatibility and dependency work not currently justified. |
| OpenCV | Camera/video I/O, conversion/crops, drawing and display; already core. | Another GUI toolkit adds surface area. Camera behavior varies by OS, so recorded video is the reproducible path. |
| MediaPipe Face Landmarker | Local pretrained face/landmark inference; already installed and accepts video timestamps. | dlib is listed by instructor but absent, adding setup/model burden. Verify MediaPipe landmark behavior and asset terms. |
| PyTorch | Train/load CNN and local inference; already an optional extra. | TensorFlow/Keras also qualifies, but duplicate frameworks add maintenance. Keep Torch optional for EAR-only use. |
| Small CNN | Classify open/closed eye crops; current `EyeCNN` is a compact 3-block convolutional model. | A larger pretrained net adds compute and obscures scope. Change architecture only with reason and comparable validation. |
| YAML + CSV/JSON | Simple configs, manifests, records and summaries. | Database/tracking service is unnecessary for this scope. |
| pytest + Ruff | Existing test/lint conventions for algorithms and regressions. | No framework change justified; hardware checks remain manual or mocked. |

## Constitution Check

- **Research-first**: Pass. Landmark PERCLOS is primary; all three methods compared. CNN remains required and distinct.
- **Simplicity**: Pass. Reuse dependencies and package boundaries; no service or framework added.
- **Reproducibility**: Pass with gates for dataset, grouped split, preprocessing, seeds, config and evaluation definitions.
- **Testability/reliability**: Pass. Acquisition, vision, temporal, decisions and presentation are separable; unknown/errors explicit.
- **Incremental delivery**: Pass. Recorded EAR/PERCLOS baseline precedes CNN and live integration.
- **Privacy**: Pass. Local capture, consent/data handling and prototype limits required.
- **Traceability**: Pass. Requirement mapping is included below; unresolved data details stay explicit.

**Gate result**: Pass to design. No principle requires new dependencies or scope. Dataset suitability and single-eye-invalid policy must be resolved before final results.

## Project Structure

### Documentation

```text
specs/001-drowsyalert/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
└── contracts/cli.md
```

The existing `tasks.md` provides the parent work packages; each will be decomposed into small leaf tasks before execution. No HTTP/API contract is needed; local CLI and output files are the system boundary.

### Application and research code (existing repository; proposed target boundaries)

```text
repository-root/
├── src/drowsyalert/
│   ├── main.py                 # thin CLI composition root
│   ├── types.py                # observation/result contracts
│   ├── detection/face.py       # MediaPipe adapter and landmarks
│   ├── features/{geometry,temporal,extra}.py # geometry, durations, cues
│   ├── models/{dataset,train,eye_cnn,ear}.py # preparation, training, inference
│   ├── pipeline/{source,realtime,decision,alerts}.py # input, composition, rules, effects
│   ├── experiments/            # add runner/metrics; currently package marker only
│   └── utils/                  # config and overlay
├── scripts/                    # thin prepare/train/download wrappers
├── configs/config.yaml         # runtime defaults
├── data/                       # local raw/processed/volunteer data, ignored
├── models/                     # local pretrained assets/checkpoints, ignored
├── outputs/{results,figures,logs}/
└── tests/                      # unit and adapter/CLI integration tests
```

**Structure Decision**: Use the repository root as the single Python project root. Application code, configuration, scripts, tests, and tools live beside workspace documentation and Spec Kit artifacts. Preserve the existing source boundaries and keep Torch optional for EAR-only use. The former nested Git metadata is retained in an ignored archive directory.

## Architecture Overview

```text
Webcam or video -> FrameSample(image, source timestamp, kind)
  -> face/landmark adapter -> FaceObservation (landmarks, crops, EAR, validity)
       ├-> landmark EAR state (primary comparison source)
       └-> CNN per-eye state/confidence (separate evaluation/optional ablation)
  -> timestamped temporal features (PERCLOS, closure, yawn/head-pose cues)
       ├-> A/B/C Decision -> visible status/reason -> optional audio
       └-> headless experiment runner -> records -> event metrics/export
```

### Module responsibilities and contracts

| Boundary | Input -> output | Responsibilities and failure behavior |
| --- | --- | --- |
| `pipeline.source.VideoSource` | camera/file -> `FrameSample` or end/error | Local I/O. Webcam uses monotonic elapsed time; video uses media timestamps with disclosed fallback. Camera failure stops decisions; never reuse stale frames. |
| `detection.face.FaceDetector` | frame + time -> `FaceObservation` | Single selected face/2D landmarks. No face, ambiguous face, invalid geometry/crops or inadequate evidence yields unknown with reason. Keep MediaPipe details behind the contract. |
| `features.geometry` | landmark arrays -> EAR/MAR/pose or invalid | Pure calculations; reject malformed/non-finite/degenerate geometry; document coordinates. |
| `models.ear`, `models.eye_cnn` | face observation -> source-tagged per-eye state/confidence and bilateral state | Same CNN preprocessing for train/inference. Preserve per-eye outputs. Invalid crops/model errors are unknown, never open. |
| `features.temporal.TemporalTracker` | increasing timestamp + state -> PERCLOS, coverage, readiness and closure duration | Integrate by elapsed time, not frames. Unknown/gaps excluded from numerator/denominator and break closure continuity. |
| `features.extra.ExtraTracker` | face observation + time -> yawn event/window count or relative pose state | Compute only active cue. Gaps/invalid data reset continuity. A continuous yawn counts once; head pose has documented reference/sign. |
| `pipeline.decision.DecisionEngine` | method + temporal/cue features -> status/reason/evidence | Pure A/B/C rules and unknown behavior. No audio or display. |
| `pipeline.alerts`, `utils.overlay` | decision + frame/status -> audio/display | Side effects only. Cooldown and mute recorded; replay can be silent. |
| `experiments` | labelled videos + locked config + method -> run and summary records | Headless replay, no audio/UI; saves method/config/data IDs, evidence, status/reason and event metrics. Does not change detector rules. |

`FaceObservation` should distinguish face-level validity from each eye's validity. One unusable eye must not be silently fabricated. Adapter replacement must not change temporal/decision tests.

### Configuration boundaries

- `configs/config.yaml` holds documented demo defaults and local asset paths; no credentials or participant identifiers.
- Experiment config records method, eye-state source, EAR/confidence thresholds, window, coverage/valid duration, max gap, closure duration, yawn/head-pose rules, alert cooldown, timestamp and event-matching policies.
- Serialize resolved values and data/model/software identifiers with every run. Display/audio options cannot affect algorithm decisions.
- Existing values (60-second window, 30-second valid minimum, 0.8 coverage, EAR 0.21, 2-second closure, CNN 0.5 and cue thresholds) are configurable starting defaults, not mandated truths; validate and record changes. Only Accuracy >=0.90 is an instructor-stated goal.

## Eye-State and PERCLOS Design

### Primary research definition

Use 2D MediaPipe eye landmarks to calculate left/right EAR. An eye is closed below its validation-selected EAR threshold. Proposed bilateral state: `CLOSED` only when both valid eyes are closed; `OPEN` when at least one valid eye is confidently open; otherwise `UNKNOWN`. Fix the single-eye-invalid policy in run configuration/protocol and use it across A/B/C. Label outputs **landmark-derived PERCLOS (EAR proxy)**: EAR is not direct eyelid-occlusion measurement.

CNN remains a distinct required eye-image classifier. Evaluate it on held-out labelled eye images. Store class and confidence for each eye. Proposed bilateral CNN state follows the same policy as landmark evidence. CNN-derived PERCLOS may be an explicitly secondary ablation only; it must not replace the primary A/B/C source.

### Temporal rules

- Each consecutive valid pair within configured `max_gap` defines an observed interval assigned the earlier state. Integrate closed/valid time in a rolling window: `PERCLOS = closed_valid_seconds / valid_eye_seconds`.
- Unknown/gaps enter neither numerator nor denominator; report coverage, valid seconds, source, window and readiness. Do not interpolate through gaps. Unknown or long gap resets prolonged-closure continuity. Reject invalid/non-monotonic timestamps.
- Use one thresholded closure stream for PERCLOS and closure duration. Preserve brief valid closures in PERCLOS; use a separate configurable duration for prolonged-closure alerts. Document that operational rule.
- Insufficient valid duration/coverage is unknown/unavailable, not normal. Live and replay share temporal semantics; only clock source differs.
- CNN crop preprocessing must match training/inference. Low-confidence predictions are unknown under a validation-selected cutoff.

## Experimental Design

### Dataset and split protocol

1. **Eye-image set**: public labelled eye images for classifier evaluation. Record source/version or retrieval date, license, label mapping, exclusions, crop procedure and hashes. Split by subject/session/source group before derived crops. Augment training only; validation/test transformations are deterministic. If subject identity is absent, state that source-group separation cannot guarantee identity independence.
2. **Drowsiness video set**: use a public Kaggle resource only if terms and temporal labels support the SPEC; otherwise use consented, labelled volunteer sessions. Image-only labels cannot establish event onset or alert latency. Record annotations, timebase, event start/end, subject/session and condition labels. Document consent/access/retention/deletion before collection.
3. **Partitions**: subject/session-disjoint train/validation/test wherever identifiers permit. Freeze one split manifest. Validation alone selects model/thresholds/rules; held-out test is used for final results. Keep adjacent frames and near duplicates in one group.

### Methods and controlled comparison

Replay the same held-out clips and timelines under all methods, with the same landmark-derived EAR PERCLOS, timestamp source, valid-observation policy, window, coverage, prolonged-closure rule, event labels, cooldown and one-to-one match rule.

- **A — PERCLOS only**: shared prolonged-closure rule or ready PERCLOS above validation-selected primary threshold.
- **B — PERCLOS + yawning**: retain A unchanged; add a conjunctive path where ready PERCLOS reaches a shared secondary/borderline threshold and valid yawn count/duration meets its configured condition in the cue window.
- **C — PERCLOS + head pose**: retain A unchanged; add the analogous secondary PERCLOS path with sustained valid head-down evidence relative to a declared reference.

This additive rule exposes the added cue while keeping A's baseline fixed. Select shared primary/secondary PERCLOS and cue thresholds on validation only, then freeze for test. If SPEC review chooses another fusion rule, update traceability before implementation. Do not give methods different clips, sources, base settings or test tuning. Apply the same uncertainty policy. The headless runner evaluates; the live UI does not serve as an experiment harness.

### Labels, measures and failure analysis

- **Eye classification**: held-out images: class counts, Accuracy, confusion matrix, per-class precision/recall/F1 and averaging rule; report rejected/unknown samples separately. Do not equate image metrics with drowsiness detection.
- **Video events**: define labelled drowsiness interval, alert matching tolerance/overlap, and one-to-one matching before test. Report event precision/recall/F1, false alarms per evaluated hour and count, misses, unknown/valid coverage and eligible clip counts. Frame Accuracy is not sufficient.
- **Latency**: first matched alert minus annotated onset per event; summarize distribution and count. Misses remain misses and are excluded from latency summary. Separate media-time latency from processing/wall time; report machine, resolution and input mode.
- **Robustness**: stratify glasses, low light and head movement only where labels/counts suffice; report subgroup size and observation loss. Review false positives/misses, late warnings, landmark/crop errors, ambiguous labels and camera loss.
- Report >=0.90 eye and system Accuracy targets separately, define system-level unit/calculation first, and disclose actual values including unmet targets. Unknown evidence cannot count as correct normal.

## Data and Model Strategy

### Dataset verification and preparation

The instructor names a Kaggle Drowsiness Detection Dataset but gives no canonical URL/version. The current downloader URL for `dheerajperumandla/drowsiness-dataset` is a candidate only. Verify dataset page/release, license, layout, labels, subject/session metadata, temporal annotations, download integrity and redistribution terms before use. Record retrieval date and hashes. Image download alone does not establish video-evaluation suitability.

Keep raw data outside Git. Create a manifest with relative path/clip ID, class or interval label, group, hash, source/license and split. Validate decoding, labels, class counts and duplicates. Assign groups before crops; use identical resize/color/normalization for training and inference. Store original annotations separately from generated manifests. Do not commit private frames or publish them without consent/permission.

### CNN training and checkpoint

Retain existing small `EyeCNN` and PyTorch extra initially. Fix seed and class order (`open`, `closed`); use modest justified train-only augmentation, no validation/test augmentation. Record Python/PyTorch/NumPy versions, platform/hardware, seed, split-manifest hash, preprocessing, architecture and optimizer/loss/batch/epoch configuration. Select checkpoint by a predeclared validation criterion; never select on test outcomes. Determinism depends on environment; record nondeterministic accelerator settings rather than promising cross-platform bitwise equality.

Save state dictionary plus format, architecture, class mapping, preprocessing, data/split identifiers, seed/config and validation summary. Verify load compatibility. Runtime imports Torch lazily for EAR-only installs and uses eval/inference mode. Return per-eye probabilities; low confidence becomes unknown based on validation.

## Testing Strategy

- **Unit**: EAR/MAR/pose known and malformed geometry; monotonic timestamps; interval weighting/window clipping; unknown/gap handling; coverage; short blink vs prolonged closure; yawn de-duplication and reset; pose sign/reference; decision truth tables; event matching/false-alarm/latency metrics; config validation.
- **Model/data**: preprocessing shape/channel/range; per-eye outputs; checkpoint round-trip/rejection; split group disjointness; duplicates; label errors; manifest stability; train-only augmentation; validation checkpoint selection.
- **Integration**: replay short labelled fixture twice and verify media times, method, source, status/reason and metadata; headless replay disables audio/UI; fake invalid frame/no face/camera errors/multiple-face ambiguity/missing model/corrupt video.
- **Manual acceptance**: camera start/stop, normal/warning/unavailable UI, audio/cooldown/mute. Record machine/camera/config. Demo is not test-set evidence.
- **Regression/lint**: run pytest and Ruff in application root. Keep training/live camera checks out of fast unit path.

## Incremental Implementation Strategy

| Milestone | Dependencies | Deliverables | Verification and completion criteria |
| --- | --- | --- | --- |
| 1. Environment/data preparation | Current `uv` project; source review | Reproducible environment; dataset provenance/license decision; label audit; group manifest/split | Install documented extras; validate labels/data; demonstrate group/duplicate isolation where possible; pause claims if data unsuitable. |
| 2. Landmark analysis/PERCLOS baseline | M1; existing FaceDetector/EAR/TemporalTracker | Per-eye validity, EAR state, timestamp PERCLOS/coverage/closure and recorded-video A logs | Unit tests for geometry/gaps/duration/window; replay known input; insufficient evidence never alerts as normal. |
| 3. CNN training/classification | M1 labels/split; M2 crop contract | CNN checkpoint and held-out classification report; separate inference path | Disjoint manifest; reproducible config; checkpoint round trip; report measured confusion matrix; same preprocessing. |
| 4. Webcam integration/alerts | M2; M3 optional for CNN runtime | Local camera start/stop, visible reasons/status, audio/cooldown/mute; retain replay | Manual camera/error/stop/audio and automated faked-source checks; no stale-frame decisions; measure throughput/latency. |
| 5. Yawn/head-pose methods | M2 stable landmarks/time | B yawn events, C relative pose, named rules | Unit tests for single yawn count, gap resets, pose sign/reference and invalid evidence; A unchanged. |
| 6. Controlled experiments | M1 grouped temporal labels; M2/M5 | Headless runner, common A/B/C config, annotation format, event metrics/exports | Same clips/labels/source/base rules; validation-frozen thresholds; review matches, misses, false alarms, coverage, latency and leakage. |
| 7. Final integration/research outputs | M1–M6 | Demo/config/checkpoint guidance, reproducibility package, tables/figures, limitations, report/slides | Re-run documented paths; reconcile report with run artifacts; acceptance mapped to evidence; disclose limitations and prototype status. |

Each milestone verifies its own outcome before dependent work begins. Do not defer testing to the final milestone.

## Risks and Trade-offs

| Risk | Consequence | Mitigation / gate |
| --- | --- | --- |
| Dataset identity/license/labels/temporal annotations unclear | Invalid, non-reproducible or legally unsuitable results | Verify exact source/version/terms/labels before use; image-only data supports classification only; new video collection follows consent requirements. |
| Subject IDs missing or frames duplicated across subsets | Leakage and inflated generalization | Split by subject/session, deduplicate before split, persist groups/hashes; disclose source-only limitation. |
| EAR varies with person, pose, glasses/light | False eye state/PERCLOS | Bilateral valid landmarks, validation threshold, coverage/unknown, condition analysis; personalization remains optional. |
| Landmark jitter or face loss | Spurious temporal events or false normality | Validate geometry/continuity; gap resets; explicit unknown; inspect failure cases, never stale evidence. |
| CNN overfits small/unbalanced data | Image score fails to generalize temporally | Group splits, class counts, train-only augmentation, held-out metrics; do not equate image Accuracy to system success. |
| Performance depends on machine/camera | Delayed warnings or unusable UI | CPU-first baseline, measure declared hardware, profile before optimization, no unsupported FPS target. |
| Yawn/head pose are confounded/reference drift | Additional false alarms or user variability | Count sustained yawn once, define pose axes/reference, validation-only thresholds and subgroup analysis. |
| Thresholds differ across methods | Unfair reported gains | Shared base settings, validation-only tuning, recorded fusion rules and one-to-one matching. |
| Consent/data terms incomplete | Participant harm or data exposure | Local processing, consent/retention/access notes, Git exclusions, license verification and identifier scrubbing. |
| False negatives invite over-trust | Unsafe reliance | Prominent research-only text, unknown state, no safety guarantees, report misses and limitations. |

## Unresolved Decisions and Plan Gates

These items are not assumed facts and do not alter SPEC requirements:

1. Select/verify exact public datasets, version, license, retrieval date and which supplies images versus temporally labelled clips; current URL is not authoritative.
2. Confirm video labels, subject/session counts and event quality; otherwise report gaps and follow SPEC for consented annotations/data.
3. Lock annotation onset/offset, event match tolerance/overlap and meaning/calculation of system-level Accuracy before test evaluation.
4. Confirm single-eye-invalid policy, CNN confidence cutoff method and landmark quality filtering before model evaluation.
5. Define head-pose neutral reference acquisition without test leakage and validate camera viewpoint/sign convention.
6. Decide whether to rename `EARBackend` to clarify landmark provenance or keep the path for compatibility; this is a naming choice.
7. Resolved 2026-10-26: the SPEC is the approved requirements baseline. Open dataset, annotation, threshold, consent, and evaluation decisions remain owned prerequisites for their dependent tasks.

## Traceability to SPEC

| SPEC requirements | Plan coverage |
| --- | --- |
| FR-001–002, FR-017: local webcam/video, failures, timestamps | Source contract, integration tests, M2/M4 |
| FR-003–006: face/landmarks, crops, distinct CNN/landmark states | Vision/backend contracts, M2/M3 |
| FR-007–008: PERCLOS and prolonged closure | Temporal design/tests, M2 |
| FR-009–010: yawning/head pose | Cue contract/tests, M5 |
| FR-011–012: A/B/C, status/reason/unknown | Shared decision rules, M5/M6 |
| FR-013–016, FR-020: display/audio, ambiguity, mute | Presentation boundary and acceptance checks, M4 |
| FR-018–019: reproducible records and summary | Experiment runner and metric records, M6 |
| NFR-001–009 | Metrics, risks, privacy, performance and prototype claims throughout |
| DR-001–008 | Dataset strategy, consent and split gates, M1 |
| Experimental requirements 1–8 | CNN report, common test protocol, event/latency/robustness, M3/M6 |
| Acceptance criteria | Milestone verification and [quickstart.md](quickstart.md) |

## Constitution Check (post-design)

- Research-first: pass; A/B/C use landmark PERCLOS, CNN stays distinct/optional ablation.
- Simplicity: pass; retain dependencies and paths, add only experiment runner/metrics.
- Reproducibility: pass with dataset, split, annotation and threshold gates.
- Testability/reliability: pass; contracts and unknown/error tests defined.
- Incremental development: pass; seven gated milestones.
- Privacy: pass; local processing, consent and data controls specified.
- Traceability: pass; SPEC requirements map to modules, checks and milestones.

No constitution violation is identified. The project owner approved this plan and the TASKS phase has produced `tasks.md`. Unresolved dataset/annotation decisions remain explicit prerequisites for their dependent training and evaluation tasks.

## Complexity Tracking

No constitution violations or extra architectural projects are proposed. An experiment runner/metrics module is the minimum addition for FR-018/019 and the controlled comparison; reusing the demo loop would mix UI/audio side effects into evaluation.
