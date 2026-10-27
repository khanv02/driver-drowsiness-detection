# Local data

All files below `data/` are private/local and ignored by Git except `.gitkeep` files and
this README.

## CEW acquisition for Phase 3

1. Read the research-only, non-commercial, citation, and no-redistribution terms on the
   [official CEW page](https://parnec.nuaa.edu.cn/_upload/tpl/02/db/731/template731/pages/xtan/ClosedEyeDatabases.html).
2. Download the **eye-patch** archive manually from that official page. Do not use mirrors.
3. Before extraction, record the local archive identity:

   ```powershell
   uv run python scripts/download_dataset.py --archive C:\path\to\CEW-eye-patches.rar
   ```

4. Extract the archive under `data/raw/cew/`. Do not commit the archive or extracted data.
5. Tell the implementation agent when it is present. T-075 will inspect the actual layout
   before choosing the preparation command; do not rename folders merely to satisfy the
   current label parser.

Expected logical labels are `open` (class 0) and `closed` (class 1). The exact extracted
folder mapping must be recorded in `docs/dataset-card.md` after inspection.

## Directory policy

- `raw/`: untouched source archives/extractions with provenance recorded separately.
- `processed/`: generated eye images, manifests, and preparation reports.
- `volunteer/`: consent-governed participant data for later phases only.

Never commit downloaded datasets, participant footage, checkpoints, or generated results.
Do not redistribute CEW through this repository.

## Phase 6 temporal-video requirement

NITYMED HDTV720 is present under `data/raw/nitymed/DSM_Dataset-HDTV720/`. Its generated
inventory is `data/processed/nitymed/video-manifest.csv`; both locations are ignored.
See `docs/nitymed-dataset-card.md` for provenance, counts, integrity findings, and open
annotation/grouping gates. The category folders are not temporal onset/offset labels.

Do not record volunteers until the supervisor/ethics and consent process is approved.
Any additional source archive must remain under `data/raw/<dataset-id>/` with its
provenance and SHA-256 recorded before extraction when the archive is available.
