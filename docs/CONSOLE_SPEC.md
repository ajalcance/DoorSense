# Indoor console specification

Status: design specification; no rendered console yet.

## Product experience

The resident should understand three things at a glance: what is outside, what
needs attention, and why. The main experience is the indoor console. Laptop
webcam input stands in for the exterior camera; the demo screen is an external
display in extended-display mode where possible.

Use a polished dark surface, large readable typography, generous spacing,
restrained overlays and smooth changes between states. Use locally bundled
fonts/icons; respect reduced-motion settings. Labels and icons accompany colour.
Verify the layout on the actual external screen, not only a development viewport.

## Layout and elements

| Element | Behaviour and purpose |
| --- | --- |
| Header | DoorSense, selected entrance, camera availability, subtle local-processing indicator |
| Event status | Green Monitoring, orange Review needed, or red Urgent event, with reason and timestamp |
| Live view | Largest panel; restrained person/object overlays; no overlay for unimplemented detection |
| Analysis card | Qwen explanation alongside authoritative observations, reason, evidence and uncertainty; explicit template fallback |
| Ask about events | Bounded questions about supplied local history, such as “What happened at my door?”; no claim to see images |
| Event facts | Arrival/occupancy duration and actual or simulated bell/contact counts |
| Resident controls | Start/stop, acknowledge, inspect evidence, replay available media |
| Timeline | Recent timestamped events, severity, source and evidence availability |
| Diagnostics drawer | Actual vision/LLM model identity, Qwen digest, request/inference timing, frame age, source mode and asset status |
| Demo controls | Clearly labelled simulated doorbell, impact and contact events; separate from resident controls |

The main screen should explain events without scattering model statistics. Put
technical details in diagnostics. The local-processing indicator is descriptive,
not a claim of proven network isolation.

## State contract

| State | Label and meaning |
| --- | --- |
| Initial | Monitoring paused; camera not started |
| Green | Monitoring; no configured alert conditions detected |
| Orange | Review needed; show specific triggering event |
| Red | Urgent event; show corroborating evidence and review controls |
| Grey | Assessment limited/unavailable; show affected component and recovery action |

Availability and severity are separate. Red remains visible if the camera fails.
Unknown/limited video assessment never becomes green merely because detections
stopped. Do not display Safe to open, Friendly visitor, Dangerous person, or a
percentage estimating dangerousness from appearance.

## Whole-scene observations

Candidate features: person presence, visible facial movements, body landmarks,
standing/crouching descriptions, movement within the doorway zone, and supported
carried objects. Each feature needs actual model output and validation.

Backpacks/handbags/suitcases are candidate supported object classes. Hoods and
dark glasses require a separate validated model; show Feature unavailable until
implemented. Clothing/object descriptions do not raise alert severity. Describe
occlusion and uncertainty without inferring personal identity or intent.

Frame the camera to include torso and hands for posture demonstrations. Full-body
analysis requires full-body visibility. Objects behind the visitor may be unseen.

## Interactions and evidence

Start monitoring requests camera access; permission denial has a useful recovery
message. Stop monitoring releases the camera. Acknowledge marks the alert and
stops its sound without deleting history. Replay is available only when real
local media exists; an event with metadata only must not imply a saved clip.

Feedback options: Useful alert, Unnecessary alert, Incorrect detection. Save
explicit labels with their event references; do not claim the model retrained.
No response remains unknown. Two-way intercom, door unlocking, face identification,
mobile push and continuous learning are outside the initial console scope.

## Local explanation behaviour

Generate short explanations through Qwen3 0.6B on new events or resident requests.
Show generating, local-model response and template-fallback states clearly.
Keep the live view and alerts responsive; LLM failure cannot hide an urgent event.
Explain only supplied facts, preserve simulation/replay provenance and show
missing evidence explicitly. Discard responses belonging to superseded events.
The model cannot change severity or decide whether the resident should open.
Diagnostics must report actual values, never placeholder inference evidence.

## Design acceptance

Check every visible control for necessity, clear wording, working action,
keyboard focus, contrast, spacing and display fit. Cover camera permission
denial, model missing, partial visibility, camera loss, urgent alert plus camera
loss, acknowledgement, and available/unavailable evidence. Simulated sensors and
replay inputs stay clearly labelled throughout the recording.
