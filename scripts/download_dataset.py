"""Download the selected public Kaggle archive; credentials are never embedded."""

import argparse
import urllib.request
import zipfile
from pathlib import Path

URL = "https://www.kaggle.com/api/v1/datasets/download/dheerajperumandla/drowsiness-dataset"


def main():
    parser = argparse.ArgumentParser(description="Download public Kaggle eye/yawn images")
    parser.add_argument("--output", type=Path, default=Path("data/raw/kaggle"))
    args = parser.parse_args()
    destination = args.output.resolve()
    destination.mkdir(parents=True, exist_ok=True)
    archive = destination / "dataset.zip"
    request = urllib.request.Request(URL, headers={"User-Agent": "DrowsyAlert/0.2"})
    with urllib.request.urlopen(request, timeout=60) as response, archive.open("wb") as target:
        while block := response.read(1024 * 1024):
            target.write(block)
    if not zipfile.is_zipfile(archive):
        raise RuntimeError("Kaggle did not return a ZIP. Download manually from the dataset page.")
    with zipfile.ZipFile(archive) as zipped:
        for member in zipped.infolist():
            target = (destination / member.filename).resolve()
            if not target.is_relative_to(destination):
                raise ValueError("Archive contains a path outside the dataset directory")
        zipped.extractall(destination)
    print(destination)


if __name__ == "__main__":
    main()
