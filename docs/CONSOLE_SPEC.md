# Indoor console specification

## Current simplified face demo

The [two-scenario face demo](FAMILY_REFERENCE.md) supersedes the activity workflow
below. Left controls provide parent Child safety mode, face enrollment/preview
and deletion. Fresh
LBPH matches drive Family member/Unknown analysis and child recommendations.
One automatic AI Analysis panel exposes the verdict, child recommendation,
enrolled example count and measured distance/threshold. Training/comparison
timing is expandable; no tabs or manual questions appear. A live camera banner
shows the current guidance. Child safety mode is a parent-controlled switch that
gates guidance while learning/recognition continue in both modes. Distance is
not a confidence probability. Sensor and manual selection APIs return 410 in
production. Occupancy cannot emit an alert.

## Historical child-mode contract (superseded)

This update supersedes earlier arming, door-open urgency and visitor-label wording
below. Parents manually Enable/Turn off Child safety mode; camera viewing and
analysis remain usable while mode is off. It defaults off and Stop/reset turn it
off. Turning it off clears pending inputs but preserves active alerts until expiry.
The switch is parent-facing, not authenticated parental access.

Simulation is one doorway-visit workflow: enable mode, Start/show a real visitor,
choose **Family member** or **Unknown**, confirm the current snapshot, set contact
closed, then use bell/impact controls. These are the only current categories.
Family member is manually parent-confirmed for an exact frame/time, not recognized
from a family database or carried to later frames. Unknown alone is not suspicious.
Confirmation expires within 60s and does not lower activity severity. One ordinary
knock can remain green/no configured alert; green does not grant permission to open.

Urgent now requires **fresh actual camera person detection + three accepted
simulated impacts on a continuously known closed door within five seconds**, while
mode is on. It fires before opening, with laptop_webcam and simulated_sensor facts.
Missing/stale person evidence (<0.8s freshness required) prevents combined urgent;
new genuine detection can complete still-pending impacts. Opening clears pending
impact sequences but not existing alerts. Open-door guidance says to step back and
get a parent; closed-door guidance says keep it closed and ask a parent. Bell
(3/10s), fresh occupancy (30s), debounce (250ms), review/urgent expiry (60/120s)
remain unchanged. Rule ID is person_closed_door_impacts; old saved event facts and
IDs remain untouched. Qwen explains supplied evidence; it does not see images,
set severity, recognize family, identify who caused impacts or infer hostile intent.

The impact button cannot distinguish gentle knocks from force; three ordinary
knocks can meet the unvalidated demo threshold. Camera corroboration is presence,
not recognition of striking/handle manipulation. Source/static/in-process evidence
is distinct from the pending genuine combined camera/Qwen/browser/offline checks.
[Ordered owner sequence](SIMULATION_CONSOLE_ACCEPTANCE.md).

Implemented through Slices 5–7; see [delivered contracts and owner acceptance](SLICES_6_7.md).
Now extended with [Slice 8 dashboard/scene contracts](SLICES_8_10.md).
Target features elsewhere in this specification are not implied to be delivered.

Status: owner design approved and Slices 5–7 implemented. Production is now
service-backed only, with no synthetic presentation selector or canned answers.
Sensor inputs remain explicitly simulated and run actual rules. History, explicit
JPEG evidence and feedback are implemented; optional face/pose/additional objects
have source implementation but still need model preparation and genuine validation.
[MVP audit and next owner checkpoint](MVP_READINESS.md).

## Product experience

The owner-authorized [Family member reference](FAMILY_REFERENCE.md) lives inside
the visit workflow. Save requires a fresh single-person frame and available face
analysis; preview/delete are explicit. It persists through Stop/reset/restart,
without automatically matching future visitors or changing severity. The larger
visitor-memory/learning simulator is still being designed.

Visit interpretation separates current/historical evidence and a parent-confirmed
snapshot from identity in later frames. It shows rule/advisory conclusions, gaps
and next actions. Suspicious-intent likelihood is explicitly unestimated rather
than a fabricated percentage. Qwen remains a separately labelled evidence selector.

The resident should understand three things at a glance: what is outside, what
needs attention, and why. The main experience is the indoor console. Laptop
webcam input stands in for the exterior camera; the demo screen is an external
display in extended-display mode where possible.

Use a polished dark surface, large readable typography, generous spacing,
restrained overlays and smooth changes between states. Use locally bundled
fonts/icons; respect reduced-motion settings. Labels and icons accompany colour.
Verify the layout on the actual external screen, not only a development viewport.

## Layout and elements

The approved simulation console uses three visible Overview columns: persistent
simulation controls/settings, a somewhat smaller live camera, and the assessment
with Scene/Qwen/Evidence tabs. Overview/Events navigation is in the header beside
the grouped Start/Stop/Fullscreen/Diagnostics/Reset controls. Inputs has no overlay
or trigger; Diagnostics remains an optional overlay. Recent records have a dedicated
Events view with actual local metadata/media/feedback.
The approved interactive dashboard adds actual count/detector-score/latency metrics,
Scene/Qwen/Evidence tabs, camera corner brackets and expandable findings. Limits
and session counters live in the simulation column. Face availability remains separate
from alert severity and does not recognize family. See [current contract](SLICES_8_10.md).
Ask and acknowledgement remain next to their evidence. Header panels
open beneath the toolbar without changing the workspace size. Revised browser
visual/interaction acceptance is pending; see [MVP readiness](MVP_READINESS.md).

Essential simulation controls and rule progress stay expanded. Owner snapshot
confirmation and rule/assessment details are compact expandable sections. Input
feedback has a timestamp and accepted/ignored colour, distinct from review/urgent
alerts. Sensor provenance remains explicit. At narrow widths the panels stack;
desktop fit and all control/focus interactions require owner browser acceptance.

Contact, recent replies and progress come from backend session state, including
after browser refresh. Contact begins unknown and retains the last accepted
transition through disarm; disarm clears qualifying inputs and recent replies.
Reset clears contact to unknown and clears active demo alerts, preserving saved
history/feedback/media and finalizing an explicitly started clip through Stop.
Arming alone creates no event. An already-open contact must close/reopen to supply
a new qualifying transition after arming/cancellation or expiry.

| Element | Behaviour and purpose |
| --- | --- |
| Header | DoorSense, selected entrance, camera availability, subtle local-processing indicator |
| Event status | Green Monitoring, orange Review needed, or red Urgent event, with reason and timestamp |
| Live view | Largest panel; restrained person/object overlays; no overlay for unimplemented detection |
| Analysis card | Current contract: Qwen-selected evidence with original fact/template wording, authoritative reason/source/uncertainty; separate generating, fallback and application-unavailable states |
| Ask about events | Initial UI exposes only tested event-question presets; free-text and history retrieval are deferred; no claim to see images |
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

Current adapter permits exactly: Explain this event; What was observed; Why does
this event require review; Which evidence supports the existing urgent event.
Use the exact strings/punctuation from `QUESTION_PRESETS` in the backend. Other
questions return `application_unavailable` without a Qwen call. Model-only name
abstention failed; never present this application guard as a model success.
Source `qwen_evidence_selection` means actual accepted selection with supplied
wording; `template_fallback` and `application_unavailable` have separate labels.
No unrestricted generated explanation or free-text history QA is implemented.

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
