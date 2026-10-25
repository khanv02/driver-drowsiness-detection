import time
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np


@dataclass
class FrameSample:
    index: int
    timestamp: float
    image: np.ndarray


class VideoSource:
    def __init__(
        self, camera: int = 0, video: Path | None = None, width: int = 640, height: int = 480
    ):
        if video is not None and not video.is_file():
            raise FileNotFoundError(f"Video not found: {video}")
        self.video = video
        self.capture = cv2.VideoCapture(str(video) if video is not None else camera)
        if not self.capture.isOpened():
            self.capture.release()
            raise RuntimeError(
                f"Cannot open {'video ' + str(video) if video else 'camera ' + str(camera)}"
            )
        if video is None:
            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        fps = self.capture.get(cv2.CAP_PROP_FPS)
        self.fps = fps if np.isfinite(fps) and fps > 0 else 30.0
        self.start = time.monotonic()
        self.index = 0
        self.last_timestamp = -1.0

    def read(self) -> FrameSample | None:
        ok, frame = self.capture.read()
        if not ok:
            if self.video is None:
                raise RuntimeError("Camera stopped delivering frames")
            return None
        if self.video is None:
            timestamp = time.monotonic() - self.start
        else:
            # Decoder timestamp first, FPS timeline only when timestamps are unavailable.
            timestamp = self.capture.get(cv2.CAP_PROP_POS_MSEC) / 1000
            if not np.isfinite(timestamp) or timestamp <= self.last_timestamp:
                timestamp = max(self.index / self.fps, self.last_timestamp + 1 / self.fps)
        self.last_timestamp = timestamp
        sample = FrameSample(self.index, timestamp, frame)
        self.index += 1
        return sample

    def close(self):
        self.capture.release()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()
