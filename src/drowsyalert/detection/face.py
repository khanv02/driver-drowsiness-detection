"""MediaPipe adapter. The rest of the project only sees FaceObservation."""

import urllib.request
from pathlib import Path

import cv2
import numpy as np

from drowsyalert.features.geometry import EYE_INDICES, eye_aspect_ratio
from drowsyalert.types import FaceObservation

MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/"
    "face_landmarker/face_landmarker/float16/latest/face_landmarker.task"
)


def download_model(destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        return destination
    temporary = destination.with_suffix(".download")
    try:
        with urllib.request.urlopen(MODEL_URL, timeout=60) as response:
            with temporary.open("wb") as output:
                while block := response.read(1024 * 1024):
                    output.write(block)
        if temporary.stat().st_size < 100_000:
            raise ValueError("Downloaded face model is unexpectedly small")
        temporary.replace(destination)
    finally:
        temporary.unlink(missing_ok=True)
    return destination


def observation_from_landmarks(frame: np.ndarray, points: np.ndarray) -> FaceObservation:
    if len(points) < 468 or not np.isfinite(points).all():
        return FaceObservation(False, "Invalid landmarks")
    height, width = frame.shape[:2]
    crops, boxes, ears = [], [], []
    for indices in EYE_INDICES:
        eye = points[list(indices), :2]
        if (
            eye[:, 0].min() < 0
            or eye[:, 1].min() < 0
            or eye[:, 0].max() >= width
            or eye[:, 1].max() >= height
        ):
            return FaceObservation(False, "Eye outside frame", landmarks=points)
        try:
            ears.append(eye_aspect_ratio(eye))
        except ValueError:
            return FaceObservation(False, "Invalid eye geometry", landmarks=points)
        eye_width = np.linalg.norm(eye[0] - eye[3])
        if eye_width < 8:
            return FaceObservation(False, "Eyes too small", landmarks=points)
        center = eye.mean(axis=0)
        half_w, half_h = eye_width * 0.7, eye_width * 0.45
        x1, y1 = np.maximum(0, np.floor(center - (half_w, half_h))).astype(int)
        x2, y2 = np.minimum((width, height), np.ceil(center + (half_w, half_h))).astype(int)
        crops.append(frame[y1:y2, x1:x2].copy())
        boxes.append((int(x1), int(y1), int(x2), int(y2)))
    return FaceObservation(
        True, landmarks=points, eye_crops=tuple(crops), eye_boxes=tuple(boxes), ears=tuple(ears)
    )


class FaceDetector:
    def __init__(self, model_path: Path, image_mode: bool = False):
        if not model_path.is_file():
            raise FileNotFoundError(
                f"Face model not found: {model_path}. Run drowsyalert --download-model."
            )
        import mediapipe as mp

        self.mp = mp
        mode = (
            mp.tasks.vision.RunningMode.IMAGE if image_mode else mp.tasks.vision.RunningMode.VIDEO
        )
        self.landmarker = mp.tasks.vision.FaceLandmarker.create_from_options(
            mp.tasks.vision.FaceLandmarkerOptions(
                base_options=mp.tasks.BaseOptions(model_asset_path=str(model_path)),
                running_mode=mode,
                num_faces=1,
                min_face_detection_confidence=0.5,
                min_face_presence_confidence=0.5,
                min_tracking_confidence=0.5,
            )
        )
        self.image_mode = image_mode
        self.last_ms = -1

    def detect(self, frame: np.ndarray, timestamp: float = 0) -> FaceObservation:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = self.mp.Image(image_format=self.mp.ImageFormat.SRGB, data=rgb)
        if self.image_mode:
            result = self.landmarker.detect(image)
        else:
            milliseconds = max(self.last_ms + 1, int(timestamp * 1000))
            self.last_ms = milliseconds
            result = self.landmarker.detect_for_video(image, milliseconds)
        if not result.face_landmarks:
            return FaceObservation(False, "No face")
        height, width = frame.shape[:2]
        points = np.array(
            [(p.x * width, p.y * height) for p in result.face_landmarks[0]], dtype=np.float64
        )
        return observation_from_landmarks(frame, points)

    def close(self):
        self.landmarker.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()
