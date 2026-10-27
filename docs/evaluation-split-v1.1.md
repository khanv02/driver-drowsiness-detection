# NITYMED Evaluation Split v1.1

**Protocol:** `drowsyalert-video-eval-v1.1`

**Selection seed:** 42

**Separation:** Clip-disjoint; participant mapping unavailable

**Canonical split identity:**
`2e4e0ea7eb2e529ea2db2f692444768a4de91023d9ce29829bcbdab911cbd047`

Local ignored artifacts:

| Artifact | File SHA-256 |
|---|---|
| `evaluation-split-v1.1.csv` | `13f0133e0b729a1b45fb480dab32cccea64aabe37154f130005e5ed15ddcf65e` |
| `evaluation-worklist-v1.1.csv` | `5ca1246e5361ec4075acc86d4253c7e2a346f4fb7ce3aa0ff4d3ac4b2a5ff67b` |
| `review-schedule-v1.1.csv` | `1a24bfb7d71aca9d4802372725ccf46be7344c86136be71a7b005f66429fc3a9` |

The corpus uses all 19 microsleep clips and a deterministic selection of 19 yawning
clips. There are no duplicate clip IDs or content hashes across partitions. The four
viewed pilot clips are locked to validation. Exact membership was frozen before further
annotation or held-out scoring.

## Counts

| Partition/category | Female | Male | Total |
|---|---:|---:|---:|
| Validation microsleep | 3 | 3 | 6 |
| Validation yawning | 3 | 3 | 6 |
| Test microsleep | 5 | 8 | 13 |
| Test yawning | 7 | 6 | 13 |

- Validation duration: 939.72 seconds across 12 clips.
- Test duration: 2,011.64 seconds across 26 clips.
- Total selected duration: 2,951.36 seconds (about 49 minutes 11 seconds).
- All 12 validation clips are reviewed. The 26 held-out test clips remain in seven
  review batches.

## Validation membership

- `P1042751_720`, `P1042760_720`, `P1042762_720`, `P1042776_720`
- `P1042797_720`, `P1043081_720`, `P1043084_720`, `P1043089_720`
- `P1043090_720`, `P1043106_720`, `P1043112_720`, `P1043115_720`

## Held-out test membership

- `P1042748_720`, `P1042756_720`, `P1042757_720`, `P1042764_720`
- `P1042767_720`, `P1042769_720`, `P1042772_720`, `P1042786_720`
- `P1042787_720`, `P1042793_720`, `P1042795_720`, `P1042796_720`
- `P1042799_720`, `P1043067_720`, `P1043068_720`, `P1043075_720`
- `P1043083_720`, `P1043085_720`, `P1043094_720`, `P1043100_720`
- `P1043101_720`, `P1043114_720`, `P1043119_720`, `P1043122_720`
- `P1043129_720`, `P1043134_720`

Test clips may be independently annotated while reviewers remain blind to model output,
but their labels/results must not be used to choose thresholds. Test replay occurs once
after validation configuration is frozen.

## Limitation

NITYMED states that 21 participants contributed data, but the acquired file layout does
not map clips to participants. Sex-folder stratification reduces an observable imbalance
but does not prevent the same participant from appearing in both partitions. Every
reported conclusion must therefore say `clip-disjoint` and disclose possible participant
leakage; it must not claim subject-independent generalization.
