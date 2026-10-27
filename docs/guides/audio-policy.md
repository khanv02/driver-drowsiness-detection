# Audio warning policy

Audio is a live presentation side effect. Detection and decision state do not depend on
speaker availability or playback success.

- The first live `ALERT` requests asynchronous playback immediately.
- A sustained alert can replay only when `cooldown_seconds` has elapsed.
- Returning to `NORMAL` or `UNKNOWN` stops active playback.
- A new alert during the existing cooldown remains visible but does not replay early.
- `--mute` disables playback without changing eye, temporal, or decision behavior.
- Recorded-video replay is silent by policy so experiments do not emit sound.
- A missing sound or playback/stop failure is recorded and does not change the decision.

Every run summary records whether audio was enabled and available, the live/muted/replay
policy, play and failure counts, the cooldown, sound identity, and last error. Actual speaker
output still requires the Phase 4 manual hardware check.
