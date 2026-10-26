import csv

import numpy as np

from drowsyalert.pipeline import realtime
from drowsyalert.pipeline.source import FrameSample
from drowsyalert.types import EyeObservation, EyeState, FaceObservation
from drowsyalert.utils.config import Config


class FakeSource:
    source_kind = "video_media"
    fps = 10.0

    def __init__(self, *_args, **_kwargs):
        frame = np.zeros((20, 20, 3), dtype=np.uint8)
        self.samples = iter(
            [
                FrameSample(0, 0.0, frame.copy(), self.source_kind),
                FrameSample(1, 0.1, frame.copy(), self.source_kind),
                FrameSample(2, 0.2, frame.copy(), self.source_kind),
            ]
        )

    def read(self):
        return next(self.samples, None)

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return None


class FakeDetector:
    def __init__(self, *_args, **_kwargs):
        self.observations = iter(
            [
                FaceObservation(True, ears=(0.30, 0.31), eye_valid=(True, True)),
                FaceObservation(False, "No face"),
                FaceObservation(True, ears=(0.10, 0.11), eye_valid=(True, True)),
            ]
        )

    def detect(self, _frame, _timestamp):
        return next(self.observations)

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return None


class FakeAlert:
    instances = []

    def __init__(self, _cooldown, *, enabled):
        self.enabled = enabled
        self.closed = False
        self.instances.append(self)

    def update(self, *_):
        return False

    def close(self):
        self.closed = True


def test_headless_replay_records_source_unknown_and_temporal_metadata(monkeypatch, tmp_path):
    monkeypatch.setattr(realtime, "VideoSource", FakeSource)
    monkeypatch.setattr(realtime, "FaceDetector", FakeDetector)
    monkeypatch.setattr(realtime, "AlertManager", FakeAlert)
    log_path = tmp_path / "replay.csv"
    video = tmp_path / "fixture.mp4"
    video.touch()
    config = Config(window_seconds=1.0, min_valid_seconds=0.1, min_coverage=0.5)

    result = realtime.run(config, video=video, headless=True, log_path=log_path)

    with log_path.open(newline="", encoding="utf-8") as source:
        rows = list(csv.DictReader(source))
    assert result["frames"] == 3
    assert result["input_kind"] == "video_media"
    assert result["eye_source"] == "landmark_ear"
    assert result["eye_threshold"] == config.ear_threshold
    assert result["eye_uncertainty_margin"] is None
    assert result["checkpoint_sha256"] is None
    assert result["method"] == "perclos"
    assert [row["timestamp"] for row in rows] == ["0.0", "0.1", "0.2"]
    assert {row["input_kind"] for row in rows} == {"video_media"}
    assert {row["eye_source"] for row in rows} == {"landmark_ear"}
    assert {row["eye_threshold"] for row in rows} == {str(config.ear_threshold)}
    assert {row["checkpoint_sha256"] for row in rows} == {""}
    assert {row["window_seconds"] for row in rows} == {"1.0"}
    assert rows[1]["eye_state"] == "UNKNOWN"
    assert rows[1]["observation_reason"] == "No face"
    assert rows[1]["state"] == "UNKNOWN"
    assert rows[2]["valid_seconds"] == "0.0"
    assert FakeAlert.instances[-1].enabled is False
    assert FakeAlert.instances[-1].closed


def test_cnn_runtime_records_checkpoint_and_confidence_policy(monkeypatch, tmp_path):
    import drowsyalert.models.eye_cnn as eye_cnn

    class FakeCNN:
        source = "cnn_eye_classifier"

        def __init__(self, checkpoint, threshold, uncertainty_margin):
            self.threshold = threshold
            self.uncertainty_margin = uncertainty_margin
            self.checkpoint_sha256 = "c" * 64

        def predict(self, observation):
            return EyeObservation(
                EyeState.CLOSED,
                probabilities=(0.9, 0.8),
                source=self.source,
            )

    monkeypatch.setattr(realtime, "VideoSource", FakeSource)
    monkeypatch.setattr(realtime, "FaceDetector", FakeDetector)
    monkeypatch.setattr(realtime, "AlertManager", FakeAlert)
    monkeypatch.setattr(eye_cnn, "CNNBackend", FakeCNN)
    log_path = tmp_path / "cnn.csv"
    video = tmp_path / "fixture.mp4"
    video.touch()
    config = Config(window_seconds=1.0, min_valid_seconds=0.1, min_coverage=0.5)

    result = realtime.run(
        config,
        video=video,
        backend="cnn",
        headless=True,
        log_path=log_path,
    )

    with log_path.open(newline="", encoding="utf-8") as source:
        rows = list(csv.DictReader(source))
    assert result["eye_source"] == "cnn_eye_classifier"
    assert result["checkpoint_sha256"] == "c" * 64
    assert result["eye_threshold"] == config.cnn_threshold
    assert result["eye_uncertainty_margin"] == config.cnn_uncertainty_margin
    assert {row["eye_source"] for row in rows} == {"cnn_eye_classifier"}
    assert {row["checkpoint_sha256"] for row in rows} == {"c" * 64}
    assert {row["eye_uncertainty_margin"] for row in rows} == {
        str(config.cnn_uncertainty_margin)
    }
