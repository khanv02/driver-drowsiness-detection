# NITYMED Four-Clip Pipeline Pilot

**Date:** 2026-10-26

**Status:** Integration pilot only — not held-out research evidence

This pilot verifies that reviewed media-time annotations, headless A/B/C replay, run
records, event matching, latency, coverage, system Accuracy, failure summaries, and the
comparison exporter work together. It must not be cited as the final Phase 6 comparison.

## Frozen artifact identities

- Dataset: `nitymed-hdtv720`
- Video manifest SHA-256:
  `bb654b8c5f7104d23268503f02935d3c30974a0199fa4c64d3b8fe4985816307`
- Pilot annotation SHA-256:
  `7ebd51ac7af75ed39534261eed113ba25dd7ac1949a17142b8735f362a65d934`
- Batch-plan SHA-256:
  `10db2c31de4c110a03bc4b39714284d63421573fc1176577c1207b52b2043d3b`
- Split ID: `nitymed-pilot-4-v1` (`validation`, pilot-only)
- Eye source: `landmark_ear`
- Methods: A PERCLOS, B PERCLOS+yawn, C PERCLOS+head pose
- Output: ignored `outputs/results/nitymed-pilot-v1/`

The pilot contains four clips (two provider microsleep-category and two yawning-category
clips), 310.72 seconds of eligible media, three reviewed primary microsleep events, and
six secondary yawn events. One project-owner reviewer supplied the intervals. Overlapping
duplicate presses were merged; microsleep marks shorter than the agreed two-second pilot
review guide and yawn marks shorter than one second were removed. Original drafts were
retained locally under ignored data storage.

## Pilot results

All 12 planned replays completed with no runner failure. A, B, and C produced identical
alert episodes under this provisional configuration:

| Measure | A | B | C |
|---|---:|---:|---:|
| Reference microsleep events | 3 | 3 | 3 |
| Alert episodes | 9 | 9 | 9 |
| TP / FP / FN | 2 / 7 / 1 | 2 / 7 / 1 | 2 / 7 / 1 |
| Event precision | 0.2222 | 0.2222 | 0.2222 |
| Event recall | 0.6667 | 0.6667 | 0.6667 |
| Event F1 | 0.3333 | 0.3333 | 0.3333 |
| False alarms per valid hour | 132.8273 | 132.8273 | 132.8273 |
| Primary 1-second-bin Accuracy | 0.1981 | 0.1981 | 0.1981 |
| Observed-only Accuracy | 0.3229 | 0.3229 | 0.3229 |
| Observation coverage | 0.6106 | 0.6106 | 0.6106 |
| Detected / missed events | 2 / 1 | 2 / 1 | 2 / 1 |
| Mean signed latency (detected only) | 5.18 s | 5.18 s | 5.18 s |
| Mean processing time/frame | 15.32 ms | 15.57 ms | 16.17 ms |

Matched latency values were 6.80 and 3.56 seconds. Unknown time was 121.00 seconds of
310.72 seconds. The dominant unknown reason was the 30-second temporal-window warm-up
(113.92 seconds aggregated across the four clips); no-face time was 7.04 seconds, plus
0.04 seconds from one eye-region validity failure.

## Interpretation and limitations

- The equal A/B/C output means the auxiliary cue paths did not change alert episodes on
  this tiny pilot under the provisional thresholds. It does not prove the cues are
  useless or equivalent.
- Accuracy, precision, and false-alarm results are poor and must not be hidden. They show
  that the demo defaults are not validated experimental thresholds.
- Participant identities are unavailable, so subject-disjoint separation is unproven.
- Four validation clips and three primary events are far too small for a general claim.
- Labels came from one reviewer and underwent disclosed duration/overlap normalization.
- Glasses, head movement, and per-event lighting conditions remain `unknown`; no subgroup
  robustness conclusion is available.
- The 60-second window creates substantial unavailable time in short yawning clips.
- The fixed `0.0` degree pose reference was used only to exercise method C end-to-end;
  it is not validation-selected evidence for a final comparison.

The pilot passes the software integration purpose of T-145. T-139 and the final A/B/C
study remain blocked until independently reviewed annotations and participant-safe
validation/test grouping exist. No test threshold is selected from these pilot results.
