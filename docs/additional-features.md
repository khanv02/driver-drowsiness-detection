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

## Method C: PERCLOS plus relative head pose

Head pose uses a six-point perspective-n-point estimate. Positive relative pitch is
defined as head-down for this implementation. The evidence records the relative
pitch/yaw/roll tuple, validity, sustained head-down duration, Boolean sustained
indicator, reference pitch, and an unavailable reason.

`head_pose_reference_degrees` may supply a fixed absolute pitch reference. A controlled
experiment must use and record a reference selected by its approved validation
protocol. When the setting is `null`, the live/demo tracker captures the first valid
pitch as its reference and records that acquisition in the evidence. This automatic
mode is convenient for a demonstration but must not be treated as a validated neutral
pose or silently used to tune held-out test material.

Relative pitch at or above `head_down_degrees` starts a candidate. The indicator becomes
true after continuous valid evidence for at least `head_down_seconds`; both boundaries
are inclusive. A below-threshold sample, invalid pose, missing face, or gap longer than
`max_gap_seconds` resets duration. The reference remains fixed for the run.

Pose from a monocular landmark model depends on camera geometry and is not a physical
measurement of fatigue. Method C's thresholds and reference procedure require
validation before research comparison.

## Controlled method matrix

| ID | CLI method | Shared evidence | Additional evidence |
| --- | --- | --- | --- |
| A | `perclos` | Eye source, sustained closure, PERCLOS window/readiness and primary threshold | None; auxiliary cues are ignored |
| B | `perclos-yawn` | The unchanged Method A settings | Valid rolling yawn count in the combined-PERCLOS band |
| C | `perclos-head-pose` | The unchanged Method A settings | Valid sustained relative head-down evidence in the combined-PERCLOS band |

All methods alert on the same prolonged-closure or primary-PERCLOS rule. Between
`combined_perclos_threshold` and `perclos_threshold`, B or C requires its named valid
cue. If that required cue is unavailable, the decision is `UNKNOWN`, not `NORMAL`.
Below the combined threshold, unavailable auxiliary evidence does not affect the normal
base decision. Each runtime result contains a method ID, eye source, shared settings,
auxiliary cue name, and that cue's resolved settings. Per-frame CSV rows contain only
the active method identity plus both cue validity fields so missing evidence remains
auditable.
