import json

import pytest

from drowsyalert.main import main


def test_cli_forwards_live_controls_and_prints_run_metadata(monkeypatch, capsys, tmp_path):
    import drowsyalert.pipeline.realtime as realtime

    captured = {}

    def fake_run(config, **kwargs):
        captured["config"] = config
        captured.update(kwargs)
        return {
            "frames": 1,
            "input_kind": "live_monotonic",
            "eye_source": "cnn_eye_classifier",
            "checkpoint_sha256": "a" * 64,
            "audio": {
                "policy": "muted",
                "enabled": False,
                "available": True,
                "play_count": 0,
                "failure_count": 0,
            },
        }

    monkeypatch.setattr(realtime, "run", fake_run)
    checkpoint = tmp_path / "eye.pt"
    result = main(
        [
            "--camera",
            "1",
            "--eye-backend",
            "cnn",
            "--checkpoint",
            str(checkpoint),
            "--headless",
            "--mute",
            "--max-frames",
            "1",
            "--record",
            str(tmp_path / "run.json"),
            "--dataset-id",
            "demo-v1",
            "--split-id",
            "validation-v1",
            "--seed",
            "42",
            "--code-revision",
            "abc123",
        ]
    )

    printed = json.loads(capsys.readouterr().out)
    assert result == 0
    assert captured["camera"] == 1
    assert captured["backend"] == "cnn"
    assert captured["headless"] is True
    assert captured["mute"] is True
    assert captured["max_frames"] == 1
    assert captured["record_path"] == tmp_path / "run.json"
    assert captured["dataset_id"] == "demo-v1"
    assert captured["split_id"] == "validation-v1"
    assert captured["random_seed"] == 42
    assert captured["code_revision"] == "abc123"
    assert captured["config"].checkpoint == str(checkpoint)
    assert printed["eye_source"] == "cnn_eye_classifier"
    assert printed["audio"]["policy"] == "muted"


@pytest.mark.parametrize(
    "arguments",
    [
        ["--camera", "-1"],
        ["--max-frames", "0"],
    ],
)
def test_cli_rejects_invalid_live_arguments(arguments):
    with pytest.raises(SystemExit):
        main(arguments)
