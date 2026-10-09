# DoorSense architecture

## Current face-recognition pipeline

The [technical overview](TECHNICAL_OVERVIEW.md) is the current implementation
reference. On the local computer: OpenCV camera capture → EfficientDet person
detection → Face Landmarker localization → LBPH appearance matching against a
parent-enrolled SQLite reference → live camera banner and unified AI Analysis.
Supplied text facts separately go to local Qwen through Ollama for bounded
evidence selection. Application guidance is gated by the parent-controlled Child
safety mode. Enrollment/matching continue while that mode is off.

Only Family member and Unknown are current visitor categories. No sensor inputs
or occupancy thresholds can trigger a production demo alert. Earlier records and
test-only legacy event paths remain. End-to-end disconnected startup remains
unverified; this diagram establishes component placement, not offline acceptance.

## Historical architecture and planning notes (superseded)

### Earlier child-mode and sensor-scenario contract (superseded)

The [current console contract](CONSOLE_SPEC.md) supersedes earlier arming,
door-open urgency and visitor-label wording below. Parent-enabled Child safety
mode is optional; camera viewing remains available while it is off. Simulation is
one visitor-category/camera/sensor workflow, with only Family member and Unknown.
Categories are parent-confirmed snapshots, not database recognition or intent.
Urgent requires fresh person detection plus three simulated impacts on a known
closed door within five seconds. Events contain webcam and sensor provenance;
opening is not required. Missing/stale camera evidence prevents combined urgent.
Earlier saved history is preserved. [Owner checks](SIMULATION_CONSOLE_ACCEPTANCE.md)
for genuine combined camera/Qwen/browser/offline acceptance remain pending.


Status: target contracts, webcam/person-detection spike and Slice 5 console service
foundation, now extended through Slices 6–7 with labelled simulated rules and
SQLite history/explicit media/feedback. [Implementation](SLICES_6_7.md). Rendered
and genuine console integration acceptance pending.
Ollama startup/metadata and basic owner camera/model acceptance passed;
first genuine Qwen calls ran; full example and integrated-app acceptance remain pending.
Target: Apple M1 laptop, 8 GB unified memory.

Slice 8 adds optional local Face/Pose tasks and bag classes, with isolated failures,
exact-frame facts, two-frame stabilization and inference budgets. Slice 9 owner
acceptance tooling and Slice 10 source inventory/demo preparation are delivered;
[contracts](SLICES_8_10.md) and [audit](SLICES_8_10_AUDIT.md). New genuine model and
offline/reproduction acceptance remain pending. Manual visitor annotations are
snapshot-bound owner facts, not biometric identities. No VLM was added.

## Operating contract

The webcam, inference, event engine, storage and console run on one laptop.
The console is a locally served browser application on an external display.
Loopback networking between local processes is allowed; external networking is
unnecessary. The camera, inference and alerts must start after a restart with
Wi-Fi off and Ethernet disconnected, once all required assets are available.

Do not require cloud inference, CDN assets, remote fonts, telemetry, remote login,
online licence validation, runtime package installation or automatic model pulls.
Missing model assets produce a visible unavailable state, not a cloud fallback.

## Reference components for stack discussion

| Component | Responsibility | Candidate |
| --- | --- | --- |
| Camera adapter | Capture timestamped webcam frames; release device on stop | OpenCV |
| Vision workers | Produce supported observations and availability state | Small MediaPipe model bundles |
| Event engine | Combine observations with timestamped sensor events | Python rules and bounded state |
| Local explanation adapter | Explain supplied event facts and answer event-history questions | Approved Qwen3 0.6B via Ollama |
| Application service | Stream frames/observations, handle controls, serve UI | FastAPI |
| Local event store | Keep event metadata, optional snapshots/clips, feedback | SQLite and local files |
| Console | Live view, analysis, alerts, controls and event history | React/Vite built to local static assets |

Direct pins, backend hash lock, frontend integrity lock and initial asset hashes
are now recorded after preparation; see current state. Actual model compatibility
and combined resource use remain live acceptance checks.
Serve the built console from the application service for the final demo; avoid
requiring a separate frontend development server at runtime.

## Model and explanation strategy

- Start with one small detector for people and supported objects.
- Add visible facial movement and body-landmark models one at a time after
  measuring resource use. Disable unsupported or unloaded features explicitly.
- Integrate Qwen3 0.6B via Ollama for concise explanations of supplied facts
  and resident questions about local event history. Keep severity in event rules.
- Retain structured-template fallback; LLM availability cannot block monitoring.
- Use thinking disabled, bounded context/output, one generation at a time and
  event-triggered or resident-requested calls rather than per-frame generation.
- Do not add PyTorch, a vector database, training pipelines, or RL packages to
  the first runtime solely for future roadmap work.
- Schedule inference at a configurable sampled rate with a latest-frame buffer.
  Do not accumulate an unbounded processing queue. Measure latency and memory.

Initial acquired models have version/source, local filename, actual size and
SHA-256 in the inventory. Vision asset-specific licence confirmation remains pending.

### Approved local LLM integration

Selected for implementation on 2026-10-09: Ollama `qwen3:0.6b`, Q4_K_M,
listed download 523 MB, Apache-2.0 model licence. Weights, actual hashes/sizes and
Ollama 0.40.1 startup/exact model metadata are verified; the genuine v3 run passed four supported event examples but failed identity-question
abstention. The application now restricts requests to tested presets and handles
unsupported questions without Qwen; broader free-text/history QA is deferred. Model size is not total
RAM consumption; benchmark vision, language model and console together.

The Python application adapter calls `http://127.0.0.1:11434/api/chat` with the
local model tag, `stream: false` and `think: false`. Start with a small context
budget (2048 tokens) and short output (about 100 tokens), then measure suitability.
Keep prompts compact and requests bounded by a timeout. The adapter receives
structured, timestamped observations, rule-assigned severity, source provenance
and relevant local event history. It never receives frames: this is a text model.

