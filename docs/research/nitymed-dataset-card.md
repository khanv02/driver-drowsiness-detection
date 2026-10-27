# NITYMED HDTV720 Dataset Card

**Local dataset ID:** `nitymed-hdtv720`

**Inventory date:** 2026-10-26

**Inventory manifest SHA-256:**
`bb654b8c5f7104d23268503f02935d3c30974a0199fa4c64d3b8fe4985816307`

**Evaluation readiness:** Acquired and decode-verified; Protocol v1.1 and a deterministic
clip-disjoint split are approved. Final annotation/manifest validation remains open under
T-139. Participant-to-clip mapping is unavailable, so possible participant overlap must
be disclosed and subject-independent generalization must not be claimed.

## Source and permitted use

- Provider: University of the Peloponnese NITYMED portal,
  <https://datasets.esdalab.ece.uop.gr/>.
- Provider page last-updated date: 2022-05-25.
- Provider-declared license: Creative Commons Attribution (CC BY), with citation of one
  or more listed dataset papers requested by the provider.
- Access path: the provider access form and its grouped HDTV720 downloads. The project
  owner must retain any access confirmation outside Git.
- Local scope: extracted HDTV720 MP4 files only. No archive was retained, so archive
  hashes are unavailable; the ignored local manifest records a SHA-256 for every video.
- Raw videos and the generated manifest remain under ignored `data/` paths and are not
  redistributed by this repository.

The category folders describe the provider's clip grouping. They do not contain event
onset/offset annotations and are not treated as temporal reference truth. Protocol v1.1
locks a balanced 38-clip split (12 validation and 26 held-out test); the four clips
viewed during the pilot remain in validation. Independent review and final manifest
validation are evidence gates and are not implied by the split artifact alone.

## Observed inventory

| Group | Videos |
|---|---:|
| Yawning / Male | 48 |
| Yawning / Female | 59 |
| Microsleep / Male | 11 |
| Microsleep / Female | 8 |
| **Total** | **126** |

- Total bytes: 697,049,508 (664.76 MiB).
- Total media duration: 5,860.677 seconds (about 97 minutes 41 seconds).
- Decode check: all 126 videos opened and yielded a first frame.
- Resolution: all 126 are 1280x720.
- Frame rate: 125 report 25 FPS. `P1042749_720.mp4` reports 24 FPS; evaluators must
  use each video's actual media timestamps instead of assuming 25 FPS.
- Duplicate content hashes: none.
- Duplicate clip IDs: none.

The provider page says both "130 videos" and category totals of 107 yawning plus 21
microsleep videos (128). The actual grouped HDTV720 download contains 107 yawning plus
19 microsleep videos (126). This source discrepancy is disclosed rather than silently
corrected. The local manifest defines the exact corpus used by this project.

## Local artifacts

- Raw root: `data/raw/nitymed/DSM_Dataset-HDTV720/`
- Generated manifest: `data/processed/nitymed/video-manifest.csv`
- Manifest builder: `scripts/prepare_video_manifest.py`

Both data paths are ignored by Git. Rebuild the manifest from the repository root with:

```powershell
uv run python scripts/prepare_video_manifest.py `
  --root data/raw/nitymed/DSM_Dataset-HDTV720 `
  --output data/processed/nitymed/video-manifest.csv `
  --retrieval-date 2026-10-26
```

The command refuses to replace an existing manifest unless `--overwrite` is supplied.

## Known research limitations and next gate

- The download has no verified participant-to-clip mapping. Filenames, appearance, and
  sex folders must not be guessed into participant IDs. A subject-disjoint split cannot
  yet be demonstrated.
- The download has no reviewed media-time onset/offset labels. A human reviewer must
  annotate observable events independently of DrowsyAlert predictions.
- Glasses, lighting, and head-movement tags are not supplied per event and remain
  `unknown` unless independently reviewed.
- All clips remain `split=unassigned` until grouping is resolved. Held-out test scoring
  is prohibited before the split and protocol are frozen.

Accordingly, this corpus is ready for tooling and annotation work, but not yet for final
A/B/C research claims.
