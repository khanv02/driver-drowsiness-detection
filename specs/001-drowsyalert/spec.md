# Software Requirements Specification: DrowsyAlert

**Feature directory**: `specs/001-drowsyalert`
**Created**: 2026-10-26
**Status**: Approved requirements baseline
**Source**: User brief; Project 12 in `docs/PhieuMoTaDeTai_30DeTai_ThiGiacMayTinh_NCKH.docx`; `docs/de-tai-12-drowsyalert.md`; repository state reviewed 2026-10-26.

## 1. Problem Statement

Driver drowsiness can reduce a driver's ability to remain alert. DrowsyAlert is a student research system intended to observe one person in front of a local webcam, estimate eye state over time, identify sustained indicators associated with drowsiness, and provide an audible and visible warning. Its users are the student researchers evaluating the methods and a driver or demonstration participant using the local application. The research also has potential relevance to people working night shifts, but the required initial use case is a single person facing a webcam in a controlled, local-computing setting.

The project investigates whether landmark-derived PERCLOS is sufficient, and whether yawning or head pose adds useful evidence. It is a research and demonstration aid, not a certified driver-monitoring system, a medical diagnosis, or a substitute for safe driving practices or official vehicle safety measures. A webcam may fail to observe the eyes reliably because of lighting, glasses, occlusion, pose, camera placement, or tracking loss. Such conditions limit the validity of any estimate and must not be represented as confident normality.

## 2. Research Questions and Objectives

### Primary research question

> Can PERCLOS calculated from 2D facial landmarks accurately detect drowsiness, or should yawning and head-pose features be incorporated?

### Required method comparisons

- **Method A**: PERCLOS only.
- **Method B**: PERCLOS + yawning detection.
- **Method C**: PERCLOS + head-pose estimation.

All three methods must be evaluated on the same held-out video material, with the same event labels and comparable decision/alert evaluation rules. Results must identify the eye-state source used for PERCLOS.

### Role of eye-state methods

The instructor requires a CNN to classify eye-region images as open or closed and a temporal eye-closure measure. The research question specifically concerns PERCLOS calculated from 2D facial landmarks. Therefore landmark-derived eye state (for example, a geometric eye-openness measure) is the primary evidence path for answering that question. The CNN is a separately evaluated eye-image classifier and a required application capability; it may be evaluated as an alternative eye-state source for PERCLOS, but must not be silently treated as equivalent to the landmark method. The final report must state which source produced each result and, if available, compare both sources under the same temporal protocol.

Objectives are to deliver a local webcam demonstration with sustained-closure monitoring and audible warnings; evaluate open/closed eye classification; compare methods A, B, and C; measure video-level detection, alert latency, false alarms, missed detections, and observation coverage; and document limitations and reproducible results.

## 3. Scope

### Mandatory research requirements

1. Evaluate open/closed eye classification using public eye-state data and report test-set Accuracy, confusion matrix, and clearly defined class metrics.
2. Implement and evaluate landmark-derived, timestamp-based PERCLOS and sustained eye closure.
3. Compare A, B, and C on a common held-out, temporally annotated evaluation set.
4. Report video-level detection outcomes, alert latency, false alarms, missed detections, and robustness/error analysis for glasses, low lighting, and head movement where data permits.
5. Preserve provenance, licensing, consent records, split assignments, configuration, and experiment results sufficiently for another researcher to reproduce the reported evaluation.
6. Treat Accuracy ≥ 0.90 for eye classification and system-level test performance as instructor-stated research goals, not guaranteed requirements or achieved results.

### Minimum viable application

One person, local webcam or recorded video input, face/landmark observation, eye-region analysis with CNN eye classification and a distinct landmark-derived eye-state estimate, temporal PERCLOS and prolonged-closure indicators, visible status, audible warning, handling of unknown observations, and a recordable run suitable for evaluation. A recorded-video mode supports repeatable experiments; audio warnings are required for live demonstration and may be suppressed during offline replay.

### Optional extensions

Personalized alert thresholds, a larger and more diverse volunteer study, broader occupational monitoring, additional sensors or features, and publication of a newly collected dataset. These are not prerequisites for the initial SRS acceptance.

### Explicit non-goals

Multiple-driver tracking; cloud processing or storage; mobile applications; vehicle integration or control; certified safety claims; clinical diagnosis; identity recognition; automatic personalization; and treating a missing face as open eyes. Detailed implementation architecture, libraries, model internals, and numerical hardware/FPS guarantees are outside this requirements specification.

