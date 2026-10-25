# CLI and Local Output Contract

DrowsyAlert is a local Python command-line application with no network API or service. The installed command is `drowsyalert` from the root `pyproject.toml`.

## Inputs

- A local webcam (`--camera`, default 0) or recorded video (`--video`), mutually exclusive.
- Optional `--config`, `--face-model`, `--checkpoint`, `--eye-backend ear|cnn`, `--method perclos|perclos-yawn|perclos-head-pose`, `--max-frames`, and `--log`.
- `--headless` suppresses display; `--mute` suppresses live audio. Replay is silent by default.
- `--download-model` explicitly downloads the configured face asset and exits; network is needed only for this action.

Invalid camera/video/model/config/backend returns a non-zero exit and readable error. Camera read failure stops decisions; end-of-file is normal.

## Outputs

- Windowed mode shows selected input, observation availability, status/reason and visible warning.
- Successful CLI runs print JSON with frame count, wall time, measured throughput and resolved configuration (no sensitive identity values).
- Optional CSV logs use video-media timestamps for replay and monotonic elapsed timestamps for webcam, and identify source, method, eye-state source, evidence, unknown status, decision/reason and processing time. Event summaries identify annotation/matching policy.
- Audio is an alert side effect with cooldown. Mute changes audio only, not detection.

Treat the current CSV schema as provisional until documented and tested. Current options are defined by `drowsyalert.main.build_parser()`.
