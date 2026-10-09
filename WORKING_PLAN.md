# DoorSense working plan

## Current approved demo scope

The current submission uses real laptop-camera person/face inference, one
parent-enrolled Family member reference, LBPH appearance matching and Unknown
results after deletion or rejection. Parents control Child safety mode. Live
camera banners and one automatic AI Analysis view present guidance and measured
matching evidence; there are no sensor/activity simulation controls or manual
category selections. Learning is explicit supervised enrollment, not RL.

See the [technical overview](docs/TECHNICAL_OVERVIEW.md) for what works now,
validation limits and three focused next steps: evaluated recognition reliability,
additional parent-confirmed household examples and supported household deployment.
The [runbook](demo/DEMO_RUNBOOK.md) is the current demo sequence.

## Historical product planning (superseded for this demo)

The following records earlier scope and implementation discussions. It does not
reactivate sensor simulations, manual labels, tabs or autonomous learning claims.

Updated: 2026-10-10, Asia/Manila.

## Approved product direction

DoorSense is a local AI doorway safety assistant. It observes the entrance,
recognises activities, combines camera and physical sensor evidence, and helps
residents understand and respond to events from inside their home.

The user approved the long-term roadmap and proceeding with an offline prototype.
The selected prototype uses the laptop webcam, local inference, and a modern
indoor console shown on an external display. The laptop is an Apple M1 with
8 GB unified memory. Qwen3 0.6B via Ollama is approved for local explanations
and resident questions. Remaining dependency choices require preflight.
The initial webcam/person-detection spike has passed basic owner acceptance.
The bounded Qwen adapter is implemented: four genuine supported examples worked;
the application guards unsupported questions after model abstention failed.
Free-text/history questions remain target scope, not current capability.
Broader detection quality, live failure handling, integrated application behaviour,
hardware integration and product security effectiveness remain unverified.

Document responsibilities:

- [README](README.md): project entry point and document index.
- [Current state](docs/CURRENT_STATE.md): implemented and verified facts.
- [Architecture](docs/ARCHITECTURE.md): offline runtime and interfaces.
- [Console specification](docs/CONSOLE_SPEC.md): resident experience and states.
- [Build plan](docs/BUILD_PLAN.md): ordered implementation checkpoints.
- [Demo and acceptance](docs/DEMO_AND_ACCEPTANCE.md): evidence and disclosures.

This file is the product roadmap, not proof of implementation.

Product statement:

> DoorSense helps households understand what is happening outside their door,
> receive evidence-based warnings, and respond from inside, with AI running locally.

## Approved prototype and offline contract

- Laptop webcam substitutes for the exterior ESP32 camera; this is real camera
  input, not ESP32 camera emulation.
- The laptop runs all core inference, event processing, storage, and the console.
- An HDMI or USB-C external display represents the resident's indoor console.
- Core operation must start and continue with Wi-Fi disabled, Ethernet unplugged,
  and no external network access after required dependencies and assets are present.
- UI bundles, fonts, icons, models, sounds, and media must be local. No CDN,
  cloud inference, account sign-in, online licensing check, or Wokwi dependency.
- Initial package/model acquisition requires existing local assets, downloads
  before disconnecting, or an offline transfer. Runtime must not auto-download.
- Doorbell, vibration, and door-contact inputs are explicitly labelled simulated
  sensor events. Actual model predictions must not be replaced by scripted values.
- Physical ESP32 integration, continuous unattended operation, and adaptive
  learning remain future milestones with separate acceptance evidence.

## M1 8 GB resource direction

Use small pretrained vision models incrementally, alongside the approved Qwen3
0.6B text model via Ollama. The listed quantized download is 523 MB; this excludes
Ollama, vision assets, dependencies and context/runtime memory. Measure the full
pipeline on the M1 before claiming compatibility or response speed.

