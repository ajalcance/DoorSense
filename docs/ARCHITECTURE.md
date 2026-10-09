# Offline prototype architecture

Status: proposed implementation specification; no running components yet.
Target: Apple M1 laptop, 8 GB unified memory.

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

This is a reference, not a locked dependency list. Select compatible versions
after checking macOS, available Python, model assets and measured resource use.
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

Each downloaded model needs an inventory entry: name, version/source, licence,
local filename, actual size and SHA-256. These fields are pending asset selection.

### Approved local LLM integration

Selected for implementation on 2026-10-09: Ollama `qwen3:0.6b`, Q4_K_M,
listed download 523 MB, Apache-2.0 model licence. No weights are downloaded and
no local inference is verified yet. Record the actual pulled model digest,
Ollama version, licence and asset size during preflight. Model size is not total
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

Planned deliverables: a `local_llm.py` adapter, versioned prompts/response schema,
configuration example, focused contract/fallback checks, model/tool disclosures,
and actual setup/start instructions. Show camera observations -> event rules ->
local Qwen request -> console output. Record model digest, actual response source,
request timing and inference metrics for diagnostics. Do not commit weights,
private camera recordings, personal event history or machine-specific secrets.
Repository: https://github.com/ajalcance/DoorSense . Initial scaffolding is
prepared; application integration remains unimplemented.

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
