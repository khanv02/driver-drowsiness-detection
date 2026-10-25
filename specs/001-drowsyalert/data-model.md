# Data Model and Processing Contracts

These records describe boundaries in [plan.md](plan.md), not implementation code.

## Runtime records

| Record | Core fields | Validation and meaning |
| --- | --- | --- |
| `FrameSample` | index, image, timestamp seconds, source kind (`live_monotonic`/`video_media`) | Nonempty image; finite, strictly increasing stream time. Clock domains remain distinct. |
| `FaceObservation` | face selection/count, landmarks, left/right eye validity/crops/boxes/EAR, reason | Each eye can be valid independently; no face, ambiguity, invalid geometry and out-of-frame crops are explicit. Coordinates documented. |
| `EyeStateEvidence` | source (`landmark_ear`/`cnn`), per-eye state and confidence, bilateral state, config ID, reason | `OPEN`, `CLOSED` or `UNKNOWN`; preserve per-eye outputs; invalid/low confidence is unknown. |
| `TemporalFeatures` | source, window bounds, closed/valid seconds, coverage, PERCLOS or null, ready, continuous closure | Unknown excluded from numerator/denominator; insufficient coverage is not ready; long gap breaks continuity. |
| `CueFeatures` | method, yawn events/count/validity, pose/reference/validity, head-down duration | Unknown is not zero-valued evidence. Sustained mouth opening counts once. |
| `Decision` | method, status, reason, contributing evidence, timestamp | Reasons identify rule/evidence; unknown readiness cannot be normal. |
| `RunConfig` | method, source, thresholds/windows/gap/coverage, decision/match rules, audio, assets | Fully resolved and serialized; display/mute do not alter decisions. |
| `RunRecord` | run ID, code/config/data/model IDs, environment, source, frame/event outputs, completion/error | No participant identity by default; raw frames not retained by default. |

## Data and evaluation records

| Record | Core fields | Validation and meaning |
| --- | --- | --- |
| `DatasetManifestRow` | relative path/clip ID, source/version/license, labels, subject/session/source group, hash, split, transforms | Split at source-group level before crops. Missing identity metadata constrains claims. |
| `EyeImageLabel` | sample ID, open/closed/ambiguous, label source/adjudication, eye side | Ambiguous/occluded samples excluded or separately labelled. |
| `DrowsinessAnnotation` | clip ID, start/end media time, event definition, annotator/source, confidence, condition tags | Times ordered and within clip. Image labels do not imply temporal onset. |
| `ModelCheckpointMetadata` | format, architecture, class order, preprocessing, training config/seed, split hash, selected epoch, validation metrics/library | Reject incompatible class order or transforms; test metrics never select model. |
| `EventEvaluation` | method/run, reference event, matched warning, match rule, TP/FP/FN, latency/miss, coverage | One-to-one matching under declared tolerance; misses are not zero-latency detections. |

## State and interval rules

- Valid adjacent observations define `[t_i, t_(i+1))` only when the gap is within configured maximum; earlier state labels the interval.
- Unknown intervals enter neither closed nor valid duration. Coverage uses the declared warm-up/window rule.
- Bilateral closed requires both required eyes valid and closed; a valid open eye can establish not-bilaterally-closed; otherwise unknown. Final one-eye-invalid handling is recorded.
- Prolonged closure resets on opening, unknown or excessive gap. PERCLOS includes all valid closed time under the operational EAR threshold; it is not a blink-event counter.
- Decisions are pure outputs; audio, GUI and file writes are downstream effects.

## Relationships

A `RunConfig` and source identity govern many `FrameSample`s. Each may produce a `FaceObservation`, two eye evidence values, temporal/cue updates and a `Decision`. `RunRecord` groups them. A `DatasetManifest` maps sources to image labels and/or temporal annotations. Checkpoints reference training manifests; event records aggregate into method summaries.
