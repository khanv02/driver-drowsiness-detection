# Temporal Evaluation Metrics

**Status:** Parameterized implementation verified with synthetic cases; protocol and
real-data scoring remain unapproved.

`drowsyalert.experiments.metrics` provides data-independent primitives for the draft
Phase 6 protocol. It deliberately has no default matching tolerances: callers must supply
the early and late bounds from an approved, frozen protocol.

## Matching

Reference events and predicted alert episodes have stable IDs, clip IDs, and finite
media-time intervals. Matching processes references chronologically within each clip and
assigns the earliest unmatched alert onset inside the supplied inclusive early/late
window. Each reference and alert can be used once. An alert beginning before the early
boundary remains a false alert even if its interval later overlaps the event.

The result preserves matched IDs, unmatched reference IDs, unmatched alert IDs, and
signed onset latency. A negative value is early detection; it is not clamped. Missing
events have no latency value.

## Summaries

- Event metrics: TP, FP, FN, precision, recall, and F1.
- False alarms: unmatched alerts divided by valid observed hours.
- Latency: raw matched values plus detected/missed counts, mean, median, population
  standard deviation, range, and linearly interpolated 25th/75th percentiles.
- Coverage: eligible, valid, and unknown seconds; coverage; eligible and valid hours.

Undefined divisions are `null`/`None`, not a fabricated zero. When both references and
alerts exist but none match, precision, recall, and F1 are valid zeros. Invalid or
duplicate intervals, negative/non-finite tolerances, negative durations, and impossible
coverage totals are rejected.

These functions do not load videos, select thresholds, define ground truth, approve the
draft -1/+2 second proposal, or produce a research conclusion. T-025 remains pending
until T-023 is approved; later integration must prove that the same approved clips,
eligibility mask, labels, tolerances, and denominators are supplied for A/B/C.

## Alert episodes and system Accuracy

Frame statuses are converted to half-open media-time intervals using the earlier
sample's state. A transition from `ALERT` to either `NORMAL` or `UNKNOWN` ends an alert
episode; consecutive alert samples remain one episode. Missing time before the first
status is `UNKNOWN`. Samples must be finite, strictly increasing, and inside the clip.

System Accuracy divides each declared clip timeline into caller-supplied fixed bins.
Reference-event overlap and predicted-state duration use an explicit positive-fraction
parameter. If ALERT and NORMAL both meet that fraction in a tie, the bin is conservatively
`UNKNOWN` instead of silently choosing one outcome.

Primary Accuracy is `correct_bins / all_bins`: UNKNOWN remains in `all_bins` and never
counts as correct normal. Observed-only Accuracy and coverage are separate diagnostics.
TP/TN/FP/FN cover observed predictions, while `unknown_bins` preserves withheld
evidence. The same calculation can be grouped by a declared condition value; absent tags
form an explicit `unknown` group.

The proposed 1-second/50-percent protocol is not embedded as a hidden decision. Bin size
must be supplied by the caller, and the overlap fraction remains an explicit parameter
to be frozen by the approved protocol.

## Run-record evaluator

`drowsyalert.experiments.evaluation` joins strict annotations to completed headless run
records by clip ID. It requires the run clips to exactly match the declared corpus and
the method ID to match the requested method. It derives alert episodes from media-time
status transitions, then reports event matching, signed latency, fixed-bin Accuracy,
valid/unknown coverage, observation-loss reasons, condition-tag counts, and processing
time as separate sections. Incomplete runs, missing clips, empty frame evidence,
negative processing times, or annotations outside the corpus are rejected.

The evaluator accepts a protocol object containing the reference labels, early/late
tolerances, bin size, and positive fraction. It does not decide which NITYMED behaviors
are the primary endpoint. Results can be written as strict JSON with non-finite values
rejected.
