# Method A decision policy

Phase 4 Method A combines immediate sustained-closure evidence with a ready PERCLOS window.
Method B/C cue fusion remains deferred to Phase 5 T-021.

## Decision precedence

1. An unknown eye observation produces `UNKNOWN` with reason `Eyes unavailable`.
2. Invalid/non-finite temporal evidence produces `UNKNOWN`.
3. Continuous closure at or above `closed_seconds` produces `ALERT`, even while the
   PERCLOS window is warming up.
4. Insufficient valid duration/coverage produces `UNKNOWN` with a warm-up reason.
5. A ready window without PERCLOS produces `UNKNOWN`.
6. PERCLOS at or above `perclos_threshold` produces `ALERT`.
7. A ready, valid PERCLOS below the threshold produces `NORMAL`.

Threshold equality is inclusive for alerts. Missing or invalid evidence never becomes
`NORMAL`. Current defaults are configuration values for research evaluation, not certified
driver-safety thresholds.

## Recorded configuration

Every run result serializes the resolved `closed_seconds`, `window_seconds`,
`min_valid_seconds`, `min_coverage`, `max_gap_seconds`, and `perclos_threshold` values with
the remaining configuration. Per-frame CSV records include closure duration, PERCLOS,
coverage, valid duration, readiness, state, and reason.
