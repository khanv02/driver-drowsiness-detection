import pytest

from drowsyalert.main import main
from drowsyalert.utils.config import load_config


@pytest.mark.parametrize(
    "text",
    [
        "unexpected: 1",
        "window_seconds: -1",
        "min_coverage: 2",
        "width: 1.5",
        "- not a mapping",
        "max_gap_seconds: .nan",
        "cnn_threshold: 0.5\ncnn_uncertainty_margin: 0.6",
    ],
)
def test_config_rejects_invalid_values(tmp_path, text):
    path = tmp_path / "bad.yaml"
    path.write_text(text)
    with pytest.raises((ValueError, TypeError)):
        load_config(path)


def test_missing_custom_config_is_error(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_config(tmp_path / "missing.yaml")


def test_missing_checkpoint_does_not_fall_back(tmp_path):
    assert (
        main(
            [
                "--eye-backend",
                "cnn",
                "--checkpoint",
                str(tmp_path / "missing.pt"),
                "--headless",
                "--max-frames",
                "1",
            ]
        )
        == 1
    )