Qwen explains supported event facts and answers bounded questions about local
event history. It cannot inspect images, set severity, infer a visitor's intent,
or control the door. Use short context/output, thinking disabled, event-triggered
or resident-requested calls, and one bounded generation at a time. Preserve the
camera/event loop independently and fall back to structured templates when Qwen
is missing, slow, unavailable or produces unsupported output. A fallback is not
a successful LLM-inference demonstration.

Downloading an LLM does not implement reinforcement learning. Keep PyTorch
training, ONNX deployment and RL packages out of the initial runtime unless a
measured need emerges. Record model provenance, actual sizes, memory use and
latency. Compatible package versions and the vision-model selection remain open.

## Intelligence layers

1. Environment: doorway zones, lighting, visibility, camera obstruction.
2. People and objects: presence, movement through the doorway zone, objects left
   behind. Automatic personal identification is outside this plan; residents may
   manually label visits or use an explicitly provisioned guest credential.
3. Activities over time: arrival, departure, doorway occupancy, repeated doorbell
   presses, interaction with the door.
4. Physical evidence: door contact, vibration, repeated impacts, selected sounds.
5. Context and response: resident settings, expected visits, corroborating events,
   clear alerts with supporting evidence and uncertainty.

Example proposed alert: person near doorway plus repeated door vibration and a
door-contact change while armed produces an urgent review notification with the
supporting clip. These signals suggest an event for review; they do not establish
a visitor's intent or that a crime has occurred.

Facial appearance must not establish emotion, personal identity, relationships,
or dangerousness. Observable facial movements, if later included, remain visual
descriptions and do not determine security warnings. An unusual event is not
automatically a dangerous event. Poor visibility or a disconnected camera must
remain visible as an uncertain or unavailable monitoring state.

## Future-progress roadmap

| Stage | Proposed capability | Evidence before advancing |
| --- | --- | --- |
| 1. Doorway awareness | Local camera input, person detection, indoor notification, event snapshots | Run with internet disconnected; measure missed detections and unwanted alerts |
| 2. Activity understanding | Arrival/departure, occupancy duration, repeated interactions, event timeline | Test staged activities across lighting changes and partial obstruction |
| 3. Corroborated warnings | Video plus door-contact, vibration, and audio sensors | Test defined tampering scenarios against ordinary knocks and authorised entry |
| 4. Household adaptation | Resident feedback, zones, routines, periodic model improvements | Reduce nuisance alerts on separate test data without increasing missed important events |
| 5. Adaptive product | Bounded notification learning, dedicated local hub, mobile interface, authenticated access, retention controls | Compare versions, test failure states, support rollback |

The initial camera/detector spike has passed basic owner acceptance. The hackathon prototype should
demonstrate a bounded part of this roadmap, not claim the complete product.

## Learning strategy

- Supervised learning: annotated observations and clips for defined events.
- Anomaly detection: entrance-specific patterns, with unusualness leading to
  review rather than an automatic danger label.
- Reinforcement learning: future action selection with explicit feedback;
  learning from data alone is not necessarily reinforcement learning.
- Candidate first RL application: a contextual bandit choosing among approved
  notification options for non-critical events.
- Keep urgent sensor-triggered alerts outside exploratory notification learning.
  Dismissal does not prove harmlessness; missing feedback is unknown.
- Collect owner-reviewed labels, use separate evaluation data, compare new models
  and policies against the previous version, and support rollback. Evaluate
  candidate policies on recorded events before affecting live notifications.
- Door access remains under resident control in this proposed product scope.

## Reference architecture and stack for discussion

Camera/sensors -> local household processing hub -> evidence and event engine ->
resident interface and indoor notifications.

