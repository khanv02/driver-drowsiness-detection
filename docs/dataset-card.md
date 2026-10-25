# Eye-State Dataset Card

Status: **CEW selected for academic research, pending owner-provided files and local verification**  
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
- CEW's public description does not provide reusable subject/session identifiers for the
  eye-patch package. Each source image is therefore treated as an independent group,
  with exact and near-duplicate images forced into the same group.
- The deterministic seed is `42`. Splits target 70% train, 15% validation, and 15% test;
  all splits must contain both classes.
- Model/checkpoint selection uses train and validation only. The test split is evaluated
  once after the model and decision rule are frozen.
- Because identity separation cannot be proved without identity metadata, this limitation
  must accompany every CEW result. No subject-independent claim may be made.

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

Pending. After the owner provides CEW, record:

- official retrieval date and page;
- original archive filename, byte size, and SHA-256;
- extraction layout and label-folder mapping;
- readable, unreadable, excluded, open, and closed counts;
- duplicate/group statistics and final split counts;
- generated `dataset.json` and `manifest.csv` SHA-256 values;
- reviewer approval for the research-only/non-commercial restriction.

Until this section is complete, T-010, real-data T-012, T-013, T-086, and G3 remain
blocked. Synthetic tests and smoke runs are not performance evidence.
