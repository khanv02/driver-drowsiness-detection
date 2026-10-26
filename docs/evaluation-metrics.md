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
