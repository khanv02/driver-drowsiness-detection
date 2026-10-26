# Tasks: DrowsyAlert

**Feature**: `specs/001-drowsyalert`
**Basis**: SRS `spec.md`, current repository root, and the seven workstreams in the task request.
**Plan status**: The project owner approved `spec.md`, `plan.md`, Constitution v1.0.0, and the available Project 12 source on 2026-10-26. Research/data decisions remain owned blockers for their dependent tasks. The dirty Git baseline must be reviewed before branch or commit operations.

## How to execute this task list

Each T-task below is a parent work package. Before starting one, split it into leaf tasks that change one behavior or one artifact at a time; aim for a task that can be implemented, verified, and reviewed in one focused Codex session. Add leaf tasks to the active phase with stable IDs before implementation, and check the parent only after all its leaf tasks pass their acceptance checks. Do not pre-decompose later research decisions into guessed implementation details. “Tests” means tests or observable checks are part of the task, not a separate end-only activity. Data collection and research protocol tasks are labelled **Research/Data** and must be completed by an authorized human with consent and provenance records. Do not check off a task solely because a corresponding file or scaffold already exists; verify behavior against its acceptance evidence.

### Branch and recovery workflow

The root-layout migration is preserved at commit `3f717de` on `checkpoint/root-layout`; the original `master` branch remains unchanged. `feature/001-drowsyalert` starts from that checkpoint. Use one short-lived `task/T-###-slug` branch per leaf task. Keep each branch focused, verify the task's checks, review the diff, commit, and merge into the feature branch. Never use `git reset --hard` or rewrite shared branch history as a recovery shortcut. Recover by abandoning an unmerged task branch or reverting its task commit; the feature branch and accepted commits remain recoverable.

### Gate G0 — approval before implementation

The feature owner/supervisor must record approval of the Draft SRS, the constitution adoption date, approval of the existing completed plan, and the exact Project 12 source document revision as recorded in `spec.md` OQ-002. Dataset/license, temporal ground truth, decision thresholds, and consent/ethics decisions must be resolved or assigned with explicit owners and blocking effects. No application code changes are authorized by this task list before G0. This is an approval gate, not an invitation for the coding agent to invent missing decisions.

## Phase 1 — Project Foundation

**Milestone outcome**: verified environment, project conventions, approved protocol/design prerequisites, and a safe data/documentation foundation.

- [X] T-001 — Verify implementation prerequisites and approval gate (Research/Planning)

- **Phase:** 1 — Foundation; Gate G0.
- **Priority:** P0.
- **Dependencies:** None.
- **Requirements:** NFR-005–NFR-007; DR-001, DR-004–DR-007; RA-005; SRS OQ-001, OQ-002, OQ-005–OQ-009.
- **Objective:** Record environment facts and obtain the human approvals needed before code or participant-data work begins.
- **Implementation Steps:** Review `specs/001-drowsyalert/spec.md`, `.specify/memory/constitution.md`, `specs/001-drowsyalert/plan.md`, `docs/PhieuMoTaDeTai_30DeTai_ThiGiacMayTinh_NCKH.docx`, and the current app. Confirm SRS approval, constitution ratification date, intended official DOCX revision, completed plan approval, dataset candidate/license, temporal ground-truth protocol, and participant/ethics guidance. Record unresolved items; do not choose them silently.
- **Expected Artifacts:** Approval/decision record in `specs/001-drowsyalert/decisions.md` or approved project review record; constitution ratification date; owner-approved `specs/001-drowsyalert/plan.md`.
- **Verification:** Reviewer confirms each G0 item is either approved with evidence or explicitly deferred with an owner and blocking effect; the existing detailed `plan.md` has owner approval and blocking protocol decisions are recorded.
- **Definition of Done:** All G0 items are recorded and accepted by the project owner/supervisor. Until then, implementation tasks remain blocked; read-only environment inspection may proceed.

### T-001 leaf tasks — G0 authority and decision record

T-001 is complete only when all leaf tasks below are checked. Approval tasks must be completed by the named owner/supervisor; an implementation agent must not mark them complete from inference.

- [X] T-036 [Parent: T-001] Inventory the SRS, constitution, plan, official-source candidate, and open research decisions in `specs/001-drowsyalert/decisions.md`.
- [X] T-037 [Parent: T-001] Record owners, blocking effects, source-file identity, and the safe Git baseline decision in `specs/001-drowsyalert/decisions.md` (depends on T-036).
- [X] T-038 [Parent: T-001] Record project owner/supervisor approval of the Draft SRS and detailed plan in `specs/001-drowsyalert/decisions.md` (depends on T-037; human approval required).
- [X] T-039 [Parent: T-001] Record Constitution v1.0.0 adoption and ratification date in `.specify/memory/constitution.md` and `specs/001-drowsyalert/decisions.md` (depends on T-037; human approval required).
- [X] T-040 [Parent: T-001] Confirm whether the available unsuffixed Project 12 DOCX is the authoritative revision and record the answer in `specs/001-drowsyalert/decisions.md` (depends on T-037; human confirmation required).
- [X] T-041 [Parent: T-001] Review and accept the owners/blocking effects for dataset, temporal ground truth, metrics, thresholds, consent, and Git baseline decisions in `specs/001-drowsyalert/decisions.md` (depends on T-038–T-040; human approval required).
- [X] T-051 [Parent: T-001] Preserve the reviewed root-layout migration at checkpoint `3f717de`, keep `master` unchanged, and create `feature/001-drowsyalert` from that checkpoint (depends on T-041; owner approved).

- [X] T-002 — Audit and record the current environment (Coding/Environment)

