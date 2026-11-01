# Controlled A/B/C Evaluation Execution

The batch runner creates one immutable plan and uses it for methods A, B, and C. The plan
contains the exact clip list, NITYMED manifest hash, split ID, code revision, seed,
landmark-EAR source, and one shared resolved configuration. Method specifications differ
only by the declared auxiliary cue.

The runner refuses to build a plan unless:

- all selected worklist clips are `reviewed` and assigned to the requested partition;
- the video manifest and worklist paths agree;
- the eye source is `landmark_ear`;
- all shared threshold/window/cue settings are present;
- method C has a numeric, validation-frozen head-pose reference;
- data/split/manifest/code identities are present.

Every replay is forced to `headless=True`, `mute=True`, and the EAR backend. Run records
use the stable clip ID plus the real source SHA-256. Existing records are resumed only if
their clip, hash, method, source, eye backend, completion state, and audio policy match;
incompatible collisions are rejected rather than overwritten.

After T-126/T-139, run validation first with a dedicated frozen evaluation config:

```powershell
uv run python scripts/run_video_evaluation.py `
  --manifest data/processed/nitymed/video-manifest.csv `
  --worklist data/processed/nitymed/annotation-worklist.csv `
  --video-root data/raw/nitymed/DSM_Dataset-HDTV720 `
  --output outputs/results/nitymed-validation-v1 `
  --partition validation --split-id nitymed-split-v1 `
  --code-revision <git-commit> --seed 42 `
  --config configs/evaluation-v1.yaml
```

Do not use the current demo config unchanged: its head-pose reference is intentionally
`null`, so controlled method C is blocked until validation fixes a numeric reference.

When final annotations and protocol values are approved, add:

```powershell
  --annotations data/processed/nitymed/annotations.csv `
  --early-tolerance 1.0 --late-tolerance 2.0 `
  --bin-seconds 1.0 --positive-fraction 0.5 `
  --reference-label microsleep
```

Those values are frozen by Protocol `drowsyalert-video-eval-v1.1`. The comparison exporter
reloads all planned records, recalculates each method from the same clips and annotations,
and writes one strict JSON comparison. Validation results may guide threshold selection;
held-out test results must not be used for tuning.

## Offline validation replay and bounded sweep

Once the planned validation records exist, replay recomputes eye, temporal, yawn, head-pose,
and decision states from the stored frame observations. It does not run the face landmarker,
does not read video, and refuses test partitions or test annotations. The same record set,
annotations, protocol, and plan identity are reused for every candidate.

```powershell
uv run python scripts/replay_validation_sweep.py `
  --plan outputs/results/nitymed-validation-v1.1/batch-plan.json `
  --annotations data/processed/nitymed/validation-annotations-v1.1.csv `
  --output outputs/results/nitymed-validation-v1.1/sweep.json `
  --early-tolerance 1.0 --late-tolerance 2.0 `
  --bin-seconds 1.0 --positive-fraction 0.5 `
  --reference-label microsleep
```

The default pre-declared grid varies temporal window, warm-up duration, minimum coverage,
PERCLOS threshold, prolonged-closure threshold, and EAR threshold. It is capped at 350
combinations; invalid combinations such as a warm-up longer than the window are skipped.
Every output candidate contains its full resolved configuration, config SHA-256, per-method
A/B/C metrics, and one aggregate record. T-158 selects from this validation output; the
sweep must never be pointed at held-out records.