| Component | Proposed technology |
| --- | --- |
| Prototype camera | Laptop webcam through a local camera adapter |
| Future camera/sensor endpoint | ESP32 camera, Arduino framework/C++ |
| Initial local hub | Apple M1 8 GB; Python, FastAPI and OpenCV are candidate tools |
| Initial detection | Small MediaPipe model bundles; compatibility and latency to verify |
| Event storage | SQLite and locally stored clips |
| Interface | Locally served console; React/Vite with bundled assets is the reference option |
| Local language model | Approved Qwen3 0.6B via Ollama; text explanations and event-history questions |
| Explanation fallback | Structured templates; alerts and monitoring independent of LLM availability |
| Future training | PyTorch on a development machine |
| Future inference deployment | ONNX Runtime for validated compatible exports |
| Future adaptive notification policy | Vowpal Wabbit contextual bandits |

The ESP32 is initially an image/sensor endpoint. The local hub performs demanding
inference. Embedded inference is a separate future integration dependent on the
exact board, memory, supported runtime, and measured model performance.

## Console and whole-scene analysis direction

The user endorsed a modern indoor console as the main resident-facing product.
For the selected demo approach, the laptop webcam represents the exterior camera, local
inference runs on the laptop, and an external display shows the indoor console.
This is camera substitution; ESP32 emulation may only be claimed if firmware
actually executes in an emulator. Camera/vision and bounded Qwen spikes exist;
console/event/storage source is implemented, with partial owner webcam/Qwen
integration evidence. Optional scene features and the interactive dashboard are
implemented; new model and full live/offline acceptance remain pending.

Approved simulation-console layout: persistent left simulation controls/settings,
a somewhat smaller middle live camera, and right assessment/Scene/Qwen/Evidence.
Overview/Events navigation and grouped global controls live in the header.
Simulation inputs stay visible while analysis updates; backend state supplies
contact/progress/timing after refresh. Diagnostics remains an optional overlay.
Events retains the saved history/evidence workspace. This layout is implemented;
rendered fit and live interaction acceptance remain pending.
Use readable typography, restrained overlays, clear labels, and smooth state
transitions. Technical diagnostics belong in an expandable panel.

Extend observations beyond faces to posture, movement, clothing, carried objects,
and environmental visibility. Examples: person standing or crouching, arm raised,
movement toward the configured doorway zone, backpack visible, hood visible,
dark glasses visible, or relevant body parts outside the frame.

These are descriptions of visible evidence. A hood, dark glasses, backpack, or
body pose alone must not raise the security severity or establish malicious
intent. Face occlusion affects assessment availability, not a visitor's threat
classification. Do not infer that an unseen item is absent.

Proposed severity contract, always accompanied by text and an icon:

| Colour | Resident-facing meaning | Example condition |
| --- | --- | --- |
| Green | Monitoring; no configured alert conditions detected | Camera available; no active review or urgent event; this is not a guarantee of safety |
| Orange | Review an event | Repeated doorbell presses or occupancy beyond a configured duration |
| Red | Urgent event requires review | Corroborated repeated door impacts and a door-contact event while armed |
| Grey | Assessment limited or unavailable | Camera disconnected, poor lighting, relevant regions obscured, or model unavailable |

Monitoring availability and event severity are separate fields. An urgent sensor
event stays visible even if video assessment becomes unavailable. Initial
thresholds are proposed configurable rules, not validated danger probabilities.

Analysis presentation should answer: what was observed, why the event was flagged,
what evidence is available, and what remains uncertain. Avoid a numerical danger
percentage derived from appearance. Resident actions include reviewing live view,
acknowledging an alert, and replaying the event clip.

Candidate models: MediaPipe Face Landmarker for visible facial movement;
MediaPipe Pose Landmarker for body landmarks; a supported object detector for
people and carried objects. Pose landmarks do not themselves establish actions
or intent. Hood and dark-glasses detection require a separately validated
attribute model and are not established capabilities of the initial detector.
Camera framing must include relevant body parts and objects for these analyses.

## Physical integration and simulation boundaries

Selected prototype: real laptop-webcam input with local AI and simulated door
sensors. Optional local video replay supports repeatable scenarios, always
labelled as replay. A future ESP32 input adapter implements the same frame
contract without requiring a different event engine or console.

