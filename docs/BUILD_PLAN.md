# Ordered prototype build plan

## Current completion checkpoint

The face-only implementation is delivered with source/build checks. The
[technical overview](TECHNICAL_OVERVIEW.md) records current capabilities and
limitations. Use [current acceptance](DEMO_AND_ACCEPTANCE.md) for final owner
browser/camera/automatic-Qwen trials and offline restart, then complete the
[submission fields](../demo/SUBMISSION_DRAFT.md). No additional sensor or activity
features are required for this demo.

## Historical ordered implementation plan

The slices below record the earlier build sequence; they are not the current
face-only demo specification or a claim that remaining live acceptance passed.

Status: local preparation passed; initial webcam/person-detection spike implemented,
with basic owner camera/model acceptance complete. Broader quality, live failure
handling and offline acceptance remain pending. Four supported Qwen examples worked; an application guard handles unsupported questions.
General model abstention failed and remains documented. Console design approved;
foundation implemented; rendered and genuine integration acceptance pending.
Slices 6 and 7 are now implemented with automated source/fixture evidence; see
[Slices 6 and 7](SLICES_6_7.md). Slice 8 scene code, Slice 9 acceptance tooling
and Slice 10 local reproduction/demo preparation are now implemented/prepared:
[current contracts](SLICES_8_10.md), [audit](SLICES_8_10_AUDIT.md).
Required genuine new-model, offline and reproduction/submission evidence remains pending.
Target: Apple M1, 8 GB unified memory. Qwen3 0.6B via Ollama is approved;
backend/frontend dependencies and initial model assets are locally acquired.

## Chat slice numbering

Section numbers below group implementation areas; chat slices use this map.
The original [Slice 5 handoff](HANDOFF_SLICE_5.md) is historical; current next work
is staged model/live/offline acceptance in [Slices 8–10](SLICES_8_10.md).

| Chat slice | Scope | Section below |
| --- | --- | --- |
| 1 | Read-only preflight | 0 |
| 2 | Runtime/packages/assets preparation | 0 |
| 3 | Webcam/person spike | 1 |
| 4 | Bounded Qwen spike and guards | 1a |
| 5 | Console design/review and foundation | 2 |
| 6 | Simulated sensors, event rules and integration | 3 |
| 7 | History, explicit media/replay and feedback | 3 |
| 8 | Incremental face/pose/objects | 4 |
| 9 | Offline/failure acceptance | 5 |
| 10 | Reproduction/demo/submission preparation | 6 |

## 0. Stack and local asset preflight

- Confirm macOS/Python compatibility, camera permission path and external display.
- Inventory existing runtime packages and small vision model assets.
- Select compatible pinned dependencies and record model sources/licences/sizes.
- Prepare Ollama and Qwen3 0.6B; record the actual digest, size and licence.
- Disable cloud features, verify loopback binding and prohibit runtime model pulls.
- Prepare packages/assets before disconnecting, or transfer them offline. Obtain
  organiser clarification on the disclosed sensor/camera substitution approach.

Packages/models are acquired, dependency imports and Ollama metadata checks passed.
External-network behaviour, full licence review and actual inference remain separate
acceptance evidence; see [current state](CURRENT_STATE.md).

## 1. Actual camera and inference spike

Implementation: [owner commands and acceptance](CAMERA_SPIKE.md). Nine fake-camera
lifecycle/expiry/threading checks passed. Sandbox model check Blocked on NSOpenGL
context, but owner model and fresh webcam inference worked. Initial permission
startup bug corrected; clean rerun and owner entry/exit, physical pause and restart
confirmation complete the basic checkpoint. Broader quality, live failure handling
and offline acceptance remain pending.

- Read the laptop webcam locally and run one selected small detector.
- Show actual observations with capture and inference timestamps.
- Measure response time and memory on the M1; cap inference rate and queue size.
- Test fresh movements rather than relying on prerecorded detection results.

Complete when local camera/model output is genuine, usable and stable enough to
support the console. Model failure must remain visible.

## 1a. Genuine local Qwen inference spike

Slice 4 bounded adapter is ready for integration: four supported genuine v3
requests worked; fifteen fixture checks passed. Model-only identity abstention
failed. The application restricts Qwen requests to tested event presets and
returns unavailable for all other questions before HTTP. The updated runner
separates generation from the application guard; it cannot claim five genuine
passes. See [evidence and limitations](LLM_SPIKE.md). Free-text/history QA, offline
acceptance and live daemon failure scenarios remain separate checkpoints.

