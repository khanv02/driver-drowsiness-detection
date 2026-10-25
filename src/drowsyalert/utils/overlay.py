import cv2

from drowsyalert.types import AlertState


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
    perclos = (
        f"{temporal.perclos:.1%}"
        if temporal.ready and temporal.perclos is not None
        else "warming up"
    )
    lines = [
        f"{decision.state}: {decision.reason or eyes.state}",
        f"Eyes: {eyes.state} | closed: {temporal.closed_seconds:.1f}s | FPS: {fps:.1f}",
        f"Estimated PERCLOS: {perclos} | coverage: {temporal.coverage:.0%}",
    ]
    if face.ears:
        ear_text = [f"{value:.3f}" if value is not None else "unknown" for value in face.ears]
        lines.append(f"EAR: {ear_text[0]} / {ear_text[1]}")
    if eyes.probabilities:
        lines.append(f"P(closed): {eyes.probabilities[0]:.2f} / {eyes.probabilities[1]:.2f}")
    if extra.mar is not None:
        lines.append(f"MAR: {extra.mar:.2f} | yawns: {extra.yawns}")
    if extra.angles is not None:
        lines.append(
            f"Relative pitch: {extra.angles[0]:.1f} | head down: {extra.head_down_seconds:.1f}s"
        )
    for index, text in enumerate(lines):
        cv2.putText(
            frame, text, (10, 25 + index * 24), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1, cv2.LINE_AA
        )
    cv2.putText(
        frame,
        "Q: quit | Reference support tool",
        (10, frame.shape[0] - 12),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45,
        (240, 240, 240),
        1,
        cv2.LINE_AA,
    )
    return frame
