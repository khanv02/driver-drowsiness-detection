# Research: DrowsyAlert Plan Decisions

## Decision: Retain the Python toolchain and dependencies

**Decision**: Keep Python as declared (`>=3.12,<3.15`), `uv`, OpenCV, MediaPipe, NumPy, PyYAML and optional PyTorch. Use the `train` extra for Pillow, scikit-learn and plotting. Do not add TensorFlow or dlib.

**Rationale**: These tools are already declared/used, satisfy the instructor's options, and avoid duplicate frameworks. Python 3.12+ exceeds the stated >=3.9 floor but does not promise 3.9 compatibility.

**Alternatives considered**: TensorFlow/Keras and dlib are valid, but add setup and maintenance without a requirement to switch.

## Decision: Use MediaPipe Face Landmarker with video timestamps

**Decision**: Keep local MediaPipe Face Landmarker; provide monotonically increasing timestamps in video mode. Begin with a synchronous sequential adapter; consider async live stream only if measured latency warrants it.

**Rationale**: The official API requires timestamps for video calls; live-stream callbacks can omit frames under load. Sequential processing simplifies temporal reasoning. Missing observations remain unknown.

**Alternatives considered**: dlib is named in the instructor brief but absent; it adds setup/model management. Async mode may reduce latency but complicates dropped-frame accounting.

**Source**: [MediaPipe FaceLandmarker Python API](https://ai.google.dev/edge/api/mediapipe/python/mp/tasks/vision/FaceLandmarker).

## Decision: Treat EAR as a landmark-derived proxy and integrate temporal intervals

**Decision**: Use 2D EAR as eye-openness proxy with validation-selected thresholds; compute PERCLOS from valid timestamp intervals and report coverage/unknown.

**Rationale**: EAR is lightweight and testable but can be noisy and is not direct eyelid-occlusion measurement. Duration weighting avoids frame-rate assumptions. Call it landmark-derived PERCLOS (EAR proxy).

**Alternatives considered**: Frame counts vary with frame rate/dropped observations. CNN-derived temporal scores are a secondary ablation and do not answer the landmark-focused question.

**Sources**: [Soukupová and Čech, Eye Blink Detection Using Facial Landmarks](https://cmp.felk.cvut.cz/ftp/articles/cech/Soukupova-CVWW-2016.pdf); [PERCLOS review](https://pmc.ncbi.nlm.nih.gov/articles/PMC10108649/).

## Decision: Retain the small PyTorch CNN with metadata

**Decision**: Start with existing `EyeCNN`, identical train/inference crop processing, per-eye output, validation-only checkpoint selection, and metadata for architecture, labels, preprocessing, data and configuration.

**Rationale**: The model is small and Torch is an optional dependency. CNN remains separately evaluated from landmark evidence. Record seeds/environment; do not promise bitwise identity across hardware.

**Alternatives considered**: A larger pretrained network or second framework adds compute and maintenance without SPEC need.

**Sources**: [PyTorch saving/loading](https://docs.pytorch.org/tutorials/beginner/saving_loading_models.html); [PyTorch reproducibility](https://docs.pytorch.org/docs/stable/notes/randomness.html); [PyTorch DataLoader](https://docs.pytorch.org/docs/main/data.html).

## Decision: Compare methods on shared replay and labels

**Decision**: Run A/B/C over identical held-out clips, labels, timestamps, base PERCLOS and one-to-one matching. Report event precision/recall/F1, misses, false alarms per time, coverage and latency; report eye-image classification separately.

**Rationale**: Frame accuracy does not describe event detection or warning delay. Matching reference/output events and reporting misses/false alarms is established evaluation practice.

**Alternatives considered**: Live GUI demonstration is not a repeatable held-out comparison; counting alert frames as independent detections inflates results.

**Sources**: [NIST ActEV evaluation report](https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=934669); [NIST ActEV evaluation plan](https://actev.nist.gov/pub/Draft_ActEV_2018_EvaluationPlan.pdf).

## Unresolved project decisions

No authoritative Kaggle URL/version, license, subject metadata, temporal labels, event matching tolerance, or system Accuracy unit is established. Current downloader URL is only a candidate. Verify suitability and record decisions before dependent training/evaluation. Image-only data cannot support event latency/recall; any new volunteer data follows SPEC consent requirements.
