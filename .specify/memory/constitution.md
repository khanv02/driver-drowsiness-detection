<!--
Sync Impact Report
Version change: no ratified constitution → 1.0.0 (initial constitution)
Modified principles: none; this establishes the project's first binding principles.
Added sections: seven core principles, research and privacy constraints, development workflow, governance.
Removed sections: none.
Follow-up TODOs: none.
-->
# DrowsyAlert Constitution

## Core Principles

### I. Research-First Development
All specifications and implementation work MUST advance the Project #12 research objectives. The central question MUST remain whether PERCLOS computed from 2D facial landmarks is sufficient to detect drowsiness, and whether adding yawning or head-pose signals improves detection. Evaluation MUST compare the three required methods: PERCLOS alone, PERCLOS with yawning, and PERCLOS with head pose. The methods MUST use the same eligible evaluation data, labels, and protocol. Research questions and hypotheses MUST be stated separately from measured findings; proposed targets MUST NOT be reported as achieved results. This keeps engineering choices accountable to the study.

### II. Simplicity and Maintainability
Code and design MUST favor the smallest understandable solution that meets a documented requirement. Python modules MUST have clear responsibilities and avoid duplicated logic. SOLID abstractions are appropriate only when they reduce coupling or make behavior easier to test. New dependencies and abstractions MUST have a stated need; speculative features and unrelated changes MUST be excluded. This keeps the project maintainable within its undergraduate research scope.

### III. Scientific Reproducibility
Every reported experiment MUST record dataset identity and version, provenance and license, preprocessing, labels, subject/session split, model and configuration, decision thresholds, random seeds, and evaluation procedure. Training, validation, and test data MUST be separated to prevent subject, session, or near-duplicate frame leakage. Thresholds and model selection MUST use training/validation data; final test results MUST be computed only under the declared protocol. Comparisons MUST share the same test examples, labels, and metrics. Results MUST be traceable to saved measurements or artifacts; fabricated, inferred, or target-only results MUST NOT be presented as experimental evidence.

### IV. Testability and Reliability
Computer-vision input handling, eye-state inference, temporal feature calculation, alert decisions, and presentation MUST remain separable enough to exercise core behavior independently. Core algorithms and alert transitions MUST have automated tests for normal, boundary, and invalid inputs. Missing faces, invalid frames, camera failures, low-confidence predictions, and interrupted timestamps MUST be represented and handled explicitly. Missing observations MUST remain unknown and MUST NOT be silently counted as open or closed eyes. Alert behavior MUST not turn uncertainty into an unsupported positive or negative classification.

### V. Incremental Development
Work MUST establish and verify a minimal end-to-end baseline before adding optional signals or presentation complexity. Each phase MUST have a stated outcome and a practical verification method. Changes MUST remain scoped to the approved specification and avoid regressions in working behavior. Functional correctness and reliable measurements take precedence over visual polish. This makes progress reviewable and helps isolate research and implementation failures.

### VI. Privacy and Responsible Use
Webcam frames and recordings MUST be processed locally by default. Any collection or publication of participant recordings MUST require informed consent and an appropriate documented purpose. Private recordings, identifiers, and other sensitive data MUST NOT be committed to version control. Dataset use MUST respect its license and applicable consent conditions. User-facing documentation and demonstrations MUST identify DrowsyAlert as a research prototype, not a certified road-safety system or substitute for official safety measures.

### VII. Documentation and Traceability
Project documentation, specifications, design decisions, and user-facing terminology MUST be maintained consistently in English. Each mandatory requirement MUST be traceable to relevant design, implementation work, and verification evidence; optional enhancements MUST be labeled as optional. Assumptions, limitations, unresolved questions, dataset decisions, and deviations from the official research brief MUST be recorded. Documentation MUST distinguish current implementation status from intended behavior and measured outcomes.

## Research and Data Constraints

The instructor's official Project #12 brief is authoritative for required scope and deliverables. The project description supplies context and proposed elaborations; existing code describes implementation status and does not establish requirements. The official brief specifies a public Kaggle drowsiness dataset, consent-based volunteer trials, pretrained face/eye-region detection, CNN open/closed eye classification, a webcam alert demo, eye-classification Accuracy target of at least 0.90, alert-latency measurement, and a 35–45 page report with slides. These are targets and deliverables, not evidence of achieved performance.

The PERCLOS-from-2D-landmarks question and the three required comparison methods in Principle I govern the research comparison. Any ambiguity about how those methods relate to the official CNN eye classifier MUST be resolved in the feature specification before the experiment design is fixed. Dataset choice, availability, and suitability MUST be documented; no particular Kaggle dataset version or URL is established by the brief. Evaluation MUST report eye-classification quality separately from video-level drowsiness detection and alert latency. Additional metrics may supplement but MUST NOT obscure required measurements.

## Development Workflow

Every SPEC, PLAN, TASKS, and IMPLEMENT artifact MUST comply with this constitution and preserve traceability to the official brief. A specification MUST identify user-visible behavior, research requirements, data and privacy constraints, assumptions, and unresolved decisions. A plan MUST explain a proportionate design without prematurely adding dependencies or scope. Tasks MUST be independently reviewable and verifiable. Implementation MUST add or update tests for core algorithmic behavior and report the verification performed; unavailable hardware or data MUST be identified as a limitation rather than simulated as a successful result.

Constitution compliance is reviewed when artifacts are created or materially changed and before research results are accepted. Any proposed deviation MUST identify the affected principle, reason, impact on validity or safety, and a compensating measure; the deviation requires an explicit constitution amendment before it becomes governing practice.

## Governance

This constitution governs all subsequent SPEC, PLAN, TASKS, and IMPLEMENT work and takes precedence over conflicting project guidance, except that the official instructor requirements remain authoritative for research scope and deliverables. Amendments MUST be made in this file, include a rationale and impact review, update the version and amendment date, and be checked for consistency with active specifications and plans. Initial adoption records the date on which the project team ratifies this document; that date is currently unknown and must be filled in at adoption.

Versioning follows semantic versioning: MAJOR for backward-incompatible principle changes or removals, MINOR for new principles or materially expanded governance, and PATCH for clarifications and non-semantic edits. Reviewers MUST check requirement traceability, scientific validity, privacy, test evidence, and documented limitations. Complexity or deviations MUST be justified in the relevant artifact. No later SDD phase is implied by adopting this constitution.

**Version**: 1.0.0 | **Ratified**: 2026-10-26 | **Last Amended**: 2026-10-26
