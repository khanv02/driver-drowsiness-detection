"""Landmark geometry in pixel coordinates, without camera or MediaPipe dependencies."""

import numpy as np

EYE_INDICES = ((33, 160, 158, 133, 153, 144), (362, 385, 387, 263, 373, 380))


def eye_aspect_ratio(points: np.ndarray) -> float:
    points = np.asarray(points, dtype=float)
    if points.shape != (6, 2) or not np.isfinite(points).all():
        raise ValueError("EAR requires six finite 2D points")
    width = np.linalg.norm(points[0] - points[3])
    if width < 1e-6:
        raise ValueError("Degenerate eye width")
    return float(
        (np.linalg.norm(points[1] - points[5]) + np.linalg.norm(points[2] - points[4]))
        / (2 * width)
    )


def mouth_aspect_ratio(points: np.ndarray) -> float:
    width = np.linalg.norm(points[61] - points[291])
    if width < 1e-6:
        raise ValueError("Degenerate mouth width")
    heights = (np.linalg.norm(points[82] - points[87]), np.linalg.norm(points[312] - points[317]))
    return float(np.mean(heights) / width)
