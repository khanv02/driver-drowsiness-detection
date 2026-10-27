# DrowsyAlert Temporal Evaluation Protocol

**Protocol ID:** `drowsyalert-video-eval-v1.1`

**Prepared:** 2026-10-26

**Status:** APPROVED AND FROZEN by the project owner on 2026-10-26

**v1.1 amendment:** The owner approved a disclosed clip-disjoint NITYMED evaluation
because the acquired provider package has no participant-to-clip mapping. This amendment
does not claim subject-independent generalization.

This document fixes the definitions approved under T-126. Data-artifact fields that
depend on completed annotations and grouping remain T-139 evidence gates; their absence
blocks a final run but does not reopen the scoring rules below.

## 1. Research comparison

The primary comparison replays the same eligible held-out RGB face-video timelines with:

- A: landmark-derived PERCLOS and the shared prolonged-closure rule;
- B: A plus valid yaw evidence in the configured combined-PERCLOS band;
- C: A plus valid relative head-down evidence in the same band.

All methods use the same landmark-EAR eye source, media timestamps, face-validity rule,
single-eye policy, temporal window, gap/coverage rule, primary and combined PERCLOS
thresholds, prolonged-closure rule, clips, labels, and event matcher. Only the named
auxiliary cue and its declared settings differ. CNN-derived PERCLOS, if later evaluated,
is a separately labelled secondary ablation.

## 2. Dataset and partition

- Selected source/version: **NITYMED HDTV720 local inventory, provider page last updated
  2022-05-25; approved public-data path**
- License/terms evidence and retrieval date: **Provider-declared CC BY; retrieved
  2026-10-26 through the official grouped access page; owner must retain access evidence**
- Dataset/archive SHA-256: **No archive retained. Per-video hashes are recorded in local
  manifest `bb654b8c5f7104d23268503f02935d3c30974a0199fa4c64d3b8fe4985816307`.**
- Annotation source/version: **Independent human media-time review using
  `docs/guides/annotation-review.md`; exact final annotation manifest pending T-139**
- Subject/session identifiers: **Absent from acquired layout; limitation disclosed and
  no identity is inferred from appearance or filenames**
- Validation/test split manifest identity:
  **`2e4e0ea7eb2e529ea2db2f692444768a4de91023d9ce29829bcbdab911cbd047`;
  audited membership in `docs/research/evaluation-split-v1.1.md`**

The v1.1 corpus contains all 19 available microsleep clips and a deterministic seeded
selection of 19 yawning clips. It is balanced and clip-disjoint:

- validation: 6 microsleep + 6 yawning clips;
- held-out test: 13 microsleep + 13 yawning clips;
- the four already viewed pilot clips are locked to validation;
- selection seed: 42; exact membership and hashes are stored before further annotation.

No clip, derived frame, or content hash may cross validation and test. Participant IDs
remain unavailable, so the split cannot prove subject independence. All results must say
"clip-disjoint" and disclose possible same-participant leakage. A later authoritative
provider mapping may upgrade the split under a new protocol version, but test membership
must not be rearranged after test labels/results are inspected.

Validation data selects EAR/PERCLOS/yawn/pose thresholds, durations, pose reference
procedure, and any matching tolerance. Once selected, save the resolved configuration
and manifest hashes and freeze them. Held-out test data is evaluated once without
threshold changes. Any change creates a new protocol version and invalidates the earlier
test comparison as the final result.

## 3. Reference annotations

Annotations use video media time in seconds and this minimum schema:

| Field | Rule |
|---|---|
| `clip_id` | Stable non-identifying ID mapped privately to the source content hash |
| `subject_group` / `session_group` | Required for leakage-safe splitting when available |
| `start_seconds`, `end_seconds` | Finite, `0 <= start < end <= media duration` |
| `label` | Dataset-defined `drowsy_event` for the primary endpoint; observable subtypes such as `microsleep`, `prolonged_eye_closure`, `yawn`, or `head_nod` may be secondary tags |
| `annotation_source` | Original provider label or independent human annotation; never a DrowsyAlert prediction |
| `annotator_id`, `adjudication` | Pseudonymous reviewer ID and disagreement resolution status when manually labelled |
| `confidence` | Declared ordinal/continuous scale or `not_provided`; never silently inferred |
| condition tags | `glasses`, `lighting`, and `head_movement` only when explicitly observed/available; otherwise `unknown` |

