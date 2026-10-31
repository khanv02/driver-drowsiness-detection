# Phase 6 Temporal-Video Dataset Audit

**Audit date:** 2026-10-26

**Status:** NITYMED HDTV720 acquired and integrity-audited. It is selected for local
Phase 6 preparation, but temporal annotation, participant grouping, split assignment,
and protocol approval remain required before final evaluation.

Phase 6 requires face videos with time-localized reference evidence. The CEW eye-image
dataset used in Phase 3 cannot supply event onset/offset, alert latency, false alarms per
time, or a controlled A/B/C video comparison.

## Current local inventory

- The official grouped NITYMED HDTV720 download is present under ignored `data/` storage:
  126 MP4 videos, 697,049,508 bytes, and 5,860.677 seconds of media.
- All videos decode at 1280x720; 125 report 25 FPS and one reports 24 FPS.
- The local manifest and exact discrepancies are documented in
  [NITYMED dataset card](../research/nitymed-dataset-card.md).
- The corpus is not temporally annotated and has no verified clip-to-participant map, so
  it is not yet an approved held-out evaluation corpus.
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

## Remaining owner/reviewer action

1. Retain evidence that the NITYMED access form and provider terms were followed.
2. Obtain a provider participant mapping, if one exists, or record that a
   participant-disjoint split cannot be guaranteed.
3. Independently annotate event onset/offset in media time and review those labels.
4. Approve/freeze the evaluation protocol before held-out scoring.

Volunteer recording remains unauthorized and unnecessary while this public-data path is
being evaluated. Acquisition alone does not approve final scoring.