## 4. Functional Requirements

Each requirement is mandatory unless explicitly labelled optional. “Unknown” means the observation cannot support an open/closed inference.

| ID | Requirement |
|---|---|
| FR-001 | The application shall allow the user to select and start an available local webcam, report an unavailable or failed input, and stop the session without requiring a network service. |
| FR-002 | The application shall accept a recorded video as an input for repeatable analysis and associate observations with source timestamps; it shall distinguish live capture time from recorded-media time in results. |
| FR-003 | For the single-person scope, the system shall identify the selected face and obtain facial landmarks needed for eye and, when enabled, mouth/head-feature analysis. It shall expose a no-face/invalid-observation state when required evidence is unavailable. |
| FR-004 | The system shall extract left and right eye regions from a valid face observation and mark unusable, out-of-frame, or insufficiently observed regions invalid. |
| FR-005 | The system shall provide a CNN-based open/closed eye-region classification with a confidence value for each usable eye region. The CNN result shall remain identifiable as a distinct evidence source. |
| FR-006 | The system shall provide a separate landmark-derived eye-state estimate from 2D eye landmarks, including an unknown result for invalid geometry or inadequate evidence. |
| FR-007 | The system shall calculate PERCLOS as closed-eye duration divided by valid observed eye duration in a configurable time window, using timestamps rather than frame counts. It shall report the window, valid duration/coverage, eye-state source, and whether the estimate is ready. |
| FR-008 | The system shall detect prolonged eye closure using a configurable duration criterion and shall distinguish that event from short closures. The criterion and any blink handling rule shall be recorded with the run. |
| FR-009 | When Method B is selected, the system shall derive a temporal yawning indicator from valid mouth observations, prevent a continuous mouth-open interval from being counted repeatedly as separate yawns, and expose invalid/unknown evidence. |
| FR-010 | When Method C is selected, the system shall derive a head-pose indicator from valid facial observations, apply a documented reference/threshold rule, and expose invalid/unknown evidence. |
| FR-011 | The system shall support the three named decision methods A, B, and C as separately selectable configurations. It shall use the same PERCLOS source and base temporal settings across a comparison unless a deliberate difference is disclosed. |
| FR-012 | The system shall produce a drowsiness-related status (at minimum normal, warning, and unknown/unavailable) and a human-readable reason tied to the evidence and method that caused the status. It shall not use unknown evidence as evidence of normality. |
| FR-013 | During a live session, the application shall present current processing/observation status and a visible warning when the configured decision rule is met. |
| FR-014 | During a live session, the application shall emit an audible warning when the configured decision rule is met and shall provide a documented mechanism to prevent uncontrolled repeated playback. |
| FR-015 | On no face, temporary tracking loss, invalid landmarks, uncertain classification, or insufficient valid PERCLOS coverage, the system shall mark evidence unknown, break or suspend affected temporal continuity, and avoid inferring open eyes from missing data. It shall show the unavailable state when it affects interpretation. |
| FR-016 | If multiple faces are present, the system shall not silently combine evidence from different people. It shall either maintain the explicitly selected single subject or report ambiguity and withhold a subject-specific decision. Multiple-person monitoring is out of scope. |
| FR-017 | If a live camera disconnects or stops yielding frames, the system shall stop making new decisions from stale observations and inform the user that input has failed. |
| FR-018 | The system shall support experiment runs for A, B, and C on specified input material and record method, configuration/thresholds, timestamps, evidence source, status/reason, and per-run outcome needed to reproduce the comparison. |
| FR-019 | The system shall produce exportable experiment records and a summary suitable for comparing methods, including counts of evaluated cases and the specified eye-classification/video-level/latency/error measures when the necessary labels are supplied. |
| FR-020 | The system shall allow live audio to be disabled for offline evaluation and shall record whether audio was enabled; muting shall not silently change the underlying detection result. |

## 5. Non-Functional Requirements

