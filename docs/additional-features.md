# Additional Research Features

Method B and Method C add one auxiliary landmark cue to the unchanged Method A
PERCLOS baseline. Their current numerical values in `configs/config.yaml` are
configurable implementation defaults. They are not validated safety thresholds and must
be selected on training/validation material, then frozen before held-out evaluation.

## Method B: PERCLOS plus yawning

Mouth aspect ratio (MAR) uses MediaPipe landmark pairs 61/291 for mouth width and
82/87 plus 312/317 for two vertical openings. A mouth observation is valid only when
these landmarks are present, finite, and have non-degenerate width.

A yawn candidate begins when valid MAR is at least `yawn_threshold`. It becomes one
event after the opening remains continuously valid for at least `yawn_seconds`.
Threshold equality is inclusive. The same continuous opening cannot produce another
event until a valid below-threshold observation closes it. Missing/invalid observations
and gaps longer than `max_gap_seconds` reset the candidate without creating an event.
Completed events remain in the rolling `window_seconds` interval, and Method B's
auxiliary path requires at least `yawn_count` events.

Run evidence distinguishes the rolling count, current MAR, a newly completed event,
continuous candidate duration, cue validity, and an unavailable reason. Method A and
Method C do not calculate or consume this yawn evidence.

## Research limitation

MAR can respond to speech, facial expression, camera angle, or landmark error. A yawn
event is therefore a configured geometric indicator, not proof of physiological
drowsiness. Its threshold and duration require validation-only selection before any
comparative claim.
