# Experiment Record Contract

DrowsyAlert can write two complementary local artifacts:

- `--log <path.csv>` writes the stable per-frame evidence fields used for inspection.
- `--record <path.json>` writes schema-versioned run metadata plus the same scalar
  frame records. It never includes frame pixels or eye crops.

Both paths are generated outputs and remain ignored by Git under `outputs/`.
Experiment files are created without silently replacing an existing JSON record.

## Example

```powershell
uv run drowsyalert --video <permitted-clip.mp4> --headless --mute `
  --method perclos-yawn `
  --dataset-id <dataset-version> --split-id <split-manifest-id> `
  --seed 42 --code-revision <git-commit> `
  --log outputs/logs/clip-001.csv `
  --record outputs/results/clip-001.json
```

The JSON record contains:

- schema version, deterministic run ID, UTC creation time, completion/error state;
- package/code revision and non-identifying runtime environment;
- dataset and split IDs, privacy-safe source ID and video content hash;
- method A/B/C identity, common settings, active auxiliary cue and cue settings;
- resolved configuration hash and full resolved configuration;
- eye source, threshold, optional checkpoint hash, and face-model filename;
- random seed and final audio policy/state;
- scalar per-frame observations, temporal/cue evidence, decision and processing time;
- frame count, wall time and measured processing throughput.

The run ID is a hash of the declared creation time and scientific identities. Supplying
the same inputs and creation time produces the same ID; changing configuration or an
identity changes it. Dataset ID, split ID, and code revision are allowed to be absent
for an informal demo, but the record then sets `provenance_complete` to false and lists
the missing fields. Such a run is not complete research evidence.

Camera records use a non-personal `camera:<index>` source identity. Video records use a
content-hash-derived source identity and the full SHA-256 rather than exposing a local
filename or absolute path. Raw images, participant names, and local paths must not be
added to records. Dataset manifests stored under the approved private-data policy map
content hashes to authorized clip IDs.

If processing fails after record creation, the JSON status is `error`, completed scalar
frames are retained, and the exception type/message is recorded. It is never labelled
as a completed run. Metrics and comparative conclusions remain Phase 6 work and require
an approved temporal dataset and frozen evaluation protocol.
