"""Testable presentation text plus the OpenCV drawing adapter."""

import cv2

from drowsyalert.types import AlertState

ADVISORY_TEXT = "Research prototype - not a certified safety system"
CONTROLS_TEXT = "Q/Esc: quit | Use --mute to disable audio"


def overlay_lines(face, eyes, temporal, extra, decision, fps: float) -> list[str]:
    reason = decision.reason or eyes.reason or face.reason or str(eyes.state)
    perclos = (
        f"{temporal.perclos:.1%}"
        if temporal.ready and temporal.perclos is not None
        else ("unavailable" if temporal.ready else "warming up")
    )
    lines = [
        f"Status: {decision.state} | {reason}",
        f"Observation: {'available' if face.valid else 'unavailable'}"
        + (f" | {face.reason}" if face.reason else ""),
        f"Eye source: {eyes.source} | Eyes: {eyes.state}",
        f"Closed: {temporal.closed_seconds:.1f}s | FPS: {fps:.1f}",
        f"Estimated PERCLOS: {perclos} | coverage: {temporal.coverage:.0%}",
    ]
    if face.ears:
        ear_text = [f"{value:.3f}" if value is not None else "unknown" for value in face.ears]
        lines.append(f"EAR: {ear_text[0]} / {ear_text[1]}")
    if eyes.probabilities:
        probability_text = [
            f"{value:.2f}" if value is not None else "unknown"
            for value in eyes.probabilities
        ]
        lines.append(f"P(closed): {probability_text[0]} / {probability_text[1]}")
    if extra.mar is not None:
        lines.append(f"MAR: {extra.mar:.2f} | yawns: {extra.yawns}")
    if extra.angles is not None:
        lines.append(
            f"Relative pitch: {extra.angles[0]:.1f} | head down: {extra.head_down_seconds:.1f}s"
        )
    lines.extend((ADVISORY_TEXT, CONTROLS_TEXT))
    return lines


def draw_overlay(frame, face, eyes, temporal, extra, decision, fps):
    color = {
        AlertState.NORMAL: (40, 220, 40),
        AlertState.ALERT: (40, 40, 255),
        AlertState.UNKNOWN: (0, 200, 255),
    }[decision.state]
    if face.eye_boxes:
        for box in face.eye_boxes:
            if box is None:
                continue
            x1, y1, x2, y2 = box
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 1)

    lines = overlay_lines(face, eyes, temporal, extra, decision, fps)
    for index, text in enumerate(lines[:-2]):
        cv2.putText(
            frame,
            text,
            (10, 25 + index * 24),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            color,
            1,
            cv2.LINE_AA,
        )
    for text, y in zip(lines[-2:], (frame.shape[0] - 36, frame.shape[0] - 12), strict=True):
        cv2.putText(
            frame,
            text,
            (10, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            (240, 240, 240),
            1,
            cv2.LINE_AA,
        )
    return frame