- **Phase:** 1 — Foundation.
- **Priority:** P0.
- **Dependencies:** None; do not change source/dependencies before G0.
- **Requirements:** NFR-002–NFR-003, NFR-005; RA-006.
- **Objective:** Establish a reproducible baseline of the existing runtime and development environment.
- **Implementation Steps:** From the repository root, record Python and `uv` versions, OS/platform, dependency-lock status, installed optional CNN support, available webcam/video test resources, and whether required model/data assets exist. Clearly distinguish observed facts from planned capabilities.
- **Expected Artifacts:** `docs/environment-audit.md` (or the approved plan's designated documentation path).
- **Verification:** A reviewer can reproduce the listed version and asset checks; no credentials, personal footage, or unnecessary machine identifiers are recorded.
- **Definition of Done:** Audit records present/missing prerequisites and limitations without modifying application behavior.

### T-002 leaf tasks — Environment audit

Complete these small tasks in order. T-002 is complete only when all four leaf tasks are checked.

- [X] T-032 [Parent: T-002] Record Python, `uv`, operating system, and platform versions in `docs/environment-audit.md`.
- [X] T-033 [Parent: T-002] Record lockfile/dependency status and whether the optional PyTorch environment is available in `docs/environment-audit.md` (depends on T-032).
- [X] T-034 [Parent: T-002] Inventory model/data assets and available non-personal video fixtures; record missing items without downloading data or capturing webcam footage in `docs/environment-audit.md` (depends on T-033).
- [X] T-035 [Parent: T-002] Review the audit for reproducibility and remove unnecessary machine-identifying details; verify each recorded fact has a reproducible command or source in `docs/environment-audit.md` (depends on T-034).

- [X] T-003 — Review dependencies and project layout against the approved design (Coding/Environment)

- **Phase:** 1 — Foundation.
- **Priority:** P1.
- **Dependencies:** T-001 for design conformance; T-002 for environment facts.
- **Requirements:** NFR-005, NFR-006; RA-006.
- **Objective:** Identify only dependency or layout gaps needed for approved requirements; avoid duplicating existing modules.
- **Implementation Steps:** Compare approved `plan.md` with `pyproject.toml`, `src/drowsyalert/`, `tests/`, and `README.md`. Inventory what exists versus what is verified. Propose dependency changes only with a specific requirement and plan rationale.
- **Expected Artifacts:** Reviewed dependency/layout note in `docs/environment-audit.md` or approved plan location; narrowly scoped dependency changes only if the owner-approved plan requires them.
- **Verification:** Each proposed change maps to a SPEC ID and has a platform/installation rationale; existing modules and tests are not recreated unnecessarily.
- **Definition of Done:** Reviewer accepts the gap list and any required dependency decision before implementation.

### T-003 leaf tasks — Dependency and layout review

- [X] T-042 [Parent: T-003] Compare the approved root layout with `pyproject.toml`, `src/drowsyalert/`, `scripts/`, `tests/`, and `README.md`; record the result in `docs/environment-audit.md`.
- [X] T-043 [Parent: T-003] Map runtime, CNN, training, and development dependencies to observed imports and plan responsibilities in `docs/environment-audit.md` (depends on T-042).
- [X] T-044 [Parent: T-003] Record missing assets, experiment/test modules, documentation-language drift, and provisional-config limitations without changing dependencies in `docs/environment-audit.md` (depends on T-043).
- [X] T-045 [Parent: T-003] Review the Phase 1 gap list and record that no dependency or layout change is currently justified (depends on T-044).

- [X] T-004 — Establish configuration, test, and data-handling conventions

- **Phase:** 1 — Foundation.
- **Priority:** P0.
- **Dependencies:** T-001, T-003.
- **Requirements:** FR-018–FR-020; NFR-005–NFR-007; DR-004–DR-007.
- **Objective:** Make configuration, test organization, run provenance, and private-data boundaries explicit.
- **Implementation Steps:** Reconcile current config and test paths with the approved plan; define where tests for each behavior live, how thresholds/settings are recorded per run, which data/model/output paths are private or ignored, and how consent/provenance records are stored without committing participant footage.
- **Expected Artifacts:** Updated `docs/architecture.md` or approved plan-designated convention document; updates to `.gitignore` only if required by the approved data policy; documented test map.
- **Verification:** Paths/policies are clear, and a repository-status check with a dummy private-data path confirms it is excluded from version control.
- **Definition of Done:** Reviewer approves conventions; no real participant data is created or added during this task.

### T-004 leaf tasks — Project conventions

- [X] T-046 [Parent: T-004] Document tracked configuration, validation, path, and resolved-run requirements in `docs/development-conventions.md`.
- [X] T-047 [Parent: T-004] Map core behaviors to current and planned focused test modules in `docs/development-conventions.md` (depends on T-046).
- [X] T-048 [Parent: T-004] Document data, model, output, consent, and provenance boundaries in `docs/development-conventions.md` (depends on T-046).
- [X] T-049 [Parent: T-004] Document the task-branch and non-destructive recovery workflow in `docs/development-conventions.md` (depends on T-046).
- [X] T-050 [Parent: T-004] Verify with `git check-ignore` that representative private data, checkpoint, and generated-result paths are excluded; record the outcome in `docs/development-conventions.md` (depends on T-048).

### Phase 1 acceptance gate

G1 passes when T-001 through T-004 are complete, the approved architecture and protocol are available, dependencies and test conventions are understood, and data/privacy boundaries are reviewable. No model training or volunteer capture begins before its applicable approvals and license/consent checks.

**G1 status (2026-10-26): Passed.** T-001–T-004 and their Phase 1 leaf tasks are complete. Dataset, training, volunteer-data, and evaluation prerequisites remain explicit blockers for their later tasks.

## Phase 2 — Landmark and PERCLOS Baseline

**Milestone outcome**: deterministic local/video observation path, valid landmark-derived eye evidence, timestamp-based PERCLOS, and tested missing-observation handling.

- [X] T-052 [Parent: Phase 2] Decompose T-005–T-009 into independently reviewable source, validity, EAR, temporal, and integration leaf tasks in `specs/001-drowsyalert/tasks.md`.

- [X] T-005 — Verify and complete webcam/video input behavior

- **Phase:** 2 — Landmark and PERCLOS Baseline.
- **Priority:** P0.
- **Dependencies:** G1; T-004.
- **Requirements:** FR-001, FR-002, FR-017; NFR-004.
- **Objective:** Make local live and recorded sources explicit, timestamped, stoppable, and failure-aware.
- **Implementation Steps:** Inspect `src/drowsyalert/pipeline/source.py` and `tests/`. Preserve valid existing behavior; add or adjust source handling for open failure, end-of-file, camera disconnection, monotonic live capture time, recorded-media timestamps, cleanup, and stopping. Add focused automated tests using synthetic/fake sources and a small approved non-personal fixture if available.
- **Expected Artifacts:** `src/drowsyalert/pipeline/source.py`; `tests/test_source.py` or the existing approved test module.
- **Verification:** Tests cover successful camera/video abstractions, unavailable input, EOF/disconnect, timestamps, and cleanup without requiring a physical camera in CI.
- **Definition of Done:** Both input modes provide documented timestamp semantics and failures do not reuse stale frames; focused tests pass.

### T-005 leaf tasks — Input and timestamps

- [X] T-053 [Parent: T-005] Add focused fake-capture tests for open failure, video EOF, camera failure, cleanup, source kind, and timestamp fallback in `tests/test_source.py`.
- [X] T-054 [Parent: T-005] Implement explicit source kind/timebase and verified monotonic live/media timestamp behavior in `src/drowsyalert/pipeline/source.py` (depends on T-053).
- [X] T-055 [Parent: T-005] Run focused source tests and Ruff, then record T-005 completion in `specs/001-drowsyalert/tasks.md` (depends on T-054).

- [X] T-006 — Verify face/landmark and eye-region validity

- **Phase:** 2 — Landmark and PERCLOS Baseline.
- **Priority:** P0.
- **Dependencies:** T-005; G1.
- **Requirements:** FR-003, FR-004, FR-015–FR-017.
- **Objective:** Ensure one-person landmark observations and eye crops are explicitly valid or unknown.
- **Implementation Steps:** Review `src/drowsyalert/detection/face.py`, `src/drowsyalert/types.py`, and `tests/test_detection.py`. Extend tests for no face, malformed/out-of-frame landmarks, insufficient eye region, partial occlusion/uncertainty, and multiple-face ambiguity. Keep subject signals from separate people from being combined; follow the approved plan on selection versus withholding.
- **Expected Artifacts:** Existing detection/type files as needed; `tests/test_detection.py`.
- **Verification:** Synthetic observations cover valid and invalid boundaries; no-face/multiple-face outputs cannot become open-eye observations.
- **Definition of Done:** Detection and eye-region outputs have tested validity semantics and preserve the single-person constraint.

### T-006 leaf tasks — Face and per-eye validity

- [X] T-056 [Parent: T-006] Add tests for no face, multiple-face ambiguity, malformed landmarks, out-of-frame/degenerate eyes, and independent per-eye validity in `tests/test_detection.py`.
- [X] T-057 [Parent: T-006] Extend `FaceObservation` with explicit per-eye validity and nullable per-eye crops/boxes/EAR values in `src/drowsyalert/types.py` (depends on T-056).
- [X] T-058 [Parent: T-006] Implement no-face/multiple-face selection and independent eye validation in `src/drowsyalert/detection/face.py`; adapt presentation/log consumers as needed (depends on T-057).
- [X] T-059 [Parent: T-006] Run focused detection tests and Ruff, then record T-006 completion in `specs/001-drowsyalert/tasks.md` (depends on T-058).

- [X] T-007 — Define and test landmark-derived eye-state estimation

- **Phase:** 2 — Landmark and PERCLOS Baseline.
- **Priority:** P0.
- **Dependencies:** T-006; approved eye-closure definition from G0.
- **Requirements:** FR-006, FR-015; NFR-001; RA-002, RA-004.
- **Objective:** Provide a landmark-only open/closed/unknown state suitable for the primary PERCLOS research question.
- **Implementation Steps:** In `src/drowsyalert/models/ear.py` and/or the approved feature module, implement or reconcile the approved 2D eye-landmark measurement and open/closed decision rule. Keep it distinct from the CNN. Add tests for both eyes, unilateral/wink behavior if specified, boundary threshold, invalid geometry, and unknown evidence.
- **Expected Artifacts:** `src/drowsyalert/models/ear.py` (or approved equivalent); `tests/test_detection.py` or focused `test_eye_state.py`.
- **Verification:** Deterministic landmark fixtures exercise open, closed, boundary, and invalid cases; rule/threshold are recorded in configuration.
- **Definition of Done:** Landmark eye-state source is independently testable and named separately in outputs and documentation.

### T-007 leaf tasks — Landmark eye state

- [X] T-060 [Parent: T-007] Add tests for threshold equality, bilateral closure, one valid open eye, one valid closed eye with the other invalid, and invalid EAR evidence in `tests/test_eye_state.py`.
- [X] T-061 [Parent: T-007] Implement the approved bilateral landmark-EAR `OPEN`/`CLOSED`/`UNKNOWN` policy and source identity in `src/drowsyalert/models/ear.py` and `src/drowsyalert/types.py` (depends on T-060).
- [X] T-062 [Parent: T-007] Run focused landmark eye-state tests and Ruff, then record T-007 completion in `specs/001-drowsyalert/tasks.md` (depends on T-061).

- [X] T-008 — Verify timestamp-based PERCLOS and tracking-loss semantics

- **Phase:** 2 — Landmark and PERCLOS Baseline.
- **Priority:** P0.
- **Dependencies:** T-005, T-007; approved temporal policy from G0.
- **Requirements:** FR-007, FR-015; NFR-004, NFR-006; RA-002.
- **Objective:** Calculate PERCLOS from valid observed duration and report coverage/readiness without counting gaps as open or closed.
- **Implementation Steps:** Review `src/drowsyalert/features/temporal.py` and `tests/test_temporal.py`. Reconcile window, coverage, gap, closure, timestamp, and unknown behavior with approved research protocol; retain timestamp weighting and add/adjust tests for irregular sampling, boundary clipping, unknown intervals, insufficient coverage, and invalid/nonmonotonic timestamps.
- **Expected Artifacts:** `src/drowsyalert/features/temporal.py`; `tests/test_temporal.py`; protocol/configuration documentation.
- **Verification:** Hand-calculated timestamp sequences match expected closed-duration/valid-duration PERCLOS; gaps reduce valid coverage and never become open observations.
- **Definition of Done:** Core temporal behavior passes deterministic tests and emits source, coverage, readiness, and configured window.

### T-008 leaf tasks — Timestamp-weighted temporal behavior

- [X] T-063 [Parent: T-008] Add deterministic tests for irregular intervals, window clipping, unknown/gap exclusion, closure reset, invalid timestamps, readiness, source, and window metadata in `tests/test_temporal.py`.
- [X] T-064 [Parent: T-008] Complete temporal source/window metadata and interval behavior in `src/drowsyalert/features/temporal.py` and `src/drowsyalert/types.py` (depends on T-063).
- [X] T-065 [Parent: T-008] Run focused temporal tests and Ruff, then record T-008 completion in `specs/001-drowsyalert/tasks.md` (depends on T-064).

- [X] T-009 — Establish landmark/PERCLOS baseline integration gate

- **Phase:** 2 — Landmark and PERCLOS Baseline.
- **Priority:** P0.
- **Dependencies:** T-005–T-008.
- **Requirements:** FR-001–FR-004, FR-006–FR-007, FR-015–FR-017; NFR-004; RA-002.
- **Objective:** Verify the landmark baseline end to end on repeatable input before CNN or extra features.
- **Implementation Steps:** Connect source, face observation, landmark eye-state, temporal PERCLOS, and status path in `src/drowsyalert/pipeline/realtime.py` only as necessary. Add an integration test using deterministic frames/observations; document manual webcam check separately.
- **Expected Artifacts:** `src/drowsyalert/pipeline/realtime.py`; `tests/test_pipeline.py`; `docs/verification.md`.
- **Verification:** Automated replay confirms state/PERCLOS/unknown transitions and timestamp source; a manual local webcam check records environment and outcome without claiming general performance.
- **Definition of Done:** G2 review demonstrates valid and invalid observation paths; tests pass before CNN work proceeds.

### T-009 leaf tasks — Baseline integration gate

- [X] T-066 [Parent: T-009] Add a deterministic fake-source/fake-detector integration test covering valid, unknown, and timestamped replay records in `tests/test_pipeline.py`.
- [X] T-067 [Parent: T-009] Complete landmark-source/timebase/window/coverage metadata in `src/drowsyalert/pipeline/realtime.py` and keep offline replay silent (depends on T-066).
- [X] T-068 [Parent: T-009] Record automated replay evidence and any unavailable webcam/model/manual checks in `docs/verification.md` without claiming skipped hardware checks passed (depends on T-067).
- [X] T-069 [Parent: T-009] Run the Phase 2 test/lint suite, update requirement evidence and G2 status, and mark T-009 complete in `specs/001-drowsyalert/tasks.md` (depends on T-068).
- [X] T-070 [Parent: Phase 2] Run the final Phase 2 suite and Ruff checks, confirm every T-005–T-009 leaf task is complete, and clear staged/diff formatting errors before merging the phase branch.

### Phase 2 acceptance gate

G2 passes when T-005–T-009 are complete; recorded input is repeatable; landmark-derived eye state and PERCLOS are separately traceable; gaps and invalid input remain unknown; unit and integration tests pass. No CNN accuracy claim is made at this gate.

**G2 status (2026-10-26): Passed for automated code progression.** The full suite reports 41 passed and 1 optional-CNN skip; Ruff passes. Physical webcam, real Face Landmarker asset, real video codec, and audio checks remain explicitly unverified in `docs/verification.md` and are not claimed as passed.

## Phase 3 — CNN Eye Classification

**Milestone outcome**: lawful and leakage-aware eye-image data pipeline, trained classifier, independent held-out metrics, and explicit CNN inference integration.

- [X] T-071 [Parent: Phase 3] Decompose T-010–T-014 into independently reviewable dataset, preparation, training, evaluation, and inference tasks in `specs/001-drowsyalert/tasks.md`.

- [X] T-010 — Select and document eye-state dataset and split (Research/Data)

- **Phase:** 3 — CNN Eye Classification.
- **Priority:** P0.
- **Dependencies:** G1; T-004.
- **Requirements:** DR-001–DR-003, DR-005–DR-007; NFR-006–NFR-007; RA-004–RA-005.
- **Objective:** Establish a permitted dataset and reproducible open/closed labels without assuming a particular dataset is accessible.
- **Implementation Steps:** Research candidate public eye-state data including the instructor-named Kaggle source; verify access, license/terms, version, provenance, label definition, subject/session identifiers, and suitability. Select only after review. Design train/validation/test separation by subject/session where possible and record leakage limits. Do not download or commit restricted/personal data.
- **Expected Artifacts:** `data/README.md`; `docs/dataset-card.md`; split manifest or documented generation procedure in an approved private/derived-data location.
- **Verification:** Reviewer checks source/version/retrieval date/license/labels/splits and confirms held-out examples do not share subjects/sessions/near-duplicate frames where metadata permits.
- **Definition of Done:** Dataset is approved for intended use and reproducibility; if no suitable lawful dataset is available, task is blocked with documented alternatives rather than fabricated availability.

### T-010 leaf tasks — Dataset authority and split protocol

- [X] T-072 [Parent: T-010] Audit candidate datasets, access terms, provenance, labels, identity metadata, and leakage risks in `docs/dataset-card.md`; reject sources without usable rights evidence.
- [X] T-073 [Parent: T-010] Replace the automatic unknown-license Kaggle downloader with a safe acquisition verifier that never downloads or redistributes data implicitly (depends on T-072).
- [X] T-074 [Parent: T-010] Document the selected CEW acquisition, local layout, labels, split, provenance, and no-redistribution procedure in `data/README.md` and `docs/dataset-card.md` (depends on T-072).
- [X] T-075 [Parent: T-010] Inspect the owner-provided CEW extraction, record source/version/file hashes and actual counts, and approve the real-data manifest before training (depends on T-074; owner must provide dataset).

- [X] T-011 — Prepare eye-image labels and dataset loading

- **Phase:** 3 — CNN Eye Classification.
- **Priority:** P1.
- **Dependencies:** T-010; G1.
- **Requirements:** FR-005, DR-001–DR-003, DR-005–DR-007; NFR-006.
- **Objective:** Produce validated training/validation/test samples with unambiguous open/closed labels.
- **Implementation Steps:** Review `src/drowsyalert/models/dataset.py`, `scripts/prepare_dataset.py`, and `tests/test_cnn_dataset.py`. Extend loading/label mapping and validation for missing, ambiguous, and unusable samples; keep private raw data out of Git; record transformations and split identity.
- **Expected Artifacts:** Dataset loader/preparation code under `src/drowsyalert/models/` and `scripts/`; `tests/test_cnn_dataset.py`; dataset documentation.
- **Verification:** Tests use small synthetic fixtures and prove labels, exclusions, and splits are deterministic and auditable; no real dataset statistics are asserted until data are obtained.
- **Definition of Done:** Prepared samples conform to documented label mapping and split manifest; provenance remains attached.

### T-011 leaf tasks — Validated preparation pipeline

- [X] T-076 [Parent: T-011] Add synthetic tests for label mapping, rejected samples, manifest schema, duplicate handling, group-disjoint splits, and deterministic output in `tests/test_cnn_dataset.py` (depends on T-074).
- [X] T-077 [Parent: T-011] Implement strict label/group/manifest validation and leakage-safe deterministic preparation in `src/drowsyalert/models/dataset.py` (depends on T-076).
- [X] T-078 [Parent: T-011] Update the preparation CLI and generated provenance report with source identity, transformations, hashes, split counts, and warnings (depends on T-077).
- [X] T-079 [Parent: T-011] Run the synthetic preparation suite and Ruff checks, then document which real-data assertions remain pending T-075 (depends on T-078).

- [X] T-012 — Train and validate the eye-state CNN

- **Phase:** 3 — CNN Eye Classification.
- **Priority:** P1.
- **Dependencies:** T-011; approved plan's model/training choices.
- **Requirements:** FR-005; NFR-001, NFR-005–NFR-006; RA-004–RA-005.
- **Objective:** Train a CNN classifier and select model settings using training/validation data only.
- **Implementation Steps:** Review `src/drowsyalert/models/eye_cnn.py`, `src/drowsyalert/models/train.py`, and `scripts/train_model.py`. Implement or reconcile training, validation, checkpoint metadata, deterministic seed recording, and class mapping according to the approved plan. Do not use held-out test results for model/threshold selection.
- **Expected Artifacts:** Training code/scripts; checkpoint stored in ignored model artifact location; `docs/training.md`; run metadata.
- **Verification:** A small synthetic or authorized sample run validates the training/checkpoint path; training and validation identities, seed, settings, and metrics are recorded. The full performance claim awaits T-013.
- **Definition of Done:** A compatible checkpoint is reproducibly generated from authorized data and validation selection is documented.

### T-012 leaf tasks — Reproducible training and selection

- [X] T-080 [Parent: T-012] Add tests for deterministic training configuration, validation-only checkpoint selection, class mapping, and checkpoint metadata in `tests/test_cnn_training.py` (depends on T-079).
- [X] T-081 [Parent: T-012] Implement deterministic loaders/training, validation-only selection, and complete checkpoint/run metadata in `src/drowsyalert/models/train.py` and `src/drowsyalert/models/eye_cnn.py` (depends on T-080).
- [X] T-082 [Parent: T-012] Run a tiny synthetic training/checkpoint smoke test without making a performance claim (depends on T-081).
- [X] T-083 [Parent: T-012] Document the reproducible training command, configuration, artifacts, selection rule, and real-data prerequisites in `docs/training.md` (depends on T-082).

- [X] T-013 — Evaluate eye classification on the held-out test split

- **Phase:** 3 — CNN Eye Classification.
- **Priority:** P0.
- **Dependencies:** T-012; frozen split/model/decision rule.
- **Requirements:** NFR-001, NFR-006; RA-002, RA-004–RA-005.
- **Objective:** Report unbiased open/closed image classification performance.
- **Implementation Steps:** Add/complete evaluator in `src/drowsyalert/experiments/` or approved evaluation module. Calculate test sample counts, Accuracy, confusion matrix, and per-class Precision/Recall/F1 with averaging definition; record model/checkpoint identity and confidence/threshold policy. Keep test evaluation one-way after selection is frozen.
- **Expected Artifacts:** Evaluator, `tests/test_cnn_metrics.py`, machine-readable result under ignored `outputs/results/`, and summary in documentation.
- **Verification:** Metric calculations pass known-confusion-matrix tests; report states whether Accuracy ≥0.90 was met without implying it must be.
- **Definition of Done:** Held-out results and protocol are auditable; no unavailable or fabricated data/results.

### T-013 leaf tasks — Frozen held-out evaluation

- [X] T-084 [Parent: T-013] Add known-confusion-matrix tests for counts, Accuracy, per-class Precision/Recall/F1, macro F1, and empty/invalid inputs in `tests/test_cnn_metrics.py` (depends on T-081).
- [X] T-085 [Parent: T-013] Implement a one-way held-out evaluator with checkpoint/manifest identity, threshold policy, and machine-readable results (depends on T-084).
- [X] T-086 [Parent: T-013] Evaluate the frozen checkpoint once on the owner-approved real CEW test split and record whether Accuracy ≥0.90 was met (depends on T-075, T-083, T-085; dataset and model verified).

- [X] T-014 — Integrate CNN inference as a distinct eye-state source

- **Phase:** 3 — CNN Eye Classification.
- **Priority:** P1.
- **Dependencies:** T-007, T-009, T-012; T-013 for performance claims (integration smoke test may precede final report).
- **Requirements:** FR-004–FR-007, FR-015, FR-018; NFR-004, NFR-006.
- **Objective:** Make CNN inference available in the pipeline without conflating its eye state with landmark-derived state.
- **Implementation Steps:** Review `src/drowsyalert/models/eye_cnn.py` and `src/drowsyalert/pipeline/realtime.py`. Integrate confidence/uncertainty behavior, per-eye output, missing-checkpoint errors, selectable PERCLOS source if approved, and explicit source labels in logs/configuration.
- **Expected Artifacts:** Model/pipeline changes; `tests/test_cnn_inference.py`; updated run schema/documentation.
- **Verification:** Tests cover valid predictions, uncertain output, invalid crop, incompatible/missing checkpoint, and source identity; selected source matches the recorded PERCLOS source.
- **Definition of Done:** CNN path is independently selectable and cannot overwrite the identity of the landmark baseline.

### T-014 leaf tasks — Distinct runtime CNN evidence

- [X] T-087 [Parent: T-014] Add tests for per-eye probabilities, configurable uncertainty, bilateral policy, invalid crops, missing/incompatible checkpoints, and source identity in `tests/test_cnn_inference.py` (depends on T-081).
- [X] T-088 [Parent: T-014] Implement explicit CNN uncertainty and bilateral eye-state behavior in `src/drowsyalert/models/eye_cnn.py` (depends on T-087).
- [X] T-089 [Parent: T-014] Integrate CNN checkpoint/source/threshold identity into runtime results and CSV logging without changing the landmark baseline (depends on T-088).
- [X] T-090 [Parent: Phase 3] Run the full Phase 3 suite and Ruff checks; record completed code paths, dataset blockers, and G3 status without fabricating results (code verification depends on T-085 and T-089; final G3 pass depends on T-075 and T-086).

### Phase 3 acceptance gate

G3 passes when a licensed dataset/split is documented, data-loading and training paths are tested, a compatible trained model exists, held-out classification metrics are recorded, and CNN inference is integrated as distinct evidence. If dataset access/rights block the work, G3 is blocked and no accuracy result is claimed.

**G3 status (2026-10-26): Passed.** All Phase 3 parent and leaf tasks are complete. The CEW manifest contains 3,392 training, 726 validation, and 728 held-out test images with paired eyes kept together. Validation-only selection restored epoch 34; the one-way held-out result achieved Accuracy 0.907967 and macro F1 0.907904, meeting the ≥0.90 image-classification target. This is not a video-level drowsiness-performance claim.

## Phase 4 — Real-Time Drowsiness Alert

**Milestone outcome**: configurable sustained-closure and PERCLOS decisions, visible status, controlled audio warning, and tested live-flow behavior.

- [X] T-091 [Parent: Phase 4] Decompose T-015–T-018 into independently reviewable decision, presentation, audio, integration, asset, and manual-verification tasks in `specs/001-drowsyalert/tasks.md`.

- [X] T-015 — Finalize and test configurable decision rules

- **Phase:** 4 — Real-Time Drowsiness Alert.
- **Priority:** P0.
- **Dependencies:** G2; T-008; approved thresholds/window from G0.
- **Requirements:** FR-007–FR-008, FR-012, FR-015; NFR-001, NFR-004, NFR-006.
- **Objective:** Implement and verify the PERCLOS/prolonged-closure baseline decision path (Method A), including normal, warning, and unknown states. Method B/C fusion and shared comparison configuration are completed later under T-021 after T-019 and T-020.
- **Implementation Steps:** Review `src/drowsyalert/pipeline/decision.py`, `src/drowsyalert/utils/config.py`, and `tests/test_temporal.py`. Reconcile Method A thresholds, warm-up/coverage, prolonged closure, status reasons, unknown behavior, and parameter validation with the approved protocol. Add boundary and invalid-input tests. Do not finalize B/C cue fusion here.
- **Expected Artifacts:** Decision/config changes; `tests/test_decision.py`; documented configuration fields.
- **Verification:** Tests cover below/at/above thresholds, short closure, prolonged closure, insufficient window coverage, and unknown observations; parameters are serialized per run.
- **Definition of Done:** Method A decisions are explainable from recorded evidence/settings and unknown cannot produce normal by default; B/C remain explicitly deferred to T-021.

### T-015 leaf tasks — Method A decision contract

- [X] T-092 [Parent: T-015] Add focused Method A tests for unknown eyes, warm-up/coverage, missing PERCLOS, below/at/above thresholds, short closure, prolonged closure, and non-finite evidence in `tests/test_decision.py`.
- [X] T-093 [Parent: T-015] Implement explicit `NORMAL`/`ALERT`/`UNKNOWN` Method A precedence and reason semantics in `src/drowsyalert/pipeline/decision.py` (depends on T-092).
- [X] T-094 [Parent: T-015] Verify decision threshold/window configuration validation and resolved-run serialization in `src/drowsyalert/utils/config.py` and focused tests (depends on T-093).
- [X] T-095 [Parent: T-015] Run focused decision/config tests and Ruff, then document Method A while keeping Method B/C fusion deferred to T-021 (depends on T-094).

- [ ] T-016 — Verify visible status and alert presentation

- **Phase:** 4 — Real-Time Drowsiness Alert.
- **Priority:** P1.
- **Dependencies:** T-015.
- **Requirements:** FR-012–FR-013, FR-015; NFR-008–NFR-009; RA-007.
- **Objective:** Present observation availability, current status, warning reason, and advisory limitation clearly.
- **Implementation Steps:** Review `src/drowsyalert/utils/overlay.py` and pipeline presentation. Ensure normal, warning, unknown, camera/input error, and warming-up/unavailable states are distinguishable. Include the research-prototype advisory message in visible UI and `README.md`.
- **Expected Artifacts:** Overlay and README updates; presentation-focused tests where separable; screenshots/examples only from non-personal fixtures.
- **Verification:** A reviewer can distinguish each state/reason in a controlled run; warning is not presented as guaranteed safety detection.
- **Definition of Done:** User can identify source/status/reason and stop/mute controls as required by approved UI scope.

### T-016 leaf tasks — Visible state and advisory presentation

- [ ] T-096 [Parent: T-016] Add presentation tests for normal, alert, unknown, warm-up, unavailable evidence, source identity, controls, and advisory wording in `tests/test_overlay.py` (depends on T-095).
- [ ] T-097 [Parent: T-016] Refactor overlay text generation into a testable state summary and render distinct status/reason/advisory lines in `src/drowsyalert/utils/overlay.py` (depends on T-096).
- [ ] T-098 [Parent: T-016] Update `README.md` with status meanings, stop/mute controls, webcam privacy, and research-prototype limitations (depends on T-097).
- [ ] T-099 [Parent: T-016] Run focused overlay tests and Ruff, then record presentation verification (depends on T-098).

- [ ] T-017 — Verify audio warning and repeat control

- **Phase:** 4 — Real-Time Drowsiness Alert.
- **Priority:** P1.
- **Dependencies:** T-015.
- **Requirements:** FR-014, FR-020; NFR-004, NFR-008–NFR-009.
- **Objective:** Emit a live warning when required and bound repeat playback.
- **Implementation Steps:** Review `src/drowsyalert/pipeline/alerts.py`, bundled sound asset, configuration, and alert tests. Verify asynchronous/nonblocking behavior, cooldown/repeat transitions, recovery/stop, missing sound, mute, and audio state in result metadata.
- **Expected Artifacts:** Alert implementation/configuration; `tests/test_alerts_config.py` or focused alert tests; user guidance.
- **Verification:** Injected alert-state sequences prove first alert, sustained warning, cooldown, recovery, and mute behavior; manual sound check is marked hardware-dependent.
- **Definition of Done:** Repeated alerts follow approved repeat policy and audio failure does not corrupt detection status.

### T-017 leaf tasks — Bounded and observable audio behavior

- [ ] T-100 [Parent: T-017] Add injected audio tests for first alert, sustained alert before/at cooldown, recovery stop, re-alert, mute, missing sound, playback failure, and close in `tests/test_alerts.py` (depends on T-095).
- [ ] T-101 [Parent: T-017] Implement explicit audio availability/enabled/active/playback-result state with nonblocking cooldown behavior in `src/drowsyalert/pipeline/alerts.py` (depends on T-100).
- [ ] T-102 [Parent: T-017] Record audio enabled/available/play count/failure metadata in pipeline results and document the repeat policy (depends on T-101).
- [ ] T-103 [Parent: T-017] Run focused alert tests and Ruff; record that actual speaker output remains a manual hardware check (depends on T-102).

- [ ] T-018 — Verify the complete live webcam alert flow

- **Phase:** 4 — Real-Time Drowsiness Alert.
- **Priority:** P0.
- **Dependencies:** T-005–T-009, T-015–T-017; T-014 if CNN is selected for the demo.
- **Requirements:** FR-001, FR-003–FR-008, FR-012–FR-017, FR-020; NFR-004, NFR-008–NFR-009; RA-006–RA-007.
- **Objective:** Demonstrate end-to-end local operation and failure handling on the declared environment.
- **Implementation Steps:** Add/complete integration checks in `tests/test_pipeline.py`; run automated replay path; conduct manual webcam demonstration on available hardware; record model/assets/configuration, unknown-state behavior, warning reason, stop/mute, and camera loss.
- **Expected Artifacts:** Integration tests; `docs/verification.md`; non-personal demo evidence.
- **Verification:** Automated tests pass; manual checklist records actual hardware and outcome; no staged or simulated outcome is described as a real webcam result.
- **Definition of Done:** G4 reviewer observes normal, warning, unavailable, audible, and stop behavior or explicitly records unavailable hardware as a blocker.

### T-018 leaf tasks — Complete local live flow

- [ ] T-104 [Parent: T-018] Extend fake live/replay integration tests across normal, alert, unknown, mute, cleanup, logging, and camera-read failure in `tests/test_pipeline.py` (depends on T-095, T-099, T-103).
- [ ] T-105 [Parent: T-018] Verify CLI exit behavior, resolved configuration, backend/source identity, checkpoint identity, and audio metadata in automated runs (depends on T-104).
- [ ] T-106 [Parent: T-018] Add a concise real-webcam/audio acceptance checklist and evidence template to `docs/verification.md` (depends on T-105).
- [ ] T-107 [Parent: T-018] Acquire or verify the configured MediaPipe face model asset and record its provenance/hash without committing it (depends on T-106).
- [ ] T-108 [Parent: Phase 4] Run the full automated suite and Ruff, preserve generated/private boundaries, and record G4 status plus any physical webcam/speaker blocker (depends on T-104–T-107).

### Phase 4 acceptance gate

G4 passes when decision, UI, and audio behaviors are independently tested and the live flow passes or carries a clearly identified hardware blocker. CNN accuracy and alert effectiveness remain separate claims.

## Phase 5 — Additional Research Features

**Milestone outcome**: optional indicators are valid/unknown-aware, and A/B/C share controlled baseline settings and traceable method identities.

- [ ] T-019 — Implement and test yawning feature extraction (Coding)

- **Phase:** 5 — Additional Research Features.
- **Priority:** P1.
- **Dependencies:** G2; T-006, T-008; approved yawning definition from G0.
- **Requirements:** FR-009, FR-011–FR-012, FR-015; NFR-004, NFR-006.
- **Objective:** Detect a temporally defined yawn event from valid mouth observations for Method B.
- **Implementation Steps:** Review `src/drowsyalert/features/geometry.py`, `src/drowsyalert/features/extra.py`, and detection tests. Implement/reconcile valid mouth geometry, event duration/reset, event deduplication, window count, and unknown handling according to the approved definition. Add synthetic boundary/gap tests.
- **Expected Artifacts:** Feature implementation; `tests/test_detection.py` or focused `test_yawn.py`; configuration docs.
- **Verification:** Tests cover below/at/above definition boundary, one event per continuous interval, tracking gap, invalid landmarks, and rolling count expiration.
- **Definition of Done:** Yawn feature returns reproducible event/time evidence and never invents events from invalid mouth data.

- [ ] T-020 — Implement and test head-pose feature extraction (Coding)

- **Phase:** 5 — Additional Research Features.
- **Priority:** P1.
- **Dependencies:** G2; T-006, T-008; approved pose reference/threshold from G0.
- **Requirements:** FR-010–FR-012, FR-015; NFR-004, NFR-006.
- **Objective:** Estimate a documented head-pose indicator for Method C.
- **Implementation Steps:** Review `src/drowsyalert/features/extra.py` and existing pose tests. Implement/reconcile pose validity, reference handling, angle sign convention, sustained-duration behavior, reset on gaps, and unknown output against approved plan. Do not assume user-neutral pose or calibration rule without approval.
- **Expected Artifacts:** Feature implementation; focused pose tests in `tests/test_detection.py` or `test_head_pose.py`; decision-rule documentation.
- **Verification:** Deterministic projected/synthetic cases validate sign and threshold behavior; invalid landmarks/pose and tracking gaps reset or mark unknown as specified.
- **Definition of Done:** Pose evidence is reproducible, interpretable, and recorded with its reference/threshold.

- [ ] T-021 — Normalize method A/B/C configuration and evidence provenance

- **Phase:** 5 — Additional Research Features.
- **Priority:** P0.
- **Dependencies:** T-015, T-019, T-020; frozen common PERCLOS protocol from G0.
- **Requirements:** FR-011–FR-012, FR-018–FR-019; NFR-006; RA-001–RA-003.
- **Objective:** Ensure A/B/C differ only by the named auxiliary feature and approved method-specific rule.
- **Implementation Steps:** Review `src/drowsyalert/pipeline/decision.py`, `src/drowsyalert/pipeline/realtime.py`, `src/drowsyalert/experiments/`, and configuration. Define method IDs, common settings, feature settings, eye-state source, and per-run evidence fields; test that A does not consume auxiliary signals and B/C consume only their named signal.
- **Expected Artifacts:** Method configuration/decision updates; `tests/test_experiments.py`; documented configuration matrix.
- **Verification:** Same input/configuration produces method-labelled records; common PERCLOS settings match across methods; any difference is explicit and justified.
- **Definition of Done:** A/B/C are selectable and traceable without hidden parameter drift.

- [ ] T-022 — Add experiment execution and result-recording contract

- **Phase:** 5 — Additional Research Features.
- **Priority:** P0.
- **Dependencies:** T-013, T-018, T-021.
- **Requirements:** FR-018–FR-020; NFR-005–NFR-007; RA-001–RA-005.
- **Objective:** Record enough inputs and outputs to reproduce and audit each experiment.
- **Implementation Steps:** Review `src/drowsyalert/experiments/`, CSV logging in `src/drowsyalert/pipeline/realtime.py`, and config. Add/verify run identity, dataset/split, source timestamps, method, eye-state source, settings/thresholds, seed/model identity, audio state, evidence/unknown coverage, outputs, and environment details according to approved plan. Keep outputs/private data paths ignored.
- **Expected Artifacts:** Experiment record/export module; `tests/test_experiments.py`; schema/documentation in `docs/`.
- **Verification:** Schema test confirms required provenance fields; round-trip/export has stable column names and does not include raw frame data by default.
- **Definition of Done:** A researcher can map every reported value to a run and its declared inputs/configuration.

### Phase 5 acceptance gate

G5 passes when B and C indicators are tested, method A/B/C behavior is isolated, common settings are verifiable, and run records capture required provenance. No comparative conclusion is permitted before held-out evaluation.

## Phase 6 — Experimental Evaluation

**Milestone outcome**: lawful, consent-aware and temporally labelled evaluation data; frozen protocol; reproducible A/B/C results, latency/error analysis, and transparent limitations.

- [ ] T-023 — Approve temporal ground truth and evaluation protocol (Research)

- **Phase:** 6 — Experimental Evaluation.
- **Priority:** P0.
- **Dependencies:** G0; T-021, T-022.
- **Requirements:** DR-003, DR-005–DR-008; NFR-006–NFR-007; RA-001–RA-005.
- **Objective:** Fix event labels, event matching, onset, false-alarm denominator, and split protocol before test scoring.
- **Implementation Steps:** Document the reference-label unit, onset/offset rules, any independent annotation/adjudication procedure, event matching tolerance, per-video/time denominator, treatment of unknown coverage/overlap, and subject/session split. Obtain supervisor approval and participant/ethics guidance for volunteer work.
- **Expected Artifacts:** `docs/evaluation-protocol.md`; versioned protocol approval record.
- **Verification:** Reviewer confirms all three methods use same eligible test videos/labels/timestamps and threshold selection is restricted to training/validation.
- **Definition of Done:** Protocol frozen and dated before final test evaluation; unresolved annotation or ethics decisions block affected study claims.

- [ ] T-024 — Acquire/prepare annotated evaluation videos and condition labels (Research/Data)

- **Phase:** 6 — Experimental Evaluation.
- **Priority:** P0.
- **Dependencies:** T-001, T-010, T-023.
- **Requirements:** DR-003–DR-008; NFR-006–NFR-007; RA-003, RA-005.
- **Objective:** Obtain lawful, consented where applicable, temporally labelled videos for alert evaluation.
- **Implementation Steps:** Review the public dataset candidate and/or collect volunteer recordings only under approved consent and institution guidance. Record source/license, session/subject IDs, capture conditions, labels and annotation provenance. Annotate glasses, lighting, and head movement only when observed. Keep private raw videos outside Git and use approved access/retention controls.
- **Expected Artifacts:** `data/README.md`, restricted dataset location and versioned label/split manifests, consent/provenance records stored per approved policy.
- **Verification:** Dataset audit confirms authorization, label coverage, split separation, and no private files in Git; report dataset/sample counts only after actual acquisition.
- **Definition of Done:** Evaluation corpus is available and approved, or task is marked blocked with the specific data/permission gap; no data availability is presumed.

- [ ] T-025 — Implement and unit-test temporal/video evaluation metrics

- **Phase:** 6 — Experimental Evaluation.
- **Priority:** P1.
- **Dependencies:** T-023; T-022.
- **Requirements:** FR-019; NFR-001, NFR-006; RA-002–RA-004.
- **Objective:** Compute distinct eye-classification and video/event alert metrics using declared definitions.
- **Implementation Steps:** In `src/drowsyalert/experiments/`, implement or reconcile metric calculations for eye Accuracy/confusion matrix/class metrics, event/interval detection scores, false alarms per declared time unit, misses, observation coverage/loss, and grouped conditions. Add known-count fixtures and explicit handling of empty/unknown cases.
- **Expected Artifacts:** Metrics module; `tests/test_experiment_metrics.py`; metric definition documentation.
- **Verification:** Hand-calculated fixtures match expected values; tests ensure image classification counts are not reused as temporal alert counts.
- **Definition of Done:** Metrics and denominators are documented, tested, and traceable to protocol.

- [ ] T-026 — Measure alert latency and failure scenarios

- **Phase:** 6 — Experimental Evaluation.
- **Priority:** P1.
- **Dependencies:** T-023–T-025.
- **Requirements:** FR-017–FR-019; NFR-002, NFR-004, NFR-006; RA-003.
- **Objective:** Measure onset-to-alert delay and characterize false alarms, misses, and observation interruptions.
- **Implementation Steps:** Add latency calculation to `src/drowsyalert/experiments/` using approved reference onset and alert timestamps. Include missed events as misses, report latency distribution only for detected events plus miss count, and record input/processing conditions. Evaluate no face, tracking loss, glasses, low lighting, head movement, camera interruption, and uncertain predictions where examples exist.
- **Expected Artifacts:** Latency/failure evaluator; `tests/test_alert_latency.py`; result tables/plots under ignored outputs.
- **Verification:** Synthetic timing cases prove latency and miss treatment; real data claims cite actual event counts and condition coverage.
- **Definition of Done:** Latency, false alarms, misses, and observation loss are separate reported measures; absent conditions are identified as unavailable.

- [ ] T-027 — Run the controlled A/B/C evaluation and compare results (Research)

- **Phase:** 6 — Experimental Evaluation.
- **Priority:** P0.
- **Dependencies:** G5; T-023–T-026; final held-out eye-classifier evaluation T-013.
- **Requirements:** FR-018–FR-019; NFR-001–NFR-003, NFR-006; RA-001–RA-004.
- **Objective:** Answer the primary research question using comparable held-out results.
- **Implementation Steps:** Freeze configurations and thresholds selected on validation. Run A, B, and C over identical eligible test videos/labels, using landmark-derived PERCLOS as the primary comparison. If data and design permit, run the secondary CNN-derived PERCLOS comparison as a separately labelled experiment. Record actual runtime hardware and results; never tune against test outcomes.
- **Expected Artifacts:** Machine-readable run records and comparison tables in ignored `outputs/results/`; evaluation summary in `docs/`.
- **Verification:** Audit run IDs/configurations/test membership; confirm common test set and no test-informed tuning; recalculate summary from raw run records.
- **Definition of Done:** Complete comparable metrics or a documented blocked/incomplete result; no fabricated values or unsupported claim that an Accuracy goal was met.

### Phase 6 acceptance gate

G6 passes when evaluation protocol and corpus are approved, metrics are tested, all feasible methods are run on common held-out data, actual latency/error/coverage/condition results are recorded, and limitations are explicit. Missing lawful data or labels are blockers, not grounds to substitute invented results.

## Phase 7 — Final Validation and Delivery

**Milestone outcome**: regression confidence, traceable requirements evidence, reproducible instructions, and ready demonstration/report artifacts.

- [ ] T-028 — Run integration and regression suite

- **Phase:** 7 — Final Validation and Delivery.
- **Priority:** P0.
- **Dependencies:** G2–G6.
- **Requirements:** FR-001–FR-020; NFR-004–NFR-009; RA-006–RA-007.
- **Objective:** Verify the approved implementation as a whole and catch regressions across input, inference, temporal rules, alerts, and experiments.
- **Implementation Steps:** Run the documented lint/test commands from the repository root; execute deterministic recorded-video integration scenarios; conduct available manual webcam/audio checks; record OS/Python/dependency/model/input details and any hardware-dependent skips.
- **Expected Artifacts:** Updated `docs/verification.md`; CI/test output or reviewed run log.
- **Verification:** Automated suite passes; manual checks are labelled with real environment and no skipped check is claimed as passed.
- **Definition of Done:** All critical failures fixed or documented with owner/blocking impact; no unrelated source changes.

- [ ] T-029 — Complete requirement-to-evidence traceability

- **Phase:** 7 — Final Validation and Delivery.
- **Priority:** P0.
- **Dependencies:** T-028; T-027.
- **Requirements:** All FR/DR/NFR and RA items; Constitution Principle VII.
- **Objective:** Show which requirements are implemented, verified, measured, blocked, or deferred.
- **Implementation Steps:** Create/update `docs/requirement-coverage.md` mapping every FR, DR, NFR, RA, and G0 decision to implementation path, test/evidence, and status. Distinguish code existence from verified behavior and goals from measured results.
- **Expected Artifacts:** `docs/requirement-coverage.md`.
- **Verification:** Every mandatory requirement has a status and evidence reference or explicit blocker; A/B/C and ≥0.90 target status are not implied by scaffold code.
- **Definition of Done:** Reviewer can trace requirements to tests, records, or documented open limitations.

- [ ] T-030 — Finalize reproducible setup and run instructions

- **Phase:** 7 — Final Validation and Delivery.
- **Priority:** P1.
- **Dependencies:** T-028, T-029.
- **Requirements:** NFR-005–NFR-008; RA-005–RA-007.
- **Objective:** Enable another researcher to install, prepare permitted data, run webcam/video demo, and reproduce experiments.
- **Implementation Steps:** Update `README.md`, `docs/`, and data/model README files with approved environment setup, source/license steps, private-data placement, training/evaluation/demo commands, configuration, expected outputs, known limitations, and advisory-only messaging. Avoid bundling restricted raw data.
- **Expected Artifacts:** Updated `README.md`, `data/README.md`, `models/README.md`, and focused documentation.
- **Verification:** Follow the documented workflow in a clean environment or record exact environmental blocker; commands/paths match actual entry points and outputs.
- **Definition of Done:** Fresh researcher can follow instructions without hidden data paths or unrecorded thresholds.

- [ ] T-031 — Prepare figures, result exports, and delivery evidence

- **Phase:** 7 — Final Validation and Delivery.
- **Priority:** P1.
- **Dependencies:** T-027–T-030.
- **Requirements:** FR-019; NFR-006; RA-001–RA-007.
- **Objective:** Produce reviewable result tables/figures and demonstration evidence for the research report and slides.
- **Implementation Steps:** Generate figures/tables from saved results (not manually retyped values), verify method labels and units, prepare non-personal representative warning examples, inventory distributable source/checkpoint/configuration artifacts, and record any license/consent restrictions. Track the 35–45 page report and slides as delivery handoff inputs; do not fabricate missing results.
- **Expected Artifacts:** Reproducible export scripts, `outputs/results/` exports (ignored where appropriate), figure files, and delivery checklist.
- **Verification:** Re-generated tables match run records; private media and unauthorized artifacts are absent from Git/public delivery.
- **Definition of Done:** Evidence package supports final report/presentation or clearly identifies missing prerequisites/results.

### Phase 7 acceptance gate

G7 passes when regression checks, evidence traceability, reproducible setup instructions, and result exports are reviewed. Final report/slides may state only results supported by approved data and saved experiment evidence.

## Dependency graph and critical path

```text
G0/T-001 ─┬─ T-002 ─ T-003 ─ T-004 ─ G1
          │                            │
          └────────────────────────────┴─ T-005 ─ T-006 ─ T-007 ─ T-008 ─ T-009 ─ G2
                                                  │               │
G1 ─ T-010 ─ T-011 ─ T-012 ─ T-013 ─ T-014 ─────┘               │
G2 ─ T-015 ─┬─ T-016 ─┐                                         │
             └─ T-017 ─┴─ T-018 ─ G4                             │
G2 ─ T-019 ─┐                                                     │
G2 ─ T-020 ─┴─ T-021 ─ T-022 ─ G5                               │
G1 + G5 ─ T-023 ─ T-024 ─ T-025 ─ T-026 ─ T-027 ─ G6 ─ T-028 ─ T-029 ─ T-030/T-031 ─ G7
```

**Critical path**: G0 and approved method/data protocol → G1 → landmark/video baseline (T-005–T-009) → required method/configuration and reproducible records (T-019–T-023) → lawful temporally labelled evaluation corpus (T-024) → tested metrics/latency (T-025–T-026) → common held-out A/B/C run (T-027) → final validation/delivery (T-028–T-031). CNN classification (T-010–T-014) is required for the instructor's classifier objective and can proceed alongside the baseline after G1, but does not replace landmark-derived PERCLOS on the primary research path.

## Safe parallel work

Parallel work is allowed only after listed dependencies are complete and when separate files/data ownership avoids conflicts.

- After T-001, T-002 and read-only repository inventory can proceed independently.
- After G1, T-005 input work and T-010 dataset/license research may proceed in parallel; keep raw data private.
- After T-006, T-007 landmark eye-state work can proceed while T-011 dataset-loader work proceeds after T-010.
- After T-015, T-016 visible presentation and T-017 audio work can proceed in parallel if changes remain in their separate modules/tests.
- After G2, T-019 yawning and T-020 pose can proceed in parallel with separate feature/test files.
- After T-023, evaluation-metric implementation and approved video preparation may proceed in parallel, but test execution waits for both data and evaluator readiness.
- T-028 onward is sequential for release evidence; T-030 documentation and T-031 exports may be prepared in parallel after their dependencies, with one owner for shared README/result files.

## Milestone verification gates

| Gate | Pass condition | Human review |
|---|---|---|
| G0 — authority/design | SRS approved; constitution ratified; source DOCX revision confirmed; completed plan approved; dataset/ground-truth/threshold/consent decisions resolved or assigned as explicit blockers. | Project owner/supervisor |
| G1 — foundation | Environment/dependencies/data boundaries/config/test conventions are recorded and safe. | Technical lead |
| G2 — landmark baseline | Webcam/video and landmark path works; timestamp PERCLOS and unknown/gap behavior pass automated tests and replay check. | Technical lead/researcher |
| G3 — CNN classifier | Permitted dataset/splits, tested training/inference, actual held-out classification metrics and provenance exist. | Research reviewer |
| G4 — live alert | Decision/UI/audio and end-to-end live flow are verified, with hardware limitations recorded. | Demonstration reviewer |
| G5 — A/B/C readiness | Auxiliary features, method isolation, common settings, and experiment record schema pass tests. | Research reviewer |
| G6 — research results | Common test protocol/data, metrics/latency/error/condition results and limitations are recorded. | Supervisor/research reviewer |
| G7 — delivery | Regression, traceability, reproducibility guidance, evidence exports, and report/slide inputs are reviewed. | Project owner/supervisor |

## First executable task and recommended MVP milestone

**First completed implementation task**: **T-002 — Audit and record the current environment**. Phase 1 authority, dependency/layout, configuration, test, privacy, and recovery conventions are recorded. The next implementation milestone is **Phase 2, G2 landmark/PERCLOS baseline**. A live alert demo is not accepted as the research MVP until T-015–T-018 are complete.

## Task-readiness review

- **Traceability**: Tasks link to SRS FR, DR, NFR, RA, and open questions; existing modules are reviewed before extensions to avoid duplicate implementation.
- **Verification**: Automated tests are scheduled alongside each behavior, beginning in Phase 2; regression is repeated in Phase 7.
- **Data/research separation**: Dataset review, volunteer consent, labeling, protocol approval, and comparative evaluation are explicitly research/data tasks, separate from coding.
- **No fabricated evidence**: Dataset availability, target attainment, and experimental outcomes remain unknown until measured; blocked paths are recorded as blocked.
- **Current readiness**: G1, G2, and G3 passed. Phase 3 produced an ignored local CEW checkpoint and held-out classification record with full hashes and provenance. Phase 4 decision and alert work may proceed; later video-level research gates remain separate.

## Format and traceability summary

- Task list currently contains **31 parent work packages plus 77 leaf tasks** (108 numbered items). Create leaf tasks for the active work package before implementation; the leaf count will grow as approved work is decomposed.
- By phase: Phase 1 **4**; Phase 2 **5**; Phase 3 **5**; Phase 4 **4**; Phase 5 **4**; Phase 6 **5**; Phase 7 **4**.
- Research/data tasks: T-001, T-010, T-023, T-024, T-027; implementation/environment tasks are otherwise separated as labelled.
- T-001–T-031 are parent work packages, not the intended smallest execution units. Add focused leaf tasks with stable IDs before starting each parent; avoid speculative leaf tasks where dataset/protocol approvals may change the work.
- Every leaf task must identify its parent, phase, dependencies, affected paths, verification, and recovery branch. Keep a leaf to one behavior or artifact whenever practical.
- All task items use stable IDs and checklist syntax; completed work is checked only after its recorded verification. Parallel opportunities are explicitly bounded above; the default AI-assisted workflow is one leaf task at a time.
