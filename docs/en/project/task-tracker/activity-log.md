# DrowsyAlert Activity Log

This is a project-documentation log of reviewed artifacts and repository changes. It is
not a personal browsing history or a record of activity outside this repository.

## 2026-11-01 - Validation replay and bounded sweep

**Reviewed**

- `src/drowsyalert/experiments/batch.py`, `evaluation.py`, `records.py`, and `replay.py`
- Stored validation batch plan, run records, annotations, and the v1.1 comparison
- `docs/en/guides/evaluation-execution.md` and its Vietnamese counterpart

**Changes recorded**

- Added deterministic validation-only replay that recomputes eye, temporal, yawn,
  head-pose, and decision states from stored frame observations without rerunning the
  face landmarker or reading video.
- Added a bounded configuration grid, per-candidate A/B/C metrics, configuration hashes,
  and a validation-only guard that rejects test plans and test annotations.
- Added `scripts/replay_validation_sweep.py`, `load_batch_plan`, and focused replay tests.
- Marked T-157 complete and refreshed the English/Vietnamese status indexes to 171 task
  IDs, 152 complete, and 19 open.

**Verification status**

- Replaying the stored validation records with the frozen v1.1 configuration reproduced
  the stored A/B/C comparison exactly: TP 5, FP 28, FN 14, F1 0.19230769230769232,
  coverage 0.629932320265611, and mean latency 2.904000000000001 seconds for A, B, and C.
- `python -m pytest tests/test_experiment_replay.py tests/test_experiments.py -q` passed
  (16 tests).
- `python -m ruff check src scripts demo tests` passed.
- `uv run` failed in this environment with a trampoline path error, so the checks were run
  through the repository virtual environment directly.
- This work is validation-only. No held-out test result, frozen final configuration, or
  report/slide claim was produced.

## 2026-10-27 - Status reconciliation

**Reviewed**

- `.specify/memory/constitution.md`
- `specs/001-drowsyalert/spec.md`, `plan.md`, `tasks.md`, and `decisions.md`
- `docs/research/evaluation-protocol.md` and `docs/research/validation-evaluation-v1.1.md`
- `docs/project/verification.md`, `docs/project/phase6-team-handoff.md`, both dataset cards, and `README.md`
- Current Git branch and working-tree status

**Changes recorded**

- Reconciled SPEC open-question statuses and PLAN/TASKS readiness with the approved
  NITYMED Protocol v1.1 and current Phase 6 evaluation status. Requirement behavior was
  not changed.
- Corrected stale data-readiness text in the plan and dataset cards; separated approved
  source/protocol choices from annotation and held-out evidence still pending.
- Reconciled G0-05 through G0-09 decision statuses with the completed CEW evaluation,
  approved NITYMED protocol, remaining threshold work, and deferred volunteer collection.
- Removed the unrelated T-018 physical webcam/audio dependency from T-022. Marked T-022
  complete based on completed T-119-T-122 work; kept manual hardware acceptance open as
  T-018.
- Updated the G5, Phase 6, and task-count summaries. Current canonical checklist count:
  160 task IDs, 147 complete, 13 open.
- Added English and Vietnamese task-status indices under this folder. The canonical task
  definitions and acceptance criteria remain in `specs/001-drowsyalert/tasks.md`.
- Updated the root README to report G5 software acceptance, Phase 6 open work, and links
  to the task indices and activity log.
- Clarified the system-Accuracy bin rule after review: one-second width and stride with
  no neighboring-bin overlap; 0.50 is the separate within-bin occupancy threshold.

**Verification status**

- Checked that the bilingual status indices contain the same 160 IDs and match the
  canonical checkbox state.
- `git diff --check` passed.
- No application tests were run; this change updates project documentation and task
  status only. Physical webcam/audio acceptance and held-out A/B/C evaluation remain
  unverified/open.
- Review clarification was checked across Protocol §7, metric documentation, SPEC OQ-004,
  and decision G0-07; no evaluation code or scoring results changed.