| ID | Requirement |
|---|---|
| NFR-001 | Eye-classification Accuracy ≥ 0.90 and system-level test Accuracy ≥ 0.90 are research goals from the instructor brief. Results shall report actual values and test-set definitions; failure to meet a goal shall be reported rather than concealed. |
| NFR-002 | Processing performance, including throughput and alert latency, shall be measured and reported on declared hardware, input resolution, and input type. The instructor gives no mandatory FPS, latency, or hardware threshold; any later numeric target is provisional until approved and supported by the evaluation setup. |
| NFR-003 | Resource use shall be measured on the declared test machine or described qualitatively if reliable measurement is unavailable. No hardware capability threshold is implied by “ordinary computer.” |
| NFR-004 | Reliability: invalid input, failed camera, missing face, invalid landmarks, and model/prediction uncertainty shall result in a visible unavailable/error state rather than a fabricated normal decision. A run shall retain enough status information to identify interruptions. |
| NFR-005 | Maintainability: requirements, user-facing configuration, data preparation, and experiment procedure shall be documented. Experimental parameters affecting results shall be explicit and versioned with run records. |
| NFR-006 | Reproducibility: a reported comparison shall identify data source/version where known, license, labels, split assignment, method, eye-state source, thresholds, temporal window, valid-observation rules, and evaluation definitions. Re-running with those recorded inputs shall use the same declared protocol. |
| NFR-007 | Privacy: webcam processing shall be local by default. Capture shall not be uploaded or retained by default. Any volunteer recording shall require documented informed consent, defined access/retention/deletion handling, and must not be committed to source control. |
| NFR-008 | Usability: the operator shall be able to identify the selected input, current observation availability, current status/reason, and how to stop or mute the demonstration. Errors shall be presented in terms understandable to a student operator. |
| NFR-009 | Alerts and outputs shall identify DrowsyAlert as a research aid and shall not claim guaranteed detection or replace official road-safety measures. |

## 6. Data Requirements

| ID | Requirement |
|---|---|
| DR-001 | The study shall use a public eye-state dataset for open/closed image classification and a public drowsiness dataset where its license, labels, and use conditions permit. The instructor names a Kaggle Drowsiness Detection Dataset but supplies no URL or version; selection must be documented before training. |
| DR-002 | Eye-image labels shall use a documented open/closed definition. Ambiguous, occluded, or unusable samples shall be excluded or separately labelled, not silently forced into either class. Label mapping and any adjudication shall be recorded. |
| DR-003 | Video-level drowsiness evaluation shall use videos with time-localized reference labels sufficient to identify event start/end or another explicitly stated temporal ground truth. Image-only labels do not establish alert latency. |
| DR-004 | Volunteer recordings shall be collected only after informed consent, with the purpose, capture conditions, storage/access, retention/deletion approach, and intended evaluation use recorded. Participation shall be voluntary. |
| DR-005 | Data shall be divided into training, validation, and held-out test sets by subject or recording session where identifiers permit. Adjacent frames or crops from one recording shall not be split across training and test. If subject/session grouping is unavailable, the limitation and leakage risk shall be reported. |
| DR-006 | Data provenance records shall identify source, dataset name/version where available, retrieval date, license/terms, label source, transformations, exclusions, and split assignment. No URL, version, or dataset statistic is presumed by this specification. |
| DR-007 | Dataset terms shall be reviewed before use or redistribution. Restricted or personal video shall remain outside version control; published artifacts shall include only material permitted by consent and license. |
| DR-008 | Evaluation material shall document or annotate glasses, lighting condition, and head movement when those conditions are used for robustness analysis. Missing condition labels shall be reported as unavailable, not inferred. |

## 7. Experimental Requirements

1. **Eye-state classification**: evaluate open/closed predictions on a held-out image/sample set. Report sample counts, class definitions, Accuracy, confusion matrix, and recommended Precision, Recall, and F1 per class (with averaging rule stated). This measures image-level classification, not temporal drowsiness detection.
2. **PERCLOS source**: explicitly identify whether PERCLOS uses landmark-derived eye state or CNN-derived eye state. The primary research answer must include landmark-derived PERCLOS. CNN-derived PERCLOS is a useful secondary comparison, not a substitute for the primary question.
3. **Methods A/B/C**: run all methods against the same held-out videos, ground-truth labels, subject/session partition, timestamp source, base PERCLOS settings, and event matching rule. Tune thresholds on validation only. Disclose method-specific parameters and any missing-data exclusions.
4. **Video-level detection**: report event-level or interval-level precision/recall/F1 and the matching/tolerance rule; report false alarms per evaluated time (or another stated denominator), missed reference events, and evaluated valid/unknown time. Do not present frame Accuracy as the sole measure of temporal warning quality.
5. **Alert latency**: define reference event onset and alert time; report their difference per detected event and a summary distribution. Undetected events count as misses, not zero-latency alerts. State treatment of pre-existing alert state and event overlap.
6. **Robustness**: stratify results for glasses, low lighting, and head movement when adequately labelled data exists. Report per-condition sample/event counts and observation-loss rate; do not claim robustness from an unlabelled or insufficient subgroup.
7. **Accuracy goals**: report instructor goals of ≥0.90 separately for eye classification and system-level test performance. The system-level label unit and calculation must be defined before interpreting the number; this specification does not assume that image Accuracy equals warning Accuracy.
8. **Reproducible deliverables**: provide source and usage guidance, data preparation instructions, model/checkpoint and configuration when legally distributable, a webcam demonstration, representative alert examples, A/B/C result tables, and a research report of 35–45 pages with presentation slides. A model artifact that cannot legally be distributed shall be documented with acquisition/preparation instructions instead.