The tracked header-only template is `docs/research/annotation-template.csv`. The loader in
`drowsyalert.experiments.annotations` requires this exact column order, finite media
times, valid media bounds, stable clip/group identity, approved labels and conditions,
final adjudication, and subject/session-disjoint validation/test splits. It rejects
duplicate rows and detector-derived reference sources. The validator operates only on
metadata and never loads or stores video frames.

Approved controlled values are:

- split: `validation` or `test`;
- label: `drowsy_event`, `microsleep`, `prolonged_eye_closure`, `yawn`, or
  `head_nod` unless the approved dataset guide replaces this set;
- adjudication: `provider`, `agreed`, `resolved`, `single_reviewer`, or
  `not_applicable`; `pending` may be loaded for work-in-progress but is rejected as
  final evaluation evidence;
- glasses/head movement: `present`, `absent`, or `unknown`;
- lighting: `normal`, `low`, or `unknown`.

The primary endpoint is an independently reviewed `microsleep` event. Onset is the first
reviewed media frame showing the transition into a brief visible sleep/awareness-loss
episode; offset is the first reviewed frame showing clear return to wakeful eye/face
behavior. If those boundaries cannot be distinguished confidently, the interval remains
pending/ambiguous and is excluded before the split is frozen with its exclusion reason.
Provider folder membership alone does not supply onset or offset.

`yawn` is a secondary observable-behavior endpoint and is never silently merged into
the primary microsleep/system Accuracy result. Its onset is the first clear sustained
yawn opening and its offset is the return from that opening. Head nod and prolonged eye
closure may be secondary tags. Algorithm outputs, EAR, PERCLOS, MAR, pose values, or
DrowsyAlert alerts cannot define any reference boundary because that would be circular.

For manual annotation, two reviewers independently mark onset/offset without seeing
method predictions. They reconcile disagreements before the split is revealed as final
test. The protocol must state the adjudication tolerance and report agreement. If only
one qualified reviewer is available, record that limitation rather than implying
independent adjudication.

## 4. Predicted alert episodes

A predicted episode starts on a transition into `ALERT` and ends on the first later
non-alert status or end of eligible media. Consecutive alert frames are one episode;
audio cooldown does not create additional detections. `UNKNOWN` ends an alert episode
and contributes to observation-loss measures. Status is derived from media time, not
wall-clock processing time.

## 5. Frozen one-to-one matching

Process reference events chronologically. Match each event to the earliest unmatched
predicted alert onset inside:

`[reference onset - early tolerance, reference end + late tolerance]`

The approved fixed tolerances are **1.0 second early** and **2.0 seconds late**. Each
alert and reference event can be matched at most once. Unmatched references are false
negatives; unmatched alerts are false positives. Changing these tolerances creates a new
protocol version and the held-out test must not be rescored as the same experiment.

Latency is `matched alert onset - reference onset` in media seconds. Negative latency is
retained and reported as early detection, not clamped to zero. A continuous alert that
began before the matching window is a false alarm and cannot be reused at event onset.
Missed events have no numeric latency and are excluded from latency summaries while
remaining in the miss count.

## 6. Metrics and denominators

Report, for every method and the same eligible clips:

- event TP, FP, FN, precision, recall, and F1;
- miss count and false-alert episode count;
- false alarms per **valid observed hour** as the primary rate, plus total eligible media
  hours and valid/unknown duration so poor coverage cannot improve the interpretation;
- per-match latency values and count, median, mean, standard deviation, minimum, maximum,
  and 25th/75th percentiles; never insert zero for a miss;
