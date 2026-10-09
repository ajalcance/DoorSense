# DoorSense technical overview

Current face-recognition demo, verified against source and the saved audit on
2026-10-10, Asia/Manila. This is the current technical description; older sensor
simulation and manual visitor-label documents describe earlier iterations.

## What works now

DoorSense runs a local camera-to-analysis pipeline for child-facing doorway
guidance. The current demo supports one parent-enrolled family reference and
only two visitor categories: **Family member** and **Unknown**.

- Camera and person detection: explicit Start/Stop controls, live camera images,
  person detection boxes and detector scores. Owner screenshots confirm genuine
  camera/person inference.
- Family enrollment: a parent saves one captured face, previews it and can
  delete it. Save/preview are shown in owner screenshots; persistence and deletion
  pass temporary SQLite and API tests.
- Local appearance recognition: LBPH learns the labeled example and compares
  later clear faces. An owner screenshot shows a Family member result at distance
  53.70, below threshold 65; earlier screenshots show rejected comparisons.
- Child safety mode: parents enable or disable child guidance while recognition
  continues. Source/API tests pass; the final live toggle trial remains pending.
- Camera banners and AI Analysis: the live verdict, recommendation, comparison
  reason and learning summary appear in one automatic view. Production build and
  static rendering pass; the final owner browser trial remains pending.
- Automatic text-model findings: fresh evidence triggers bounded local Qwen
  requests. Camera analysis continues when text inference is unavailable. Earlier
  genuine Qwen runs are recorded; the new automatic flow passes injected-request
  tests, with live acceptance pending.
- Local storage and freshness: enrollment survives Stop/reset/restart. Deletion
  clears the reference/model, and stale frames cannot retain a current match.
  Automated storage, API, stale-result and in-flight deletion checks pass.

Sensors, knocking, contact transitions and occupancy rules do not drive this
demo. Sensor and manual visitor-selection endpoints reject requests in normal
operation. Earlier event history is preserved separately.

## Technology stack

- Interface: React 19.3.0, Vite 8.3.4, JavaScript/JSX and CSS power the local
  browser console, camera banners, parent controls and unified analysis.
- Application service: Python 3.12, FastAPI 0.143.0 and Uvicorn 0.54.0 provide
  the local HTTP service, camera lifecycle, enrollment/control APIs and UI hosting.
- Camera and image processing: OpenCV contrib 4.11.0.86 and NumPy 1.26.4 handle
  webcam capture, JPEG encoding, grayscale face preparation and matching.
- Person detection: EfficientDet-Lite0 int8 v1 runs through MediaPipe 0.10.21
  to detect people in sampled camera frames.
- Face localization: MediaPipe Face Landmarker float16 v1 checks face
  availability and provides landmarks used to bound the face crop.
- Supervised appearance matching: OpenCV LBPH Face Recognizer learns local
  texture histograms from the parent-labeled reference and predicts a match distance.
- Local language inference: Qwen3 0.6B through Ollama 0.40.1 selects supporting
  facts from supplied observations. It receives text, not images.
- Persistence: SQLite stores the enrolled reference/sample locally and retains
  earlier event/media records.

React/Vite versions are declared in the package lock; Python package versions
were checked against the installed environment. Model/runtime selections and
provenance are recorded in the [disclosures](DISCLOSURES.md).

## How the AI analysis works

1. **Observe:** OpenCV captures a fresh frame. EfficientDet detects a person;
   Face Landmarker checks for a usable face. Enrollment and matching require
   exactly one detected person and available face analysis.
2. **Learn:** a parent explicitly labels a captured face as Family member. The
   landmark-bounded crop must be at least 64 × 64 pixels; it becomes a 128 × 128
   grayscale example. LBPH learns its texture histograms locally. One example is
   supported; the reference cannot be silently overwritten.
3. **Compare:** the recognizer evaluates later face crops. Lower distance means
   a closer appearance match. A displayed distance of **65 or below** is accepted
   as Family member; a rejected comparison or absent enrollment remains Unknown.
   Unclear/no/stale faces are presented as waiting or limited, not a valid match.
4. **Explain:** one AI Analysis view combines the verdict, acceptance/rejection
   reason, labeled-example count and measurements. Results within five distance
   units of the cutoff receive a parent-confirmation note. Automatic Qwen calls
   select existing facts; validated selections retain their original wording.
5. **Guide:** when Child safety mode is on, a family match asks the child to
   check with a parent before opening. Unknown or unclear faces prompt keeping
   the door closed and getting a parent. When off, recognition remains visible
   without child warnings. These recommendations are application guidance based
   on model observations; Qwen does not decide identity, danger or permission.

The person-detector percentage and LBPH distance are different measurements.
Neither is a calibrated probability of safety or friendly intent. The distance
threshold is provisional; pose and lighting can produce false or missed matches.

## Local execution and data handling

Capture, vision inference, LBPH learning/matching, Qwen inference, storage and
the interface run on the user's computer. FastAPI and Ollama communicate locally;
the core implementation uses no cloud AI API. Initial dependency/model acquisition
requires internet. A complete disconnected restart and traffic inspection have
not yet established end-to-end offline acceptance.

Explicit enrollment stores the original JPEG, including background, and the
face sample in ignored local SQLite storage. Preview requires the protected
local API. Status/runtime reports omit stored images. Reset and Stop preserve
enrollment; Delete removes it and invalidates old comparisons. Delete does not
claim erasure of external backups. Camera viewing does not automatically save
footage. The current parent toggle is not authenticated parental access.

## Verification and limits

The saved source audit passes backend/frontend regression, production/static
builds, static markup, bundle and documentation-link checks. Recognition tests
perform actual LBPH training/prediction on synthetic textures; these are not
human face accuracy benchmarks. Owner screenshots provide a live recognition
example, not a measured recognition rate or full final-interface acceptance.

Current learning is **supervised enrollment and appearance matching**, not RL,
automatic identity discovery or autonomous learning from repeated visits. The
prototype does not demonstrate physical CCTV integration, a door lock, siren or
parent push notification. Face/Pose historical options do not imply all models
are enabled; the current detector enables face analysis only. Asset-specific
vision-model license confirmation remains pending.

## Focused improvement roadmap

1. **Recognition reliability:** evaluate consented family/unknown examples across
   lighting, pose and distance; measure false/missed matches and calibrate the
   threshold before claiming accuracy. Improve face alignment and matching only
   against recorded evaluation evidence.
2. **Household learning:** support multiple family members and additional
   parent-confirmed examples. Let explicit corrections improve the reference
   set over time, with clear preview/deletion controls and no silent enrollment.
3. **Household deployment:** integrate a supported camera feed, authenticate
   parent controls, validate fully offline startup and optionally deliver parent
   notifications. These are future work, not current demo features.

[Current demo and startup](FAMILY_REFERENCE.md) ·
[Submission draft](../demo/SUBMISSION_DRAFT.md) ·
[Model/tool disclosures](DISCLOSURES.md)
