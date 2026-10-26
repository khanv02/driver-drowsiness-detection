# NITYMED Independent Annotation Review

This workflow records observable event intervals in video media time. It does not use
DrowsyAlert predictions, EAR, PERCLOS, MAR, or head-pose outputs as reference labels.
The worklist, drafts, final annotations, and videos stay below ignored `data/` paths.

## 1. Initialize the worklist

```powershell
uv run python scripts/annotate_video_events.py init `
  --manifest data/processed/nitymed/video-manifest.csv `
  --worklist data/processed/nitymed/annotation-worklist.csv
```

The generated rows intentionally start with:

- `subject_group=unknown` and `session_group=unknown`;
- `split=unassigned`;
- condition fields set to `unknown`;
- `review_status=pending`.

Do not infer participant identity from a filename, sex folder, or automated face match.
Use a provider-supplied mapping or an independently reviewed project mapping. Assign
validation/test at the participant group level before final export. A participant or
session must never appear in both splits.

## 2. Review a clip

```powershell
uv run python scripts/annotate_video_events.py review `
  --root data/raw/nitymed/DSM_Dataset-HDTV720 `
  --worklist data/processed/nitymed/annotation-worklist.csv `
  --draft data/processed/nitymed/annotation-draft.csv `
  --clip-id P1042748_720
```

Controls shown in the review window:

- `Space`: pause/resume.
- `A` / `D`: seek backward/forward one second.
- `1`–`5`: first press starts the displayed event type; pressing the same key later
  closes it. Switching keys starts the newly selected event at the current time.
- `U`: remove the most recently recorded event for that clip.
- `Q`: save and quit. An unfinished interval is not saved.

The category folder may guide which behavior to inspect, but it is not itself an
onset/offset label. Reviewers must follow the frozen event-label guide. A second reviewer
and adjudication are preferred; if only one reviewer is available, use
`single_reviewer` and disclose the limitation.

For an exact time already observed in another permitted player, an interval can also be
entered without the review window:

```powershell
uv run python scripts/annotate_video_events.py add `
  --worklist data/processed/nitymed/annotation-worklist.csv `
  --draft data/processed/nitymed/annotation-draft.csv `
  --clip-id P1042748_720 --start 4.2 --end 6.1 --label yawn
```

## 3. Finalize metadata and export

Edit only the ignored worklist copy. Before setting `review_status=reviewed`, confirm
subject/session group, split, and condition tags. Final export refuses pending reviews,
unassigned splits, out-of-bounds events, circular label sources, and split leakage.

```powershell
uv run python scripts/annotate_video_events.py export `
  --worklist data/processed/nitymed/annotation-worklist.csv `
  --draft data/processed/nitymed/annotation-draft.csv `
  --output data/processed/nitymed/annotations.csv `
  --annotator-id reviewer-1 `
  --adjudication single_reviewer `
  --confidence not_provided
```

Do not run final held-out scoring merely because export succeeds. The protocol approval,
split audit, label review, and manifest hashes must also be frozen under T-126/T-139.
