from pathlib import Path

import numpy as np
import pytest

from drowsyalert.pipeline import source as source_module
from drowsyalert.pipeline.source import VideoSource


class FakeCapture:
    def __init__(self, reads=(), *, opened=True, fps=25.0, media_ms=()):
        self.reads = list(reads)
        self.opened = opened
        self.fps = fps
        self.media_ms = list(media_ms)
        self.read_index = 0
        self.released = False
        self.settings = []

    def isOpened(self):
        return self.opened

    def read(self):
        if self.read_index >= len(self.reads):
            return False, None
        result = self.reads[self.read_index]
        self.read_index += 1
        return result

    def get(self, key):
        if key == source_module.cv2.CAP_PROP_FPS:
            return self.fps
        if key == source_module.cv2.CAP_PROP_POS_MSEC:
            index = max(0, self.read_index - 1)
            return self.media_ms[index] if index < len(self.media_ms) else float("nan")
        return 0.0

    def set(self, key, value):
        self.settings.append((key, value))
        return True

    def release(self):
        self.released = True


def install_capture(monkeypatch, capture):
    monkeypatch.setattr(source_module.cv2, "VideoCapture", lambda *_: capture)


def test_open_failure_releases_capture(monkeypatch):
    capture = FakeCapture(opened=False)
    install_capture(monkeypatch, capture)

    with pytest.raises(RuntimeError, match="Cannot open camera 0"):
        VideoSource(camera=0)

    assert capture.released


def test_recorded_video_uses_media_time_and_falls_back_monotonically(monkeypatch, tmp_path):
    video = tmp_path / "fixture.mp4"
    video.touch()
    frame = np.zeros((4, 5, 3), dtype=np.uint8)
    capture = FakeCapture(
        [(True, frame), (True, frame), (True, frame), (False, None)],
        fps=25.0,
        media_ms=(0.0, 40.0, 40.0),
    )
    install_capture(monkeypatch, capture)

    with VideoSource(video=video) as source:
        samples = [source.read(), source.read(), source.read()]
        assert source.read() is None

    assert [sample.index for sample in samples] == [0, 1, 2]
    assert [sample.timestamp for sample in samples] == pytest.approx([0.0, 0.04, 0.08])
    assert {sample.source_kind for sample in samples} == {"video_media"}
    assert capture.released


def test_live_camera_uses_monotonic_time_and_failure_is_not_eof(monkeypatch):
    frame = np.zeros((4, 5, 3), dtype=np.uint8)
    capture = FakeCapture([(True, frame), (False, None)])
    install_capture(monkeypatch, capture)
    times = iter((100.0, 100.1))
    monkeypatch.setattr(source_module.time, "monotonic", lambda: next(times))

    with VideoSource(camera=2, width=320, height=240) as source:
        sample = source.read()
        with pytest.raises(RuntimeError, match="Camera stopped delivering frames"):
            source.read()

    assert sample.timestamp == pytest.approx(0.1)
    assert sample.source_kind == "live_monotonic"
    assert capture.settings == [
        (source_module.cv2.CAP_PROP_FRAME_WIDTH, 320),
        (source_module.cv2.CAP_PROP_FRAME_HEIGHT, 240),
    ]
    assert capture.released


def test_missing_recorded_video_is_rejected_before_capture(monkeypatch, tmp_path):
    called = False

    def unexpected_capture(*_):
        nonlocal called
        called = True
        return FakeCapture()

    monkeypatch.setattr(source_module.cv2, "VideoCapture", unexpected_capture)
    with pytest.raises(FileNotFoundError):
        VideoSource(video=Path(tmp_path / "missing.mp4"))
    assert not called
