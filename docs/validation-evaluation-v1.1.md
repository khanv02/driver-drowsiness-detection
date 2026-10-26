# NITYMED validation baseline v1.1

Date: 2026-10-26  
Status: validation-only baseline; not a held-out test claim

## Scope and identities

The batch replayed the same 12 independently reviewed validation clips for methods A,
B, and C. It completed all 36 planned runs headlessly with muted audio, no failures,
and no skipped records.

| Artifact | SHA-256 |
|---|---|
| Validation worklist | `f0de455c376b09bec6dd5585208ec8cafbbf002f93ce390248cb8738a149891b` |
| Validation annotations | `c27d4c01b0b37fba8b58bae7893241c94222e7c4c908c06ef241beebb5d74f21` |
| Batch plan | `0404c1dae4dff6773480d24b0b1b27990ec01bfc5efd24f59b25543bd8f07da0` |
| Comparison | `d0d02d8596e03e5d77555a34be2501511d02d10fda672de391eac6f9cd8778e7` |
| Plan identity | `9b95149bb468afd478c29859744649992dcaec5e6f695684a554a3660bb6c82f` |

The ignored machine-readable outputs are under
`outputs/results/nitymed-validation-v1.1/`. The batch used commit
`c6d89884bfc3828d15a9951112d8735867a3339a`, seed 42, Protocol
`drowsyalert-video-eval-v1.1`, and `configs/evaluation-v1.yaml`.

## Baseline results

There were 19 reviewed primary microsleep events across 939.72 eligible seconds.

| Method | TP | FP | FN | Precision | Recall | F1 | Primary system accuracy | Observation coverage | Mean detected latency |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| A: PERCLOS | 5 | 28 | 14 | 0.1515 | 0.2632 | 0.1923 | 0.2860 | 0.6299 | 2.904 s |
| B: PERCLOS + yawn | 5 | 28 | 14 | 0.1515 | 0.2632 | 0.1923 | 0.2701 | 0.6299 | 2.904 s |
| C: PERCLOS + head pose | 5 | 28 | 14 | 0.1515 | 0.2632 | 0.1923 | 0.2860 | 0.6299 | 2.904 s |

Each method processed 23,493 frames. Five of 19 reference events were matched; 14
were missed. The false-alarm rate was 170.28 per valid observed hour. Latency is
reported only for the five detected events and must not be read as performance on the
missed events.

## Interpretation and next decision

This baseline is unsuitable for freezing as the final test configuration. The 30-second
minimum-valid warm-up accounts for about 335.24 of 347.76 unknown seconds and is poorly
matched to event-focused clips that are often only 20--50 seconds long. Method B changes
bin-level output but does not improve event detection; method C is indistinguishable from
A at these settings. These observations are validation evidence, not test evidence.

Before held-out test execution:

1. add a deterministic offline replay/sweep over the stored validation observations;
2. reduce warm-up only within the predeclared validation search space and audit coverage,
   false alarms, misses, and latency together;
3. freeze exactly one selected configuration and its hashes;
4. annotate and run the 26 test clips once without further tuning.

Participant IDs and condition tags remain unavailable, and annotations are from one
reviewer with disclosed duration normalization. No subject-independent, condition-group,
or held-out-test claim is made.
