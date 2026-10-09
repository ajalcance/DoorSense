# Slice 3: real webcam and person-detection spike

Status: Slice 3 basic camera/detection checkpoint complete. Nine fake-camera
lifecycle/expiry/threading checks passed; genuine owner webcam inference and
entry/exit, physical pause and restart behavior are confirmed. Broader detection
quality, live failure handling and offline restart remain later acceptance checks.

The model-only check in the Codex command sandbox was blocked because MediaPipe
could not create an NSOpenGL pixel format, even with its CPU delegate selected.
No camera was opened by Codex. The owner Terminal check passed: load 145.16 ms,
warm blank-pixel calls 14.76-15.22 ms, peak RSS 157.3 MB. These are blank-input
compatibility figures.

An initial permission request failed because device opening ran in a worker.
Startup was corrected to use the main UI thread; capture reads remain in the
worker. The corrected owner run captured 156 frames and analysed 46, all with a
person result, over 10.93 active seconds: measured inference rate 4.21/s, median
34.06 ms, P95 36.37 ms and peak process RSS 339.8 MB (excludes Ollama). Release
completed and no errors were reported. The saved aggregate report matches these
measurements. The owner separately confirmed boxes disappeared on leaving the
view, P turned off the camera light, and S restored the live preview. Aggregate
counts alone do not measure empty-scene accuracy or missed/false detections.

## Start in Terminal

Keep the existing foreground Ollama Terminal running. Use the other Terminal:

```sh
cd "/Users/anymind/Documents/ChatGPT/Albert Space 2/Hackathon/DoorSense" &&
.venv/bin/python scripts/camera_spike.py --self-check &&
.venv/bin/python scripts/camera_spike.py
```

The first command makes four genuine detector calls on explicitly synthetic
blank pixels. It checks task/model compatibility without opening a camera or
window. It does not prove person-detection quality. If it fails, the preview
does not launch: report the first error, without installing more packages.

The second command opens a native development preview with the camera **off**.
Focus that window and use:

| Key | Effect |
| --- | --- |
| S | Start the real webcam; allow the macOS camera prompt for the named app |
| P | Pause, clear preview/results and release the device |
| S after P | Start a new capture session with new frame identities |
| Q or Escape | Stop, release the device, close the preview and print diagnostics |

The camera light should turn on when capture starts and turn off after pause or
quit, provided no other app is using it. If permission is denied, enable the
app named in System Settings > Privacy & Security > Camera and relaunch this
command. Codex need not appear in that list. No Codex restart or permission-profile
change is required. For another attached camera, use `--camera 1` explicitly.

## What this spike implements

- Real OpenCV/AVFoundation input; no video replay or scripted detections.
- Explicit S starts/opens the camera on the main UI thread so the first macOS
  permission request can run; subsequent frame reads use the bounded worker.
- One replaceable latest frame, with monotonic acquisition time, UTC timestamp,
  sequence and `laptop_webcam` provenance. Frames do not accumulate in a queue.
- Exact-hash local EfficientDet-Lite0 int8 model, MediaPipe 0.10.21, CPU delegate,
  person category only, maximum five results and score threshold 0.45. The threshold
  is a prototype setting, not a calibrated reliability or danger probability.
- Capture requested at 640x480/15 FPS; actual hardware may choose another mode.
  Inference is capped at five calls/second by default with no catch-up backlog.
  `--inference-hz 2` reduces the cap. Capture runs independently; synchronous
  model calls can briefly delay preview controls while a call is executing.
- Boxes stay attached to the exact analysed frame. Frames older than 0.8 seconds,
  camera failures and paused sessions hide the image and detections. No stale
  visitor observations are copied to a newer frame.
- Capture/inference UTC timestamps, frame age, person count, model scores,
  bounded-window median/P95 timing, measured rate and peak process RSS. RSS
  includes imports but excludes the separate Ollama process. It is not combined
  pipeline memory or a claim of real-world performance.
- Visible camera/model failures, release completion checks, pause/restart and quit.
  No severity engine, face analysis, personal identity, intent or LLM call exists.

This native preview is the development spike. It is not the planned resident
React console, which remains a separate UI checkpoint.

## Media and diagnostics

No images, clips or per-frame observations are written to disk. Only local
aggregate diagnostics are saved under ignored `.runtime/`:

- `vision-self-check.json`: model-only blank-pixel result, timings and peak RSS;
  failed checks explicitly record Blocked.
- `vision-session.json`: captured/inferred counts, aggregate person-frame count,
  timing samples summary (at most 300), peak RSS, errors and release result.

These reports do not replace owner acceptance. Model hashes are in the tracked
[runtime manifest](../assets/runtime-manifest.json). Asset-specific vision licence
confirmation and external-network behaviour remain separate unresolved checks;
weights are not redistributed.

## Owner acceptance, in order

1. Confirm the model-only check passes and the preview opens with the camera off.
2. Press S, permit the named app, and confirm fresh webcam imagery and increasing
   frame sequence/timestamps. Describe the actual camera framing.
3. Enter/leave the view several times; confirm the boxes follow newly observed
   people and disappear on fresh empty frames. Record misses/false detections.
   Full-body visibility and lighting matter; absence of a box is not proof of absence.
4. Press P and confirm the preview clears and camera light turns off. Press S again
   and confirm fresh capture resumes; quit with Q and confirm release.
5. Report the final diagnostics plus observed behaviour. Exercise denied permission
   or unavailable camera separately before marking failure handling accepted.

Do not mark Slice 3 live acceptance Passed from fake-camera tests or a blank-image
model call. Offline restart, external requests, combined memory and detection
quality across varied scenarios remain later acceptance checkpoints.

Reference: [MediaPipe Python Object Detector](https://developers.google.com/edge/mediapipe/solutions/vision/object_detector/python).