## 8. Acceptance Criteria

### Functional requirement verification

Each item below is an observable acceptance check for the corresponding FR.

| Requirement | Acceptance criterion |
|---|---|
| FR-001 | Start a connected webcam and observe frames; disconnect or deny access and observe an input error; stop the session and verify processing ends. |
| FR-002 | Process the same recorded clip twice and verify source timestamps are present and outcomes can be compared; records identify recorded input. |
| FR-003 | On valid single-face samples, observe face/landmark availability; on no-face and invalid-landmark samples, observe explicit invalid status. |
| FR-004 | For valid samples, inspect two eye regions; provide out-of-frame/invalid geometry and verify affected regions are rejected. |
| FR-005 | Run labelled open and closed eye samples through the CNN path and verify one class and confidence are emitted per usable eye; unavailable model/data is reported. |
| FR-006 | Run known open/closed landmark samples and invalid geometry; verify separate state output and unknown for invalid input. |
| FR-007 | Feed timestamped states with known closed/valid durations and gaps; verify PERCLOS equals closed duration divided by valid duration within declared numerical tolerance, and coverage/readiness/source are recorded. |
| FR-008 | Feed a short closure and a closure meeting the configured duration; verify only the latter meets prolonged-closure criteria; verify the configured duration is in run metadata. |
| FR-009 | In Method B, provide a sustained mouth-open interval followed by closure; verify one event at most for that interval, and invalid mouth observations do not create an event. |
| FR-010 | In Method C, provide valid pose samples on both sides of the configured rule plus invalid pose; verify indicator transitions and unknown handling match the documented rule. |
| FR-011 | Select A, B, and C and verify each uses its named evidence combination and common base settings in a comparison record. |
| FR-012 | Trigger each decision with known evidence; verify status and reason identify the cause; replace evidence with unknown and verify no normal inference is made from missing data. |
| FR-013 | Trigger a warning during live operation and verify visible status/reason; verify normal and unavailable states are also distinguishable. |
| FR-014 | Trigger a live warning and verify audible output; sustain the condition and verify repeated playback follows the documented repeat limit/cooldown. |
| FR-015 | Inject tracking loss, invalid landmark, uncertain prediction, and insufficient coverage; verify unknown/unavailable state, no inferred open state, and continuity reset/suspension. |
| FR-016 | Present two faces; verify ambiguity/selection behavior and that evidence from both faces is never combined. |
| FR-017 | Disconnect the live camera after a valid frame; verify stale data does not continue producing new decisions and input failure is visible. |
| FR-018 | Execute an experiment for each method and verify run records include the declared method, parameters, timestamps, evidence source, and status/reason. |
| FR-019 | Export records and verify a summary contains counts and each metric that can be calculated from provided labels; unavailable metrics are identified rather than fabricated. |
| FR-020 | Mute a live session and replay a video with audio disabled; verify audio state is recorded and detection outputs remain unchanged. |

### Research and delivery acceptance

- **RA-001**: The primary research question and all three method definitions appear in the report and result table.
- **RA-002**: Eye-image metrics and temporal/video alert metrics use separate definitions and denominators; the test split is held out from threshold selection.
- **RA-003**: Results report latency, false alarms, misses, valid/unknown coverage, and condition-stratified robustness where labels permit.
- **RA-004**: Actual eye classification and system-level accuracy are reported against the ≥0.90 research goals, regardless of whether achieved; no claim of success is based on an unreported or leaked test split.
- **RA-005**: Data source, license/terms, provenance, labels, splits, and volunteer consent handling are documented; no unauthorized personal video is included in source control or public artifacts.
- **RA-006**: Required technical/user guidance, data preparation instructions, demo, experiment result tables, report (35–45 pages), and slides are present or their explicitly unresolved delivery status is recorded at project review.
- **RA-007**: The interface/report identifies the system as advisory research and states relevant observation limitations.