- valid and unknown seconds plus observation coverage;
- eligible clip, participant, session, event, and condition counts;
- processing throughput/wall time separately from media-time alert latency.

Division by zero yields an explicit unavailable/null metric with its count/denominator,
not a fabricated zero. Eye-image Accuracy remains the Phase 3 classifier metric and is
not mixed with video-event measures.

## 7. Frozen system-level Accuracy definition

Use consecutive, half-open media-time bins with a **1.0-second width and a 1.0-second
stride**. Bins do not overlap. A final partial bin may be shorter at the end of a clip.
The **0.50 within-bin event-occupancy threshold** labels a bin reference-positive when a
primary drowsy event covers at least half of the bin's eligible labelled duration;
otherwise it is reference-negative. This 0.50 threshold is not a bin stride or overlap
between neighboring bins. A predicted bin is positive when `ALERT` covers at least 0.50
of its duration and negative when `NORMAL` covers at least 0.50. If both meet the
threshold in a tie, or neither does, the prediction is `UNKNOWN`.

Primary system Accuracy is `(correct positive + correct negative) / all eligible labelled
bins`; `UNKNOWN` bins remain in the denominator and are never counted as correct normal.
Also report observed-only Accuracy as a secondary diagnostic with its coverage. This
prevents a system from appearing accurate by withholding difficult observations. The
instructor's >=0.90 system goal is assessed only after this definition is approved and
the held-out evaluation is complete.

## 8. Conditions, exclusions, and failures

Stratify glasses, low light, and head movement only when the source or approved annotator
provides those tags and subgroup counts are reported. Do not infer a condition from model
failure. Record no-face, multiple-face, landmark/crop invalidity, uncertain CNN output,
long gaps, corrupt media, and processing errors separately. A clip may be excluded only
under a predeclared rule, with the clip ID, reason, and stage recorded. Never exclude a
clip because a method performs poorly.

All A/B/C methods share the same eligibility mask for comparison. Method-specific cue
unavailability remains method evidence and cannot remove that sample from only one
method's denominator.

## 9. Privacy and review

Raw public/restricted videos, participant identifiers, annotations tied to identities,
and generated run artifacts remain outside Git. Publish only material allowed by the
source agreement. Volunteer collection is blocked until written supervisor/ethics
approval covers purpose, consent/withdrawal, access, retention/deletion, and publication.
DrowsyAlert remains a research prototype, not a safety or medical system.

## 10. Approval record

| Decision | Frozen value/status | Reviewer/date |
|---|---|---|
| Dataset path and rights | Official-path NITYMED HDTV720 under provider-declared CC BY; access evidence stays outside Git | Project owner, 2026-10-26 |
| Primary event-label guide | Independently reviewed microsleep intervals; yawn is a separate secondary endpoint | Project owner, 2026-10-26 |
| Data split | Balanced 38-clip split: validation 6+6, test 13+13; pilot clips locked to validation; possible participant leakage disclosed | Project owner, v1.1 amendment 2026-10-26 |
| Matching rule | Earliest unmatched alert in inclusive -1.0/+2.0-second window | Project owner, 2026-10-26 |
| False-alarm denominator | Valid observed hours; also report eligible and unknown time | Project owner, 2026-10-26 |
| Latency and miss handling | Signed media-time latency; misses excluded from latency and counted as FN | Project owner, 2026-10-26 |
| System Accuracy | Non-overlapping 1-second bins with 1-second stride; event occupancy and predicted-state threshold are each 0.50 of the bin's eligible duration; UNKNOWN is incorrect in the primary denominator | Project owner, 2026-10-26 |
| Threshold selection/freeze | Validation only; one-way held-out test | Project owner, 2026-10-26 |
| Volunteer ethics path | No volunteer collection authorized; public-data path only | Project owner, 2026-10-26 |

This approval freezes the evaluation definitions; it does not certify that complete
annotations, split artifacts, thresholds, or results exist. T-139 remains the evidence
gate for those inputs. Final results may support only a clip-disjoint NITYMED claim, not
a subject-independent generalization claim.
