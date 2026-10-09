# Judge guide

## Current submission and demo

Use the [technical overview](TECHNICAL_OVERVIEW.md) for the stack, working features,
evidence and short roadmap, and the [submission draft](../demo/SUBMISSION_DRAFT.md)
for approved product copy and form-ready technical disclosures. These supersede
the historical sensor workflow below.

The current demo uses one parent-enrolled family appearance reference, local
face comparison, parent-controlled Child safety mode, live camera banners and
one automatic AI Analysis view. EfficientDet/Face Landmarker provide camera
findings; OpenCV LBPH trains and compares locally; Qwen selects supplied facts
through local Ollama. The application provides child guidance. No sensor activity
is required or enabled in production.

Owner screenshots show an accepted family match at 53.70 against threshold 65
and other rejected comparisons. These are individual observations, not an accuracy
benchmark. Automated regression/build/static checks pass; final live UI and
fully disconnected startup acceptance remain pending. Learning is supervised
enrollment, not RL. A family match does not grant permission to open the door.

## Historical guide (earlier sensor/event demo)

## What DoorSense aims to solve

A door camera shows a scene; DoorSense aims to help residents understand the event
and its supporting evidence through a local indoor console. The core workflow is
designed to remain available without internet after provisioning.

## Where to inspect

1. [Current state](CURRENT_STATE.md): delivered work and honest verification status.
2. [Architecture](ARCHITECTURE.md): camera/vision → event rules → local Qwen → console.
3. [Build plan](BUILD_PLAN.md): bounded prototype implementation sequence.
4. [Demo and acceptance](DEMO_AND_ACCEPTANCE.md): actual results will be recorded here.
5. [Demo materials](../demo/README.md): recording and live-demo links when ready.
6. [Disclosures](DISCLOSURES.md): models, tools, AI-assisted work and simulated hardware.

## Code navigation

The checkout contains [camera code](../backend/doorsense/camera.py),
[local vision](../backend/doorsense/vision.py) and a
[bounded Qwen adapter](../backend/doorsense/local_llm.py), with prompts/schema,
validation, labelled fallback and application question guards. Evidence is in
[camera spike](CAMERA_SPIKE.md) and [Qwen spike](LLM_SPIKE.md). Four supported Qwen
examples worked; model-only identity abstention failed. Unsupported questions are
handled by the application; displayed wording remains original facts/template.
Console/events/storage are implemented through Slice 7; physical hardware and
full integrated/offline acceptance are pending. [MVP audit](MVP_READINESS.md). This dirty checkout
has not been committed/pushed in this session; remote reproduction is unverified.
Diagrams/fixtures are not genuine model evidence.

## What the demo must establish

Fresh webcam input produces genuine local vision observations. Labelled simulated
sensors trigger evidence-based alerts. Qwen3 0.6B, running locally through Ollama,
explains supplied event facts. Restarting offline produces a fresh model response;
a template fallback cannot count as proof of Qwen inference. Record actual model
identity, response timing and combined memory use on the M1 8 GB.

The laptop webcam substitutes for the future ESP32 camera. No claim is made that
AI runs on the ESP32, that firmware is emulated, or that the prototype establishes
reliable 24/7 protection. Physical integration and learning remain roadmap work.
