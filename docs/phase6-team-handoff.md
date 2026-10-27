# Phase 6 team handoff

This page is the short onboarding guide for a teammate helping with the remaining
experimental evaluation work. It does not replace the frozen protocol in
[`evaluation-protocol.md`](evaluation-protocol.md).

## Current status

Phase 6 is not complete. The protocol, NITYMED audit, deterministic 38-clip split,
annotation tooling, metrics, batch runner, all 12 validation annotations, and the first
36-run A/B/C validation baseline are complete. The baseline exposed an unsuitable
30-second warm-up and is not a final result.

The remaining dependency order is:

1. T-157: replay stored validation observations over a bounded configuration search;
2. T-158: select and freeze one validation configuration;
3. T-159: independently review the 26 held-out test clips;
4. T-139/T-024: audit and freeze the final annotation manifest;
5. T-149/T-027: run held-out A/B/C once and publish the comparison.

Only the selected 26 test clips require further review, not all 126 NITYMED videos.
Every selected clip must be reviewed even when it contains no qualifying event. Keeping
fewer clips would require an explicit protocol amendment and would weaken the study.

## Data handoff

The dataset, worklists, schedules, and annotation drafts are intentionally excluded from
Git. Before beginning T-159, obtain these items from the maintainer through an approved
private channel:

- `data/raw/nitymed/DSM_Dataset-HDTV720/`;
- `data/processed/nitymed/video-manifest.csv`;
- `data/processed/nitymed/evaluation-worklist-v1.1.csv`;
- `data/processed/nitymed/review-schedule-v1.1.csv`;
- the current `evaluation-annotations-draft-v1.1.csv` and its backups.

Do not upload any of those artifacts to GitHub. Confirm that the split identity is
`2e4e0ea7eb2e529ea2db2f692444768a4de91023d9ce29829bcbdab911cbd047`
and use the `phase/6-experimental-evaluation` branch. If the identities or membership do
not match [`evaluation-split-v1.1.md`](evaluation-split-v1.1.md), stop and contact the
maintainer instead of generating a replacement split.

## Independent review procedure

Reviewers must remain blind to DrowsyAlert predictions, EAR, PERCLOS, MAR, head-pose
output, and previous model alerts. Run one clip with:

```powershell
uv run python scripts/annotate_video_events.py review `
  --root data/raw/nitymed/DSM_Dataset-HDTV720 `
  --worklist data/processed/nitymed/evaluation-worklist-v1.1.csv `
  --draft data/processed/nitymed/evaluation-annotations-draft-v1.1.csv `
  --clip-id P1042756_720
```

Controls:

- `Space`: play or pause;
- `A` / `D`: seek backward or forward one second;
- `2`: start/end a microsleep interval;
- `3`: start/end a yawn interval;
- `U`: remove the latest interval for the current clip;
- `Q`: save and exit.

For microsleep clips, record a complete visible sleep/awareness-loss episode and ignore
ordinary blinks or momentary eye closures. For yawning clips, record the complete clear
yawn and ignore ordinary mouth movement. When an onset or offset is uncertain, pause and
seek; do not infer it from the category folder. A clip may legitimately have zero events.

After each clip, tell the maintainer the clip ID is complete. The maintainer checks
bounds, labels, accidental short presses, and overlap before changing
`review_status=reviewed`. Do not manually normalize or delete another reviewer's events.

## Test review batches

Work through one batch at a time. The order alternates categories and makes recovery
from an interrupted session straightforward.

| Batch | Clip IDs |
|---|---|
| 1 | `P1042756_720`, `P1042748_720`, `P1042757_720`, `P1042764_720` |
| 2 | `P1042767_720`, `P1042769_720`, `P1042772_720`, `P1042795_720` |
| 3 | `P1042786_720`, `P1042796_720`, `P1042787_720`, `P1042799_720` |
| 4 | `P1042793_720`, `P1043083_720`, `P1043067_720`, `P1043085_720` |
| 5 | `P1043068_720`, `P1043094_720`, `P1043075_720`, `P1043100_720` |
| 6 | `P1043114_720`, `P1043101_720`, `P1043122_720`, `P1043119_720` |
| 7 | `P1043129_720`, `P1043134_720` |

## T-159 acceptance checklist

- all 26 held-out clips were independently viewed to completion;
- only observable microsleep/yawn intervals were recorded in media time;
- every clip is explicitly marked reviewed, including zero-event clips;
- no detector output was used as reference truth;
- the draft and worklist were returned privately and were not committed;
- the maintainer successfully exports and hashes the final test annotation manifest;
- no held-out score was inspected before the validation configuration was frozen.

The limitations remain important: participant mapping is unavailable, so the study is
clip-disjoint rather than subject-disjoint, and current labels use a single-reviewer
workflow unless a second independent reviewer is added.
