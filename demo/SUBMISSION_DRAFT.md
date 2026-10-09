# DoorSense — submission description

Final description for the current face-recognition demo. Prepared locally;
not published or submitted. Updated 2026-10-10, Asia/Manila.

## Project description

Keeping children safe at home is a fundamental responsibility, and the front door
is one place where a moment of uncertainty can matter. When a visitor arrives,
a child may not know who they are or whether to open the door. Security cameras
provide visibility, but interpreting the scene and deciding what to do still
falls on the person watching.

DoorSense addresses this gap by combining a live camera feed with artificial
intelligence running on the household's own device. It is designed to help
children understand when to pause and seek a parent's help before opening the door.

Parents enroll a family member by capturing and confirming a face. The system
learns that appearance and compares it with people subsequently appearing on
camera. Its AI Analysis detects a person and checks whether a clearly visible
face matches the enrolled family example.

When the system cannot establish a familiar match, it highlights the visitor as
unknown and, when Child safety mode is enabled, displays a warning to keep the
door closed and get a parent. If the face is unclear, it makes that uncertainty
visible and recommends parent verification. This provides a precaution at the
doorway without assuming that every unfamiliar visitor is dangerous.

Parents choose when to enable Child safety mode. A familiar visitor prompts the
child to ask a parent before opening, while an unknown visitor prompts them to
keep the door closed and seek help. Prominent camera banners and an automatic
analysis panel make the findings and recommended actions easy to understand.
Recognition supports the decision without treating a familiar face as proof of
safety or permission to open.

Face processing and enrolled images remain on the household's device, providing
private, understandable doorway guidance without relying on a cloud AI service
for the core experience.

## Technical disclosure — form-ready text

DoorSense uses React and Vite for its local browser interface, Python with FastAPI
and Uvicorn for the application service, and SQLite for local storage. OpenCV
captures the webcam feed. MediaPipe runs EfficientDet-Lite0 int8 for person
detection and Face Landmarker for face localization. OpenCV LBPH learns from one
parent-labeled face example and compares subsequent face crops locally. This is
supervised enrollment and appearance matching, not reinforcement learning or
autonomous learning from repeated visits.

Qwen3 0.6B runs locally through Ollama to select supporting observation facts.
It receives text, not images. The application converts recognition results into
child guidance when the parent-controlled Child safety mode is enabled. Live
camera banners and one automatic AI Analysis view show the result and match
explanation. Recognition continues while child guidance is disabled.

Capture, model inference, matching and enrolled-image storage run locally;
the core workflow uses no cloud AI API. Internet is needed for initial software
and model acquisition and external submission hosting. Full disconnected startup
remains unverified. The prototype uses a laptop webcam and one family reference;
it does not demonstrate physical sensors, door locking or parent notifications.
Face distance is not calibrated identity confidence or a safety probability.

Codex assisted development and documentation. Existing open-source models and
libraries are used, with provenance and license-review status recorded separately.
Owner screenshots demonstrate a live family match. Automated regression/build
checks pass; final banner/toggle/automatic findings acceptance and recognition
accuracy evaluation remain pending.

## Short improvement roadmap

1. Evaluate lighting/pose and unfamiliar faces; measure false/missed matches and
   calibrate recognition before claiming accuracy.
2. Support multiple family members and additional parent-confirmed examples.
3. Integrate supported camera feeds, authenticated parent controls and optional
   parent notifications after offline and reliability checks.

These are future improvements, not current demo features. See the
[technical overview](../docs/TECHNICAL_OVERVIEW.md) for the complete stack and
feature-by-feature verification status.

## Required disclosure fields

- **What runs locally:** webcam capture, person/face detection, LBPH enrollment
  and matching, Qwen inference through Ollama, the interface/backend and SQLite.
- **What requires internet:** initial dependencies/model acquisition and external
  submission/video/repository hosting. Core inference calls are local; a complete
  disconnected restart/traffic check remains an owner acceptance task.
- **Models/algorithms:** EfficientDet-Lite0 int8 v1; MediaPipe Face Landmarker
  float16 v1; OpenCV LBPH; Qwen3 0.6B.
- **Frameworks/tools:** React, Vite, Python 3.12, FastAPI, Uvicorn, MediaPipe,
  OpenCV contrib, NumPy, SQLite and Ollama.
- **Runtime APIs/cloud services:** local FastAPI and local Ollama; no cloud AI
  API is used for the core demo.
- **AI development tool:** Codex. Confirm any additional tools used by the team.
- **Existing assets:** existing open-source models/libraries. Build chronology,
  any preexisting application code and asset-specific licenses must be disclosed
  accurately; do not infer them from this description.

## Demo boundaries and remaining submission fields

This prototype uses a laptop webcam. Learning is supervised enrollment and
appearance matching, not RL or automatic identity discovery. A match is not proof
of friendly intent, identity certainty or permission to open; the threshold is
unvalidated. Guidance is an application response to model observations. No
physical sensors, automatic door lock, siren or parent push notification is
demonstrated. Automated checks pass; supplied owner screenshots show a live
family match. The final banner/toggle/unified analysis changes still require an
owner trial. Do not claim measured recognition accuracy or completed offline
acceptance without those tests.

Still needed: team members, actual public GitHub URL, demo video URL and
X/LinkedIn video URL. Publication/submission are separate owner actions.

[Current demo](../docs/FAMILY_REFERENCE.md) · [Model/tool disclosures](../docs/DISCLOSURES.md)
