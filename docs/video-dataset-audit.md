# Phase 6 Temporal-Video Dataset Audit

**Audit date:** 2026-10-26

**Status:** Candidate review only. No Phase 6 video dataset has been selected,
downloaded, approved, or evaluated.

Phase 6 requires face videos with time-localized reference evidence. The CEW eye-image
dataset used in Phase 3 cannot supply event onset/offset, alert latency, false alarms per
time, or a controlled A/B/C video comparison.

## Current local inventory

- No approved temporally annotated drowsiness video corpus is present under `data/`.
- No volunteer recording is authorized. The deferred webcam test is demonstration
  evidence and must not be repurposed as held-out research data.
- The ignored MediaPipe face model and EyeCNN checkpoint are implementation assets, not
  reference labels.

## Candidate review

| Candidate | Primary-source evidence reviewed | Temporal suitability | Rights/access and decision |
|---|---|---|---|
| NITYMED | University of Peloponnese dataset portal describes 130 night-driving MP4 videos from 21 participants, including yawn and microsleep categories, with participant diversity and two resolutions | Event-focused clips are promising, but the public description states event counts/categories rather than verified onset/offset annotations; independent temporal annotation would still be required | Portal states Creative Commons Attribution and requires an access form with name, affiliation, and academic/business email. **Recommended practical fallback**, subject to owner access, archive verification, and supervisor approval |
| NTHU-DDD | Commonly described as including normal driving, slow blinking, yawning, nodding, and other conditions; a primary official terms/download page was not verified during this audit | Potentially the best behavioral coverage if official frame labels, subject IDs, and terms are confirmed | **Preferred candidate only if** the owner obtains it from the original provider and supplies the official terms/annotation documentation. Do not use an unverified mirror |
| UTA-RLDD | Official UTA page describes 180 RGB videos (60 people, three approximately 10-minute videos per person), video-level alert/low-vigilance/drowsy self-labels, and five subject folds | Whole-video predominant-state labels do not by themselves provide event onset/offset, so they cannot directly support alert latency or event matching | Public access link exists, but a clear reuse-license grant was not located on the reviewed page. Requires terms confirmation and new independent temporal annotation; **not the first choice for this phase** |
| DROZY | University of Liège/ORBi provides NIR video, timestamps, KSS, PVT/physiological signals, landmarks, and an explicit research/evaluation-only agreement | Strong timestamp and subject/session provenance, but KSS is session-level rather than a verified facial drowsiness-event onset label; NIR also differs from the current RGB demo domain | Download is available from ORBi. Agreement prohibits redistribution, commercial use, identity disclosure, and display of non-publishable images. Useful for a separate sleepiness analysis, but **not sufficient alone for the planned event-latency endpoint** |
| Kaggle image/crop collections | No authoritative temporal-video source/version and rights record was established | Image or crop labels cannot support temporal event scoring | Rejected for Phase 6 unless an exact upstream video source, license, subject/session grouping, and temporal labels are independently verified |

Primary pages reviewed:

- NITYMED portal: <https://datasets.esdalab.ece.uop.gr/>
- UTA-RLDD provider page: <https://sites.google.com/view/utarldd/home>
- DROZY provider description: <https://www.drozy.ulg.ac.be/>
- DROZY ORBi record and archive: <https://orbi.uliege.be/handle/2268/191620>
- DROZY license agreement: <https://orbi.uliege.be/bitstream/2268/191620/5/DROZY-LicenseAgreement-20180718.pdf>

## Required owner action

Choose one of these paths before T-024:

1. Obtain NTHU-DDD from its original provider and supply the official license/terms,
   archive, annotation guide, and subject/session layout for audit.
2. Request NITYMED from the university portal, then supply the untouched archive and
   access/license evidence. The project must create and review temporal annotations.
3. Propose another public source with authoritative terms, subject/session grouping,
   and time-localized labels.
4. Use volunteer videos only after supervisor/ethics approval and a written consent,
   access, retention, withdrawal, deletion, and publication procedure.

No candidate is approved merely because it can be downloaded. T-024 must hash and
inspect the actual owner-provided archive, verify the terms, establish subject-disjoint
partitions, and assess label sufficiency before any evaluation run.
