# Eye-State Dataset Card

Status: **CEW extraction and split manifest verified; approved for academic research training**
Reviewed: 2026-10-26

This document records dataset authority separately from code readiness. No dataset is
downloaded, redistributed, or committed by this repository.

## Selected source: Closed Eyes in the Wild (CEW)

- Official page: <https://parnec.nuaa.edu.cn/_upload/tpl/02/db/731/template731/pages/xtan/ClosedEyeDatabases.html>
- Published description: 2,423 subjects (1,192 closed-eye and 1,231 open-eye examples).
- Distributed eye patches are described as 24 x 24 pixels.
- Permitted scope stated by the publisher: research use only and non-commercial use.
- Required controls stated by the publisher: do not redistribute the database and cite
  the CEW work in research that uses it.
- Project use: university research prototype only. Commercial use is not approved.
- Acquisition: the project owner downloads the eye-patch archive from the official page
  and extracts it into `data/raw/cew/`. Raw files stay ignored by Git.

Selection is conditional: T-075 must verify the retrieved archive/file identity, actual
layout, counts, readable images, and label mapping before any real training. A web-page
count is not treated as a local-data measurement.

### Label and split protocol

- `open` maps to class `0`; `closed` maps to class `1`.
- Ambiguous, unreadable, or unlabeled files are excluded and counted.
- The original relative path and content hash remain in the generated manifest.
- CEW left/right filenames share the source-face stem. Both eye patches from one published
  subject are placed in one group, with exact and near-duplicate images also linked.
- The deterministic seed is `42`. Splits target 70% train, 15% validation, and 15% test;
  all splits must contain both classes.
- Model/checkpoint selection uses train and validation only. The test split is evaluated
  once after the model and decision rule are frozen.
- The official description says the 2,423 examples are subjects, but the package contains no
  separate identity table. Pair grouping prevents direct left/right leakage; identities
  beyond the filename pair cannot be independently audited and this limitation must accompany
  every result.

### Known domain limitations

The publisher describes closed-eye examples as collected from the internet and open-eye
examples as selected from LFW. This creates a possible class/source confound. CEW can
validate the engineering path and provide a documented academic baseline, but it is not
by itself proof of in-vehicle generalization or temporal drowsiness detection.

## Rejected source: Kaggle `dheerajperumandla/drowsiness-dataset`

- Page: <https://www.kaggle.com/datasets/dheerajperumandla/drowsiness-dataset>
- Metadata inspected on 2026-10-26 reported version 1, updated 2020-09-27, and license
  `Unknown`.
- Decision: rejected for this project until the owner supplies explicit permission or a
  usable license from the rights holder.
- The former downloader was removed because automatic retrieval could imply permission
  that the metadata does not establish.

## Alternative requiring rights confirmation: MRL Eye Dataset

- Official page: <https://mrl.cs.vsb.cz/eyedataset.html>
- The official description reports 84,898 infrared eye images from 37 people and embeds
  subject, eye state, glasses, lighting, and sensor attributes in filenames.
- It is attractive for subject-disjoint splitting, but this review did not obtain explicit
  reuse terms from the official page. It is not selected unless the research supervisor
  confirms the intended use is permitted and records that evidence here.

## T-075 local acceptance record

Accepted on 2026-10-26 after the project owner supplied the official CEW extraction and
the research-only/non-commercial/no-redistribution conditions were recorded.

- Source page: the official CEW page above; published dataset version has no explicit
  numeric version, so the retrieval identity is the verified extraction tree hash.
- Original archive: not retained in `data/raw/cew/`; archive filename, byte size, and hash
  are unavailable. This limitation is recorded rather than inferred.
- Selected package: `data/raw/cew/dataset_B_Eye_Images/`.
- Label folders: `openLeftEyes` and `openRightEyes` map to open (0);
  `closedLeftEyes` and `closedRightEyes` map to closed (1).
- Input tree SHA-256: `4e9ebee01647d80f9679f8b71d3d5a32b3ebb4968c6bce0ca51491db13883a53`.
- Actual input: 4,846 readable patches, 0 unreadable, 0 unlabeled, 0 exact duplicates
  removed; 2,462 open patches and 2,384 closed patches.
- Grouping: 2,423 filename-paired source-face groups; left/right patches stay together.
- Train: 3,392 images / 1,696 groups (1,700 open, 1,692 closed).
- Validation: 726 images / 363 groups (386 open, 340 closed).
- Test: 728 images / 364 groups (376 open, 352 closed).
- `manifest.csv` SHA-256:
  `42ebc450eba138301f13df4cd06736b31dab20b7d2fa55464251ed87c765c58f`.
- `dataset.json` SHA-256:
  `1e7ade37a93f42005a0cdc30d679500269f06666744919fcfc1555bcc6344649`.
- The manifest passed schema, binary-label, hash, group-disjointness, and both-classes-per-split
  validation. It is approved for the documented university research use.

T-075 is complete. Real training may proceed. Synthetic checks remain engineering evidence
only and are not included in the final CEW accuracy claim.