For physical hardware, the camera and local hub may use a home Wi-Fi router
without an internet uplink, or the ESP32 may create its own password-protected
Wi-Fi access point. Bluetooth is not the planned camera-stream transport.
Wi-Fi networking is not internet access. Physical camera and LAN integration
remain untested. The webcam prototype needs neither a router nor active Wi-Fi.

Wokwi is a candidate for separate ESP32 firmware and supported peripheral
simulation. Its official hardware catalogue does not establish working camera
sensor simulation. It should not be a dependency of the core offline AI demo.

Simulation does not validate real camera capture, firmware timing, power,
physical sensor performance, or AI running on an ESP32. Prepared firmware is not
hardware-tested firmware. Camera replay must not substitute scripted detection
results for actual model inference.

## Hackathon requirements checked from the supplied briefing

Source: AppBuildersPH Hackathon 2026 Participant Briefing.pdf (supplied by the participant; local reference under private/reference/)

- Page 9: substantially built during the event; working product demonstrated;
  meaningful local AI inference; tools and models disclosed.
- Page 15: finalists pitch and demo live for five minutes, then three minutes Q&A.
- Pages 16 and 25: demo video, public repository, disclosures, and submission by
  2026-10-10 10:00 AM Philippine time; one submission and deadline code freeze.
- Page 26: finalists need an on-site team representative and their demo laptop.
- Page 28: public live deployment is not required if recreation instructions exist.
- The briefing does not explicitly resolve eligibility of simulated hardware.
  Obtain organiser clarification before relying on a hardware-simulated entry.

## Next action

The owner expanded scope through Slice 10 and approved an interactive local-AI
dashboard and lightweight family demo. Slice 8 scene code is implemented; Slice 9
acceptance tooling and Slice 10 reproduction/demo materials are prepared.
[Current commands/contracts](docs/SLICES_8_10.md) and [audit](docs/SLICES_8_10_AUDIT.md)
separate source checks from genuine face/pose quality and offline acceptance.
No new model acquisition, capture/service startup, Git mutation or publication
was performed. Camera boxes are frame-local detections, not identity tracking.
Green face availability does not recognize family or establish permission to open;
grey is limited availability; amber/red remain defined event-rule severities.
Owner-confirmed snapshot labels are explicit manual facts. The demo prioritises
actual vision outputs and a genuine local Qwen evidence selection, then disconnected
restart and failure resilience. The owner declined a heavier VLM path; cap/glasses
classification, automatic family recognition and emotion inference are not delivered.
Organiser acceptance of simulated sensors remains unresolved.

## Technical references

- https://huggingface.co/Qwen/Qwen3-0.6B
- https://ollama.com/library/qwen3:0.6b
- https://docs.ollama.com/api/chat
- https://docs.ollama.com/faq
- https://developers.google.com/edge/mediapipe/solutions/vision/object_detector
- https://developers.google.com/edge/mediapipe/solutions/vision/face_landmarker
- https://developers.google.com/edge/mediapipe/solutions/vision/pose_landmarker
- https://github.com/espressif/esp32-camera
- https://github.com/espressif/esp-who
- https://docs.espressif.com/projects/arduino-esp32/en/latest/api/wifi.html
- https://docs.wokwi.com/guides/esp32
- https://docs.wokwi.com/getting-started/supported-hardware
- https://docs.pytorch.org/tutorials/beginner/transfer_learning_tutorial.html
- https://onnxruntime.ai/docs/
- https://vowpalwabbit.org/docs/vowpal_wabbit/python/latest/tutorials/python_Contextual_bandits_and_Vowpal_Wabbit.html

## Parent-enabled child mode and combined visit demo

Approved 2026-10-10: optional Child safety mode enabled manually by parents,
with one visit workflow and only Family member/Unknown snapshot categories.
Urgent review combines fresh genuine person detection and three simulated impacts
on a closed door within five seconds, before it opens. Visitor identity/intent
are not inferred. Manual family confirmation does not suppress activity alerts.
Automatic family database matching/action recognition are outside current scope.
