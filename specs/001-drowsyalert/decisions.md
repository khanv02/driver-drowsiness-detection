# DrowsyAlert Decision and Approval Record

**Feature:** `001-drowsyalert`
**Prepared:** 2026-10-26
**Gate:** G0 — authority, design, research protocol, and safe development baseline

This record separates decisions that require the project owner or supervisor from technical facts already established. A pending item remains a blocker for the work named in its **Blocking effect** column. Recording a blocker does not count as approving the underlying decision.

## Authority and design approvals

| ID | Decision required | Current evidence | Owner | Status | Blocking effect |
|---|---|---|---|---|---|
| G0-01 | Approve `spec.md` as the requirements baseline | The SRS covers FR-001–FR-020, NFR-001–NFR-009, DR-001–DR-008, acceptance checks, edge cases, and open questions. | Project owner | Approved 2026-10-26 | Baseline established; later changes require traceable review |
| G0-02 | Adopt Constitution v1.0.0 and record its ratification date | Seven principles and governance are present in `.specify/memory/constitution.md`. | Project owner | Adopted 2026-10-26 | Constitution is binding for subsequent work |
| G0-03 | Approve `plan.md` as the implementation and experiment design baseline | The plan defines the Python stack, module boundaries, incremental milestones, testing strategy, A/B/C comparison, and branch workflow. | Project owner | Approved 2026-10-26 | Implementation may follow the plan subject to task prerequisites |
| G0-04 | Confirm the official Project 12 source revision | The repository contains `docs/PhieuMoTaDeTai_30DeTai_ThiGiacMayTinh_NCKH.docx`, 86,788 bytes, SHA-256 `DBFF7BBDD9010F97EB0A2A7D8EAA68AAD5BAC0DCB89C646E5486AEED9EF593F2`. The requested filename ending in `(2).docx` is absent. | Project owner | Available unsuffixed file accepted 2026-10-26 | Reconfirm only if a different official revision is later supplied |

## Research and data decisions

| ID | Decision required | Proposed handling already documented | Owner | Status | Blocking effect |
|---|---|---|---|---|---|
| G0-05 | Select lawful eye-image dataset/version and approve its license and label mapping | Evaluate candidates under T-010; record source, version/retrieval date, terms, labels, groups, hashes, and split limitations. | Research lead/supervisor | Accepted owned blocker: T-010 | Blocks CNN data preparation and training |
| G0-06 | Select or create temporally annotated drowsiness videos | Require event onset/end or another declared time-localized ground truth; image-only labels are insufficient. | Research lead/supervisor | Accepted owned blocker: T-023/T-024 | Blocks latency and A/B/C event evaluation |
| G0-07 | Define the system-level Accuracy unit and event matching rule | Define event, interval, or labelled-window unit plus tolerance/overlap and one-to-one matching before held-out evaluation. | Research lead/supervisor | Accepted owned blocker: T-023 | Blocks final system scoring and comparison |
| G0-08 | Approve PERCLOS, coverage, gap, closure, cooldown, yawn, and pose threshold-selection protocol | Select with training/validation data or a documented protocol; freeze before test and serialize resolved values. | Research lead/supervisor | Accepted owned blocker: T-023; implementation tasks consume approved values | Blocks final threshold behavior and test evaluation |
| G0-09 | Approve volunteer consent and data governance before any collection | Record purpose, consent, withdrawal, access, retention/deletion, publication, and institutional/supervisor guidance. | Supervisor/data steward | Accepted owned blocker: T-024 | Blocks volunteer recording; public-data review may continue |

## Development baseline and recovery

| ID | Decision required | Current evidence | Owner | Status | Blocking effect |
|---|---|---|---|---|---|
| G0-10 | Preserve an approved clean Git baseline before feature branching | The root-layout migration was reviewed for private/generated paths and committed on `checkpoint/root-layout` at `3f717de`. The original `master` branch remains unchanged. | Project owner | Completed 2026-10-26 | Provides the recoverable starting checkpoint |
| G0-11 | Use the documented recovery workflow | `feature/001-drowsyalert` was created from checkpoint `3f717de`; leaf work uses `task/T-###-slug` branches and is recovered by abandoning an unmerged branch or reverting its commit. | Project owner | Active 2026-10-26 | Governs subsequent implementation |

## Approval statement

G0 passes only when G0-01 through G0-04 and G0-10/G0-11 are explicitly approved, and G0-05 through G0-09 are either resolved or accepted as owned blockers with the stated effects. Approval must not imply that datasets, trained models, performance targets, or experiment results already exist.

Record approval here or in an equivalent supervisor review record:

| Reviewer | Role | Decision/date | Notes |
|---|---|---|---|
| Chat user | Project owner | Approved 2026-10-26 | Directed work to proceed; G0-05–G0-09 remain owned blockers. Root-layout checkpoint `3f717de` preserves the approved starting state. |

## Phase 6 protocol approval

On 2026-10-26, the project owner approved temporal evaluation protocol
`drowsyalert-video-eval-v1`: NITYMED HDTV720 is the public-data path; independently
reviewed microsleep intervals are the primary endpoint and yawns are secondary; matching
uses the earliest unmatched alert in the inclusive -1.0/+2.0-second window; false alarms
use valid observed hours; signed latency excludes misses while misses remain FN; system
Accuracy uses 1-second/50-percent bins with UNKNOWN retained as incorrect; thresholds
are validation-selected and frozen before test; subject-disjoint grouping is required
for final claims; and volunteer collection is not authorized. Missing participant
mapping or temporal annotations blocks final scoring but may support an explicitly
labelled, non-claim pilot.
