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
| G0-05 | Select lawful eye-image dataset/version and approve its license and label mapping | CEW selected; T-075 verified the owner-provided extraction, local identity/counts, readable images, and label mapping. | Research lead/supervisor | Resolved under T-010/T-075 | CNN training and held-out eye-image evaluation completed under T-012/T-013 |
| G0-06 | Select or create temporally annotated drowsiness videos | NITYMED HDTV720 selected; Protocol v1.1 approved a clip-disjoint 38-clip study with disclosed participant-mapping limitation. T-139 final annotation/manifest validation remains open. | Research lead/supervisor | Source/protocol approved; evidence pending | Blocks final video-level scoring until annotations are validated |
| G0-07 | Define the system-level Accuracy unit and event matching rule | Protocol v1.1 defines one-second bins with 50-percent overlap, UNKNOWN incorrect in primary Accuracy, and frozen one-to-one event matching. | Research lead/supervisor | Approved 2026-10-26 under T-126 | Scoring still waits for validated annotations and held-out review |
| G0-08 | Approve PERCLOS, coverage, gap, closure, cooldown, yawn, and pose threshold-selection protocol | Protocol v1.1 requires validation-only selection and freezing before test; numeric temporal thresholds remain to be selected under T-157/T-158. | Research lead/supervisor | Selection protocol approved; numeric values pending | Blocks held-out scoring until values and hashes are frozen |
| G0-09 | Approve volunteer consent and data governance before any collection | No volunteer collection is authorized or present in the current public-data study. Any later collection requires supervisor/institution guidance and informed consent. | Supervisor/data steward | Deferred; no collection authorized | Blocks volunteer recording only; public-data review may continue |

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

The project owner amended the protocol to `drowsyalert-video-eval-v1.1` on 2026-10-26.
The acquired NITYMED package lacks participant mapping, so the approved practical study
uses a deterministic balanced 38-clip split: all 19 microsleep clips plus 19 seeded
yawning clips; validation has 6+6, test has 13+13, and the four viewed pilot clips remain
in validation. Results must disclose possible same-participant leakage and cannot claim
subject-independent generalization. This replaces the earlier requirement that missing
subject mapping restrict all results to pilot-only status.
