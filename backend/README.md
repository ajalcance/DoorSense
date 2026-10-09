# DoorSense backend

Python 3.12, FastAPI and Uvicorn provide a loopback service for live camera
analysis, one parent-enrolled family reference, local storage and UI hosting.

## Current pipeline

- `camera.py`: bounded webcam capture and JPEG frames.
- `vision.py` / `scene.py`: local EfficientDet person detection and Face Landmarker
  availability/localization. Face analysis is enabled in the current demo.
- `recognition.py`: OpenCV LBPH training on the parent-labeled grayscale crop and
  fresh-frame comparison. Distance <=65 is accepted; lower is closer. Decisions
  use the same two-decimal value displayed in the console.
- `store.py`: local SQLite reference/sample and preserved historical event/media data.
- `console.py`: lifecycle, protected local enrollment APIs, freshness checks,
  parent guidance mode and production UI/API hosting.
- `local_llm.py`: bounded Qwen3 0.6B fact selection through local Ollama. Text only;
  validated selections preserve supplied wording, with explicit unavailable fallback.
- `events.py`: earlier event engine retained for historical compatibility/tests.
  It does not drive face-only production alerts.

Only Family member and Unknown are visitor categories. Exactly one person and
usable fresh face analysis are required for enrollment/matching. Deleting the
reference invalidates pending comparisons. Stop/reset disable Child safety mode
but preserve enrollment. Production sensor/manual-category endpoints return 410;
the parent-mode endpoint controls guidance, not the legacy event engine.

## Startup and checks

Use the pinned `requirements.lock` after [preparation](../docs/PREPARATION.md).
From the repository root:

```sh
.venv/bin/python scripts/console.py
.venv/bin/python scripts/audit.py
```

Run the audit separately from startup. It never starts the service/camera.
The service binds `127.0.0.1:8765`; camera capture begins only after Start.
No model is downloaded at runtime. Models, SQLite, images and reports are ignored.

LBPH enrollment is supervised appearance learning, not RL, autonomous identity
learning or intent classification. See the
[technical overview](../docs/TECHNICAL_OVERVIEW.md) for exact versions, current
source/live evidence and remaining acceptance limits.