- Implement the local API adapter, compact prompts and narrow response contract.
- Pass supplied event facts; keep alert severity outside the LLM.
- Disable thinking, cap context/output and use one bounded request at a time.
- Check output on distinct event examples and questions, including missing evidence.
- Check malformed/unsupported output, timeout, missing model and daemon failure.
- Measure cold-start and warm latency and combined memory with camera inference.

Complete when fresh offline requests produce genuine Qwen responses, supplied
facts are preserved on recorded examples, and fallback leaves monitoring usable.
Passing an API call alone does not establish factual reliability or resource fit.

## 2. Modern console foundation

Approved Slice 5 foundation is implemented; build and in-process fixtures passed.
Production presentation fixtures are removed; owner screenshot establishes partial
genuine webcam/Qwen integration. Current dashboard/model/whole-workflow acceptance
is in [Slices 8–10](SLICES_8_10.md); foundation instructions are historical.

First verify workspace/permissions and existing evidence, then present layout,
element-level decisions, state/interaction matrix and implementation/verification
plan. Review before broad UI implementation. Preserve bounded Qwen presets;
history/media/sensor-rule fixtures remain visibly labelled.

- Implement the specified large live view, status, analysis, timeline and controls.
- Serve built assets locally; support external-screen fullscreen presentation.
- Support initial/paused, monitoring, review, urgent and unavailable states.
- Use explicit demo/source labels; keep diagnostics separate.

Complete when every displayed control works and each state has understandable
copy. UI-only fixtures remain labelled; they are not model-integration evidence.

## 3. Event engine and evidence

- Add timestamped, labelled simulated bell, vibration and contact inputs.
- Implement debouncing, duration tracking, evidence-based severity and expiry.
- Pass actual structured facts to Qwen for explanations and event-history questions.
- Keep evidence and severity authoritative; use templates on LLM failure.
- Discard stale generation and keep alert processing responsive during requests.
- Keep urgent events visible during camera/model outages.
- Add local event metadata; implement explicit media storage/replay and deletion.

Complete when alerts trace to recorded inputs and available evidence can be
inspected. Acknowledgement is separate from resolving an event or training a model.

## 4. Incremental face, posture and object analysis

- Add visible facial-movement and pose models one at a time after resource checks.
- Expose only supported objects and tested movement/posture descriptions.
- Label missing/occluded evidence. Do not infer identity, emotion or dangerousness.
- Defer hood/dark-glasses classification until a suitable local model is validated.

Complete each feature separately on held-out attempts. Do not claim all features
passed merely because one model runs. Reduce model frequency before expanding
downloads or adopting a large vision-language model.

## 5. Offline and failure acceptance

Follow [demo and acceptance](DEMO_AND_ACCEPTANCE.md). Restart the application with
all external connections disabled. Exercise fresh camera inputs, simulated
sensors, alerts, local history and failure states. Record measurements and actual
outcomes, including blockers and failed checks.

Complete when the core workflow is demonstrated offline and external requests
have been checked separately. Documentation or source inspection alone cannot
prove runtime network behaviour or security effectiveness.

## 6. Reproduction and submission

- Write actual start instructions after the implementation works; verify them.
- Prepare a model/tool/asset disclosure and clearly distinguish simulation.
- Include the actual local LLM adapter, prompts/schema, fallback checks and
  reproducible Ollama/model setup in the GitHub repository; exclude weights/media.
- Show genuine local request/response evidence and actual model/timing diagnostics.
- Record the working prototype; prepare an on-site laptop demonstration.
- Prepare the repository and social video locally. Publication and submission
  require internet separately and are not part of the offline runtime.
- Follow the briefing deadline and code freeze; do not imply submission occurred.

## Deferred work

Physical ESP32 camera/sensors and local Wi-Fi integration; embedded inference;
two-way intercom; continuous unattended operation and recovery; authenticated
device provisioning; mobile alerts; supervised training and household adaptation;
evaluated RL notification policies; language-model training or fine-tuning.

No task is considered passed until its required evidence exists. Missing model
files, unsupported hardware and unavailable live tests are Blocked, not Passed.