For resident questions, retrieve relevant local events deterministically and
supply those records as context; no vector database or arbitrary tool execution
is needed. If the history lacks evidence, say that the information is unavailable.
Generated text must not establish identity, emotion, intent or permission to open.

Use a narrow structured response contract and validate output before display.
Schema validity alone does not prove factual accuracy: keep authoritative facts,
severity and actions in separate UI fields, test unsupported-claim cases, and
fall back to templates on malformed or unsupported results, timeout, missing
model or daemon failure. Never relabel fallback text as a Qwen response. Expire
or discard responses if the event changed before generation completed.

Before disconnecting, prepare Ollama and the model, disable cloud features with
`OLLAMA_NO_CLOUD=1`, restart the daemon with that setting and verify it. Bind to
loopback and never auto-pull models or use a cloud fallback at runtime. Offline
acceptance must restart both the application and Ollama while disconnected and
show a fresh, successful local generation. A downloaded model does not implement
RL or learn automatically from resident feedback.

### GitHub integration evidence

Implemented Slice 4: a `local_llm.py` adapter, versioned evidence-selection prompt,
dynamic fact-ID schema, bounded request settings, fifteen HTTP/application-boundary fixture checks and
[owner measurement instructions](LLM_SPIKE.md). Four supported v3 event examples worked; model-only identity abstention failed.
Unsupported questions now receive an application response with no model claim.
The initial adapter renders exact selected fact wording and authoritative
uncertainties; unrestricted generated prose is deferred. Show camera observations -> event rules ->
local Qwen request -> console output. Record model digest, actual response source,
request timing and inference metrics for diagnostics. Do not commit weights,
private camera recordings, personal event history or machine-specific secrets.
Repository: https://github.com/ajalcance/DoorSense . Initial scaffolding is
prepared; camera-only console bridge implemented with in-process fixtures.
Genuine rendered integration remains pending. See [foundation](CONSOLE_FOUNDATION.md).

References checked on 2026-10-09:
- https://huggingface.co/Qwen/Qwen3-0.6B
- https://ollama.com/library/qwen3:0.6b
- https://docs.ollama.com/api/chat
- https://docs.ollama.com/capabilities/structured-outputs
- https://docs.ollama.com/capabilities/thinking
- https://docs.ollama.com/faq

## Shared input and observation contracts

A frame includes source ID, mode (webcam/replay/future ESP32), capture timestamp,
dimensions and image data. Use monotonic time for durations and wall time for
display. The future ESP32 adapter must produce the same application-level data.

An observation includes its type, timestamp/frame reference, model provenance,
relevant region/landmarks, model score if present, and uncertainty. A model score
is not a calibrated danger probability. Outputs expire; stale observations do
not remain attached to a later visitor.

A sensor event includes event ID, type, timestamp, value and provenance. The
prototype provenance is simulation. Buttons create explicit sensor events and
never fabricate camera-model detections. Replay footage remains labelled replay.

An alert includes severity, rule ID, triggering evidence, time and acknowledgement
state. Store the event history separately from the latest displayed status.

`/api/status` includes authoritative `simulation` session state: independent input
revision, last accepted contact, six timestamped accepted/ignored replies, rolling
bell/impact counts and monotonic remaining windows, plus fresh occupancy duration.
`/api/sensors` returns the same status after processing, so timed controls update
immediately without waiting for history polling. Input revisions prevent stale
polls from regressing progress without invalidating Qwen evidence on every press.
Frontend countdowns subtract request transit/packet age; expired counts await the
next backend packet rather than being reconstructed from local clicks/logs.
Packets older than 1.5 seconds make simulation state unavailable. Occupancy
progress stops at the last genuine fresh observation and clears on freshness loss.
Contact is separate from pending rule inputs: cancellation preserves its display
but clears corroborating evidence. Reset clears both; service restart starts unknown.

## Alert and availability rules

- Green: monitoring, no configured alert conditions detected.
- Orange: review event, such as repeated bell presses or sustained occupancy.
- Red: urgent review of corroborated impact/contact events while monitoring armed.
- Grey: a feature or camera assessment is limited/unavailable.

Keep event severity and monitoring availability independent. An urgent sensor
event remains visible when camera inference is unavailable. Partial face/body
visibility affects only the relevant feature; it does not erase person detection.
Clothing, bags, visible facial movements and posture alone do not elevate severity.
No detected alert is not a guarantee of safety; an unseen object is not absent.

Debounce duplicate events, stabilise model-derived observations across frames,
and record why a rule fired. Thresholds are configurable demo rules awaiting
evaluation, not validated security thresholds. Acknowledgement silences/marks an
event; it does not establish that the event was harmless or delete its evidence.

## Storage and controls

Camera starts through an explicit resident action and macOS permission. Stop
releases capture and visibly pauses monitoring. Recording and saved event media
must be explicit, local and deletable. Use session-only media initially; the
resident may enable local evidence storage when implemented. Persist selected
event metadata and explicit feedback locally; absence of feedback stays unknown.

The prototype service binds to loopback. Future LAN camera access, authenticated
streams, remote access, device provisioning and encryption require separate work.
Do not publish footage or start a public server as part of this prototype.

## Future physical transport

ESP32 camera -> local Wi-Fi -> local hub -> indoor display.

Options: camera and hub on a router with no internet uplink, or laptop joins a
password-protected ESP32 access point. Wi-Fi is the planned image transport;
Bluetooth is unnecessary for the first camera integration. No physical transport
is currently implemented or tested. Wokwi is separate optional firmware evidence,
not a dependency of this offline application.
