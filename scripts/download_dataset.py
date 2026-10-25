"""Record a manually downloaded CEW archive without fetching or extracting it.

The historical script downloaded an archive whose Kaggle metadata reported an unknown
license. Phase 3 deliberately requires an owner-mediated download from the official CEW
page instead. This command is read-only and records the local archive identity needed for
the dataset card.
"""

import argparse
import hashlib
import json
from pathlib import Path

CEW_PAGE = (
    "https://parnec.nuaa.edu.cn/_upload/tpl/02/db/731/template731/"
    "pages/xtan/ClosedEyeDatabases.html"
)


def archive_identity(path: Path) -> dict[str, str | int]:
    if not path.is_file():
        raise FileNotFoundError(f"Dataset archive not found: {path}")
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as source:
        while block := source.read(1024 * 1024):
            size += len(block)
            digest.update(block)
    return {
        "archive": path.name,
        "bytes": size,
        "sha256": digest.hexdigest(),
        "source_page": CEW_PAGE,
        "action": "Record this identity in docs/dataset-card.md; extract under data/raw/cew/.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Hash an owner-downloaded CEW archive (no network or extraction)"
    )
    parser.add_argument("--archive", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(archive_identity(args.archive), indent=2))


if __name__ == "__main__":
    main()