## 9. Edge Cases and Failure Scenarios

| Scenario | Required behavior |
|---|---|
| No face detected | Mark face/eye evidence unknown, do not infer open eyes, suspend invalid temporal evidence, and display unavailable status when relevant. |
| Temporary tracking loss | Break continuity across the unobserved interval; do not count the gap as open or closed. Resume only with valid observations and sufficient coverage. |
| Multiple faces | Maintain only an explicitly selected subject or withhold a subject-specific result; never blend signals. This remains outside the multi-person product scope. |
| Poor lighting | Mark low-confidence/invalid evidence unknown; record observation loss. Report performance by lighting condition when labels exist. |
| Glasses or partial eye occlusion | Return uncertain/unknown for unusable eye evidence; do not force a class; include condition in robustness analysis where annotated. |
| Short natural blinks | Count observed closed duration consistently in PERCLOS, but do not trigger prolonged-closure alert unless the configured sustained-duration criterion is met. The PERCLOS window/threshold policy must be recorded. |
| Prolonged eye closure | Trigger the configured prolonged-closure warning and record event onset, warning time, and reason. |
| Camera disconnection | Stop decisions based on stale frames and notify the user; resume only after a new valid input session/observation. |
| Uncertain predictions | Expose uncertainty/unknown and exclude it from valid PERCLOS duration; do not silently convert it to open or closed. |
| Non-monotonic or missing timestamps | Reject or mark the affected interval invalid; do not calculate duration from frame index as a substitute without declaring a separate protocol. |
| Mouth/head feature unavailable | Methods B/C shall report missing auxiliary evidence and shall not silently substitute it with a positive or negative event. |

## 10. Assumptions, Constraints, and Open Questions

### Assumptions and constraints

- Initial operation is one person, facing a locally connected webcam, with all processing local by default.
- Recorded video is required for repeatable experiments even though the live webcam is the primary demonstration input.
- PERCLOS requires an explicit window, valid-observation coverage rule, eye-closure definition, and timestamp policy; values shown in project notes are examples/configuration candidates, not approved research thresholds.
- No target FPS, end-to-end latency limit, hardware specification, or resource ceiling is mandated by the official brief.
- Dataset selection, data availability, dataset licensing, and annotation quality are not guaranteed.
- Repository inspection found an application scaffold with webcam/video entry points, face/landmark handling, EAR, temporal PERCLOS, optional CNN inference, auxiliary-feature/decision/alert paths, and tests for some behaviors. It does not establish that the CNN has been trained, a suitable checkpoint or dataset is present, the application has been validated end-to-end, or any research target has been achieved. Acceptance applies to verified behavior, not code presence.

### Open questions and ambiguities

| ID | Unresolved question or conflict | Proposed resolution and trade-off |
|---|---|---|
| OQ-001 | Resolved 2026-10-26: Constitution v1.0.0 was adopted with seven binding principles and governance. | Apply the constitution to subsequent PLAN, TASKS, and IMPLEMENT work. |
| OQ-002 | Resolved 2026-10-26: the requested filename ending in `(2).docx` is absent; the available unsuffixed `PhieuMoTaDeTai_30DeTai_ThiGiacMayTinh_NCKH.docx` is the approved Project 12 source for this feature. | Preserve its recorded SHA-256 identity in `decisions.md`; review again if a different official revision is supplied. |
| OQ-003 | Resolved by approved Protocol v1.1: landmark-derived PERCLOS is the primary source for A/B/C; CNN eye-image classification is evaluated separately, and any CNN-derived temporal comparison is labelled as a separate ablation. System Accuracy uses the frozen video-level protocol definition. | Preserve separate evidence sources and cite `docs/evaluation-protocol.md`. |
| OQ-004 | Resolved by approved Protocol v1.1: primary system Accuracy uses fixed one-second bins with 50% overlap; UNKNOWN counts incorrect in the primary denominator, with observed-only Accuracy reported as a secondary diagnostic. | Apply the frozen definition and report its denominator/coverage. |
| OQ-005 | Resolved for the approved study path: CEW supplies eye images and NITYMED HDTV720 supplies temporal videos. Final annotation/manifest validation remains pending under T-139. | Cite the dataset cards and Protocol v1.1; do not treat unreviewed data as ground truth. |
| OQ-006 | Partially open: temporal PERCLOS, prolonged-closure, yawn, and pose thresholds remain provisional and must be selected on validation data under T-157/T-158. The CNN eye-classification threshold was frozen under T-013. | Record temporal values and hashes; never tune on test data. |
| OQ-007 | Resolved by Protocol v1.1: participant mapping is unavailable, so the approved split is clip-disjoint and must disclose possible participant overlap; no subject-independent claim is permitted. | Use the frozen split identity and limitation statement. |
| OQ-008 | Resolved: stratify glasses, low light, and head movement only where reviewed labels and sample counts support analysis; disclose unavailable conditions without inventing minimum subgroup sizes. | Report counts and observation loss for each supported subgroup. |
| OQ-009 | Deferred: no volunteer recordings are included in the current public-data study. Any later collection requires supervisor/institution guidance, informed consent, and documented access/retention/deletion controls. | Do not collect or publish participant recordings until those controls are approved. |
| OQ-010 | Resolved scope: the report and slides are required deliverables; timeline notes are planning context. Checkpoints/configuration/demo artifacts remain subject to data/model license and consent limits. | Track preparation and evidence under T-030/T-031 without fabricating results. |

