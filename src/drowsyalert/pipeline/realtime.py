"""Composition root for camera/video, interchangeable eye backends and presentation."""

import csv
import logging
import time
from dataclasses import asdict
from pathlib import Path

import cv2

from drowsyalert.detection.face import FaceDetector
from drowsyalert.experiments.records import (
    FRAME_FIELDS,
    build_run_record,
    file_sha256,
    finalize_run_record,
    write_run_record,
)
from drowsyalert.features.extra import ExtraTracker
from drowsyalert.features.temporal import TemporalTracker
from drowsyalert.models.ear import EARBackend
from drowsyalert.pipeline.alerts import AlertManager
from drowsyalert.pipeline.decision import DecisionEngine, method_metadata
from drowsyalert.pipeline.source import VideoSource
from drowsyalert.types import AlertState
from drowsyalert.utils.config import Config
from drowsyalert.utils.overlay import draw_overlay

LOGGER = logging.getLogger(__name__)
LOG_FIELDS = FRAME_FIELDS


def run(
    config: Config,
    *,
    camera: int = 0,
    video: Path | None = None,
    backend: str = "ear",
    method: str = "perclos",
    headless: bool = False,
    max_frames: int | None = None,
    log_path: Path | None = None,
    record_path: Path | None = None,
    dataset_id: str | None = None,
    split_id: str | None = None,
    random_seed: int | None = None,
    code_revision: str | None = None,
    mute: bool = False,
):
    predictor = EARBackend(config.ear_threshold)
    eye_source = "landmark_ear"
    eye_threshold = config.ear_threshold
    eye_uncertainty_margin = None
    checkpoint_sha256 = None
    if backend == "cnn":
        from drowsyalert.models.eye_cnn import CNNBackend

        predictor = CNNBackend(
            config.resource(config.checkpoint),
            config.cnn_threshold,
            config.cnn_uncertainty_margin,
        )
        eye_source = predictor.source
        eye_threshold = predictor.threshold
        eye_uncertainty_margin = predictor.uncertainty_margin
        checkpoint_sha256 = predictor.checkpoint_sha256
    tracker = TemporalTracker(
        config.window_seconds,
        config.min_valid_seconds,
        config.min_coverage,
        config.max_gap_seconds,
        source=eye_source,
    )
    extra_tracker = ExtraTracker(config, method)
    engine = DecisionEngine(config, method)
    resolved_method = method_metadata(config, method, eye_source)
    # Video replay uses video time for features but is silent unless used live.
    audio = AlertManager(config.cooldown_seconds, enabled=not mute and video is None)
    source_kind = "video_media" if video is not None else "live_monotonic"
    source_hash = file_sha256(video) if video is not None else None
    source_id = f"video:{source_hash[:16]}" if source_hash else f"camera:{camera}"
    record = build_run_record(
        source_id=source_id,
        source_kind=source_kind,
        source_sha256=source_hash,
        method=resolved_method,
        resolved_config=asdict(config),
        model={
            "eye_source": eye_source,
            "eye_threshold": eye_threshold,
            "eye_uncertainty_margin": eye_uncertainty_margin,
            "checkpoint_sha256": checkpoint_sha256,
            "face_model": Path(config.face_model).name,
        },
        audio={
            "enabled": not mute and video is None,
            "policy": "muted" if mute else ("replay_silent" if video is not None else "live"),
        },
        dataset_id=dataset_id,
        split_id=split_id,
        random_seed=random_seed,
        code_revision=code_revision,
    )
    log_file, writer, frame_count = None, None, 0
    record_frames = []
    caught_error = None
    audio_metadata = None
    started = time.perf_counter()
    try:
        if log_path:
            log_path.parent.mkdir(parents=True, exist_ok=True)
            log_file = log_path.open("w", encoding="utf-8", newline="")
            writer = csv.DictWriter(log_file, LOG_FIELDS)
            writer.writeheader()
        with FaceDetector(config.resource(config.face_model)) as detector:
            with VideoSource(camera, video, config.width, config.height) as source:
                while max_frames is None or frame_count < max_frames:
                    sample = source.read()
                    if sample is None:
                        break
                    frame_start = time.perf_counter()
                    face = detector.detect(sample.image, sample.timestamp)
                    eyes = predictor.predict(face)
                    temporal = tracker.update(sample.timestamp, eyes.state)
                    height, width = sample.image.shape[:2]
                    extra = extra_tracker.update(face, sample.timestamp, width, height)
                    decision = engine.decide(eyes.state, temporal, extra)
                    played = audio.update(decision.state, time.monotonic())
                    elapsed = time.perf_counter() - frame_start
                    fps = 1 / elapsed if elapsed else 0.0
                    if writer or record_path:
                        row = dict(
                            frame=sample.index,
                            timestamp=sample.timestamp,
                            input_kind=sample.source_kind,
                            method=method,
                            method_id=resolved_method["method_id"],
                            auxiliary_cue=resolved_method["auxiliary_cue"],
                            eye_source=eyes.source,
                            eye_threshold=eye_threshold,
                            eye_uncertainty_margin=eye_uncertainty_margin,
                            checkpoint_sha256=checkpoint_sha256,
                            valid=face.valid,
                            observation_reason=face.reason,
                            eye_state=eyes.state,
                            eye_reason=eyes.reason,
                            closed_seconds=temporal.closed_seconds,
                            perclos=temporal.perclos,
                            coverage=temporal.coverage,
                            valid_seconds=temporal.valid_seconds,
                            ready=temporal.ready,
                            window_seconds=temporal.window_seconds,
                            window_start=temporal.window_start,
                            window_end=temporal.window_end,
                            yawns=extra.yawns,
                            mar=extra.mar,
                            yawn_valid=extra.yawn_valid,
                            yawn_event=extra.yawn_event,
                            yawn_active_seconds=extra.yawn_active_seconds,
                            yawn_reason=extra.yawn_reason,
                            pitch=extra.angles[0] if extra.angles else None,
                            head_down_seconds=extra.head_down_seconds,
                            head_down=extra.head_down,
                            head_pose_valid=extra.head_pose_valid,
                            pose_reference_pitch=extra.pose_reference_pitch,
                            head_pose_reason=extra.head_pose_reason,
                            state=decision.state,
                            reason=decision.reason,
                            processing_ms=elapsed * 1000,
                        )
                        for prefix, values in (
                            ("ear", face.ears),
                            ("p_closed", eyes.probabilities),
                        ):
                            for side, value in zip(("left", "right"), values or (None, None)):
                                row[f"{prefix}_{side}"] = value
                        if writer:
                            writer.writerow(row)
                        if record_path:
                            record_frames.append(row)
                    if played or (decision.state == AlertState.ALERT and frame_count == 0):
                        LOGGER.info("Alert: %s", decision.reason)
                    if not headless:
                        cv2.imshow(
                            "DrowsyAlert",
                            draw_overlay(sample.image, face, eyes, temporal, extra, decision, fps),
                        )
                        delay = max(1, int(1000 / source.fps - elapsed * 1000)) if video else 1
                        if cv2.waitKey(delay) & 0xFF in (ord("q"), ord("Q"), 27):
                            break
                        if cv2.getWindowProperty("DrowsyAlert", cv2.WND_PROP_VISIBLE) < 1:
                            break
                    frame_count += 1
    except BaseException as error:
        caught_error = f"{type(error).__name__}: {error}"
        raise
    finally:
        audio.close()
        audio_metadata = audio.metadata()
        audio_metadata["policy"] = (
            "muted" if mute else ("replay_silent" if video is not None else "live")
        )
        if log_file:
            log_file.close()
        if not headless:
            cv2.destroyAllWindows()
        if record_path:
            elapsed_seconds = time.perf_counter() - started
            final_record = finalize_run_record(
                record,
                record_frames,
                status="error" if caught_error else "completed",
                wall_seconds=elapsed_seconds,
                audio=audio_metadata,
                error=caught_error,
            )
            try:
                write_run_record(record_path, final_record)
            except OSError:
                if caught_error is None:
                    raise
                LOGGER.exception("Could not write failed-run record to %s", record_path)
    seconds = time.perf_counter() - started
    return {
        "frames": frame_count,
        "wall_seconds": seconds,
        "fps": frame_count / seconds if seconds else 0,
        "input_kind": source_kind,
        "eye_source": eye_source,
        "eye_threshold": eye_threshold,
        "eye_uncertainty_margin": eye_uncertainty_margin,
        "checkpoint_sha256": checkpoint_sha256,
        "method": method,
        "method_metadata": resolved_method,
        "run_id": record["run_id"],
        "provenance_complete": record["provenance_complete"],
        "missing_provenance": record["missing_provenance"],
        "record_path": str(record_path) if record_path else None,
        "audio": audio_metadata,
        "config": asdict(config),
    }
