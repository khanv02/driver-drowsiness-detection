# DrowsyAlert Temporal Evaluation Protocol

**Protocol ID:** `drowsyalert-video-eval-v1-draft`

**Prepared:** 2026-10-26

**Status:** DRAFT — NOT APPROVED OR FROZEN

This document proposes the definitions needed for T-023. Bracketed data-source fields
and the approval table must be completed by the project owner/research supervisor before
threshold selection, test scoring, or a Phase 6 performance claim.

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

## 2. Dataset and partition (approval blocker)

- Selected source/version: **NITYMED HDTV720 local inventory candidate, provider page
  last updated 2022-05-25; final protocol approval pending**
- License/terms evidence and retrieval date: **Provider-declared CC BY; retrieved
  2026-10-26 through the official grouped access page; owner must retain access evidence**
- Dataset/archive SHA-256: **No archive retained. Per-video hashes are recorded in local
  manifest `bb654b8c5f7104d23268503f02935d3c30974a0199fa4c64d3b8fe4985816307`.**
- Annotation source/version: **[PENDING]**
- Subject/session identifiers: **Absent from acquired layout; provider mapping or
  reviewed grouping still required**
- Validation/test split manifest and SHA-256: **[PENDING AUDIT]**

Partition by participant first, or by recording session/source group if participant IDs
are genuinely unavailable. No subject, session, adjacent frames, derived clips, or
near-duplicate source may cross validation and held-out test. Missing identity metadata
must be disclosed and constrains generalization claims.

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

The tracked header-only template is `docs/annotation-template.csv`. The loader in
`drowsyalert.experiments.annotations` requires this exact column order, finite media
times, valid media bounds, stable clip/group identity, approved labels and conditions,
final adjudication, and subject/session-disjoint validation/test splits. It rejects
duplicate rows and detector-derived reference sources. The validator operates only on
metadata and never loads or stores video frames.

Current draft controlled values are:

- split: `validation` or `test`;
- label: `drowsy_event`, `microsleep`, `prolonged_eye_closure`, `yawn`, or
  `head_nod` unless the approved dataset guide replaces this set;
- adjudication: `provider`, `agreed`, `resolved`, `single_reviewer`, or
  `not_applicable`; `pending` may be loaded for work-in-progress but is rejected as
  final evaluation evidence;
- glasses/head movement: `present`, `absent`, or `unknown`;
- lighting: `normal`, `low`, or `unknown`.

Primary drowsy-event definitions must come from the selected dataset's authorized label
guide or a supervisor-approved independent annotation guide. Algorithm outputs, EAR,
PERCLOS, MAR, or pose values cannot define the reference label because that would make
the comparison circular.

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

## 5. Proposed one-to-one matching (approval required)

Process reference events chronologically. Match each event to the earliest unmatched
predicted alert onset inside:

`[reference onset - early tolerance, reference end + late tolerance]`

Proposed starting values for validation review are **1.0 second early** and **2.0 seconds
late**. These are not approved thresholds. Select/freeze them on validation evidence or
replace them with a supervisor-approved fixed rule before viewing test scores. Each alert
and reference event can be matched at most once. Unmatched references are false
negatives; unmatched alerts are false positives.

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

## 7. Proposed system-level Accuracy definition (approval required)

Use fixed, non-overlapping 1-second media-time bins over eligible labelled time. A bin is
reference-positive when at least half its labelled duration is inside a primary drowsy
event; otherwise it is reference-negative. A predicted bin is positive when at least
half its duration is `ALERT`, negative when at least half is `NORMAL`, and `UNKNOWN`
otherwise.

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

| Decision | Proposed value/status | Reviewer/date |
|---|---|---|
| Dataset path and rights | NITYMED HDTV720 acquired and integrity-audited; final rights/access evidence review pending | Pending |
| Primary event-label guide | Pending selected dataset/annotation guide | Pending |
| Subject/session split | Subject-disjoint; exact manifest pending | Pending |
| Matching rule | Earliest unmatched alert; proposed -1.0/+2.0 s validation-selected window | Pending |
| False-alarm denominator | Valid observed hours; also report eligible and unknown time | Pending |
| Latency and miss handling | Signed media-time latency; misses excluded from latency and counted as FN | Pending |
| System Accuracy | Fixed 1-second bins; unknown incorrect in primary denominator | Pending |
| Threshold selection/freeze | Validation only; one-way held-out test | Pending |
| Volunteer ethics path | Not authorized; public-data path preferred | Pending supervisor review |

Until every row is approved, this remains a draft. Synthetic metric implementation and
tests must not be presented as approval, real-data evidence, or research results.

The annotation validator and its synthetic tests are preparatory infrastructure only.
They do not resolve the pending dataset, label guide, matching thresholds, or human
approval fields above.