## Instructor Requirements Coverage Checklist

Mapped to Project 12 in the available official DOCX (sections 1–9); the source document's filename is noted in the header and OQ-002.

| Covered | Instructor requirement | SRS location |
|---|---|---|
| [x] | Research question: 2D-landmark PERCLOS versus yawning/head pose | §2; OQ-003 |
| [x] | Compare at least three methods: PERCLOS; PERCLOS+yawn; PERCLOS+head pose | §2, §7, RA-001 |
| [x] | Detect prolonged eye closure and yawning; webcam drowsiness system, system Accuracy goal ≥0.90 | §3, FR-008–FR-012, NFR-001, RA-004 |
| [x] | Public drowsiness data and consented volunteers | §6 DR-001, DR-004, DR-007; OQ-005, OQ-009 |
| [x] | Pretrained face/eye-region detection plus CNN open/closed classification and temporal eye ratio | FR-003–FR-007; CNN/landmark separation in §2 |
| [x] | Audible warning demonstration | FR-014, FR-020; FR acceptance table |
| [x] | Source code, webcam demo, report, slides | §7 item 8; RA-006 |
| [x] | Advisory-only, not a replacement for official road safety | §1; NFR-009; RA-007 |
| [x] | Python/CV technical preferences and ordinary computer | Recorded as context, not mandated implementation choices or numerical performance constraints (§5 NFR-002–003; §10) |
| [x] | Eye-state Accuracy target ≥0.90; alert latency measurement; examples of status/warning | §7 items 1, 5, 7; RA-002–004; FR-013–014 |
| [x] | Public eye-state image data for CNN classification | §6 DR-001; CNN image metrics in §7; see OQ-005 |
| [x] | Glasses and low-light robustness; adaptive thresholds as research direction | §3 optional extensions; §7 item 6; OQ-006/OQ-008 |

## Specification Quality Review

- **WHAT rather than HOW**: Pass. Requirements specify observable behavior; no library, class, or internal architecture is mandated.
- **Problem, users, environment, limitations, motivation**: Pass (§1).
- **Research and scope definition**: Pass (§2–3).
- **Unique, testable functional requirements**: Pass; FR-001–FR-020 each has an acceptance check (§8).
- **Measurable/configurable non-functional requirements**: Pass; unsupported timing/hardware thresholds are expressly not invented.
- **Data and experimental integrity**: Pass (§6–7).
- **Edge cases**: Pass (§9).
- **Assumptions, ambiguity, trade-offs, readiness**: Pass (§10 and below).
- **Open decisions/evidence**: Numerical thresholds remain validation-only inputs (OQ-006); volunteer collection remains deferred pending supervisor guidance (OQ-009); annotation and held-out evidence gates are tracked by T-139 and T-157–T-159.

## PLAN Phase Readiness

**Approved requirements baseline (2026-10-26)**: the constitution and available unsuffixed Project 12 DOCX are accepted as the governing sources. CEW/NITYMED data paths and Protocol v1.1 are approved. Remaining evidence gates are final annotation validation (T-139), validation-only temporal threshold selection (T-157/T-158), independent held-out review (T-159), and any future volunteer collection guidance (OQ-009). Approval does not imply that held-out video results or target attainment already exist.
