# DoorSense current state

For a concise current technical handoff, use the [technical overview](TECHNICAL_OVERVIEW.md):
delivered features, evidence boundaries, installed stack and focused roadmap.

## Current demonstration: face enrollment and recognition

The latest [two-scenario face demo](FAMILY_REFERENCE.md) supersedes activity
controls and manual category selection below. Installed OpenCV LBPH learns one
parent-enrolled crop locally, then compares fresh appearances as Family member
or Unknown. The console shows measured distance, camera facts and child guidance.
Parent-controlled Child safety mode gates child guidance independently of
recognition. Sensors and manual visitor selection return 410 in production;
occupancy cannot emit alerts. A live camera banner and one automatic AI Analysis
panel replace the tabs/manual questions. Old event history remains. This is supervised
enrollment, not RL or friendly-intent recognition. Synthetic fit/predict checks
do not establish live human accuracy; owner camera/offline trials remain pending.

## Historical child-mode contract (superseded by face-only demo)

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


Updated: 2026-10-10, Asia/Manila.

This document records delivered work and current evidence. Planned features
belong in the working plan and specifications.

Latest owner-authorized addition: [local Family member reference](FAMILY_REFERENCE.md)
with explicit save/preview/delete, persisted separately from event history. No
owner photo was captured in this command session. Local LBPH enrollment/matching
now supersedes the former photo-only feature; RL remains unimplemented.

Scene now includes an application evidence interpretation, supporting facts,
missing evidence, next action and an explicit unestimated intent-likelihood field.
It does not invent risk percentages. Qwen can receive current sensor facts alongside
camera/snapshot evidence; changed/expired activity discards pending responses.
Actual Qwen selections keep their separate response-source labels. These changes
are source implementation, not a new genuine Qwen or learning acceptance claim.

## Current checkpoint snapshot

| Slice | Current evidence |
| --- | --- |
| 1: preflight | M1 8 GB/macOS 14.1.2 ARM64; existing Python 3.12.13 and Node 22.23.1 inventoried |
| 2: preparation | Pinned packages/imports, local asset integrity and owner Ollama startup/metadata passed |
| 3: camera spike | Genuine webcam/person inference and basic owner entry/exit, physical pause/restart confirmed |
| 4: bounded Qwen spike | Four genuine supported v3 examples worked; 15 fixture checks passed; application guards unsupported questions |
| Model-only abstention | Failed name question in v2/v3; not counted as a successful Qwen answer or repaired model behavior |
| 5: console foundation | Owner layout reviewed; foundation audited and defects corrected; source/fixture checks passed; full rendered/genuine integration pending |
| 6: simulated sensors / rules | Timestamped labelled inputs, debounce, occupancy duration, review/urgent rules, independent availability and bounded explanations implemented; synthetic integration passed |
| 7: local history / evidence | SQLite events/acknowledgement/feedback, explicit snapshots/JPEG clips, replay/deletion and pagination implemented; temporary-store/API/session checks passed |
| 8: incremental scene / dashboard | Optional Face/Pose local tasks and supported bags, stabilized conservative descriptions, per-feature failures/budgets, interactive Scene/Qwen/Evidence tabs and camera HUD implemented; new assets/genuine quality/resource checks missing |
| 9: offline / failure acceptance | Owner acceptance template/reviewer and expanded injected integrated workflow tests implemented; disconnected restart/traffic/live failures not run |
| 10: reproduction / demo | Private-safe source inventory, exact restart/acquisition commands, two-scenario runbook and submission draft prepared; clean-machine reproduction, licensing, video/publication/submission pending |

Latest owner report predates the application guard: `.runtime/llm-session.json`
still records v3 model-only 4/5 and needs_review. The revised runner would check
four generations plus one application guard; it has not been owner-rerun. Those
are distinct evidence claims. The four supported model calls need no repetition
for this documentation handoff. Full offline/live failure/product acceptance is pending.

Continuation: [Slice 5 handoff and ways of working](HANDOFF_SLICE_5.md).

Current implementation: [Slices 8–10](SLICES_8_10.md), building on [Slices 6 and 7](SLICES_6_7.md), following the
[console audit](SLICE_5_AUDIT.md). Owner authorized these slices after requesting
an implementation audit. Existing dirty work and local assets are preserved.

The production console uses explicit Start/Stop and exact assessed image/overlay
packets expiring at 0.8 seconds. Separately armed prototype rules create real local
records from labelled simulated sensors or sustained genuine person observations.
Urgent outranks review and survives camera loss/disarming until explicit expiry.
Acknowledgement does not resolve severity or erase evidence.

SQLite stores event facts, acknowledgement, feedback and explicitly saved media.
No footage is stored automatically. Snapshot/clip capture applies only to the
current active event; replay uses actual recorded JPEG frames without inference.
The production console is now service-backed only: no synthetic scenario selector,
canned answers or standalone preview. The five obsolete presentation/preview
paths were confirmed absent on 2026-10-10; historical gate-blocked cleanup is in
[the earlier MVP audit](MVP_READINESS.md).
Four preset questions remain the only question interface; recent selected history
can be supplied, while context older than 60 seconds returns application unavailable.

Latest simulation-console automated run passed 109 backend, 32 frontend and 43 static markup checks,
production build, bundle invariants and docs links. Results/fingerprints are in ignored `.runtime/source-audit.json`,
generated by `scripts/audit.py`; [current audit](SLICES_8_10_AUDIT.md). The prior
Slices 1–7 baseline was 76 backend, 24 frontend and 25 static markup checks.
No genuine device, new model or network is accessed by these automated checks.
Browser policy blocked loopback and file preview: rendered audit is Blocked in Codex.
The owner's 2026-10-09 23:46 screenshot shows integrated genuine webcam/box/count
and Qwen-selected evidence. Actual database/media/restart, new dashboard rendering,
face/pose quality, combined M1 resources and offline acceptance remain pending.
Model-only identity abstention remains failed.

The approved family demo keeps green face analysis availability distinct from
identity; grey limited analysis asks for parent review. Active amber/red rules show
parent-contact guidance even without Qwen or camera availability. A manually
owner-confirmed expected-visitor snapshot has frame/time/source and a 60s bound;
it is not recognition of later frames and cannot lower an alert's severity.
The owner chose lightweight analysis: no VLM, cap/glasses classifier, face enrollment,
emotion inference, audible siren or automatic parent phone call is implemented.

Approved simulation-console implementation on 2026-10-10 replaces the left
navigation rail with persistent controls/settings and moves Overview/Events into
the header. Overview has controls, smaller camera and right analysis columns.
The Inputs overlay/trigger is removed; Diagnostics remains optional. Contact,
rule counts/windows and recent accepted/ignored replies come from backend session
state and survive browser refresh. Cancellation retains simulated contact while
clearing pending evidence; reset clears contact, active alerts and temporary state.
Existing rule thresholds, camera/Qwen/storage scope are preserved. The prior
source-audit report was copied to a uniquely named ignored backup before rerunning.
[Ordered owner checks](SIMULATION_CONSOLE_ACCEPTANCE.md) remain unrun for this layout.

The continuation handoff reports genuine owner face availability, Parent/Family
member snapshot annotations with original frame/time and owner_label provenance,
Qwen-selected evidence with model/timing, sustained-person amber review/parent
guidance and three matching sustained-occupancy history records with zero saved
media. These are owner-reported partial observations, not a new runtime validation
in this session. The latest red flow lacked a door-open input and remains unverified.
Banner navigation, revised layout, offline restart, saved-media workflow,
pose/object quality and full integrated acceptance remain pending.

The paragraphs below retain the earlier UI review and spike history.

Owner screenshots confirmed the initial paused console renders, but showed the
camera/card sizing pushed the lower controls below the window. On owner request,
the layout was compacted: desktop viewport-height sizing, shorter card spacing,
slim recent-events/footer rows and overlay diagnostics/fixture panels. The native
preview's incorrect "Press S" guidance was replaced with Start button copy.
The revised production build passed; revised visual fit and full fixture/live
acceptance are pending. No camera/backend behavior changed in this adjustment.

The owner reviewed that compact layout and approved a structural redesign:
left Overview/Events navigation, header global controls, aligned live-view and
unified assessment panels, dedicated Events view, and anchored Diagnostics/Demo
panels. This latest layout is implemented. Start/Stop remain explicit and available
from either view; entering UI fixture mode still requires confirmed camera release.
Source labels, preset-only answers and urgent/unavailable separation are retained.
Production build, two frontend fixtures and 16 server-rendered markup smoke checks
passed. These are markup checks, not browser visual/keyboard or genuine integration
acceptance. Owner refresh/review is next; no backend/asset/dependency changes.

The next owner screenshot confirmed the redesigned paused Overview renders.
On owner request, a further styling pass widened desktop navigation to
176–208 CSS pixels, reduced body text to 14 px, section headings to 16 px and
status text to 20 px, balanced the camera/assessment proportions and softened
secondary borders. The production build passed. This is source/build evidence;
revised visual fit, fixture interactions and genuine integration remain pending.

## Confirmed decisions

- User-approved product: a local doorway safety assistant with an indoor console.
- User-approved prototype: laptop webcam, local AI, external display, simulated
  door sensors, no internet required during core operation.
- User-confirmed computer: Apple M1 with 8 GB unified memory.
- Resource preference: smallest practical downloads.
- User-approved local LLM: Qwen3 0.6B via Ollama for explanations and local
  event-history questions, with short output, thinking disabled and template fallback.
- GitHub deliverable must expose genuine local LLM integration and offline setup;
  repository: https://github.com/ajalcance/DoorSense . Runtime integration is pending.

## Delivered and historical evidence

Entries below record the sequence of prior checkpoints. Earlier pending actions
are superseded by later results and the current snapshot above.

- Updated working plan preserving the future roadmap.
- Project README, judge guide and documentation index.
- Dedicated Hackathon/DoorSense workspace and repository scaffold, with
  ignore rules, contribution guidance and documentation-link checker.
- Offline architecture and component contracts.
- Console layout, state and interaction specification.
- Ordered implementation checkpoints.
- Offline acceptance and demo disclosure checklist.
- Qwen/Ollama integration specification, resource checks and GitHub evidence plan.
- Slice 1 read-only inventory: MacBook Air M1 / 8 GB / macOS 14.1.2 ARM64,
  existing Python 3.12.13 and Node 22.23.1; about 9.4 GiB available. No Ollama,
  Qwen store or vision weights found in checked locations. Camera/display
  enumeration returned no device records; that does not prove devices absent.
- Slice 2 preparation: direct backend/frontend version pins, an asset manifest,
  repository-local Python 3.12.13 `.venv` with bundled pip, owner acquisition
  script, explicit foreground Ollama launcher and local import/asset/daemon checks.
  Thirteen focused path/integrity/archive/dependency checks passed. Plan-only
  commands passed. See [owner preparation commands](PREPARATION.md).
- Owner acquisition subsequently produced the backend hash lock and installed
  all direct backend pins. Live backend imports passed on ARM64. Acquisition
  initially stopped on MediaPipe 0.10.21's inconsistent universal2 wheel/internal
  Intel tag. A narrow project check
  verifies the exact published wheel SHA-256, installed primary native bytes
  and native imports before recording this metadata exception. It preserves
  vendor metadata and rejects all additional dependency failures. Raw `pip check`
  still reports the mismatch; no detector or camera inference is proven by imports.
- Resumed owner acquisition completed: npm integrity lock generated, all four
  frontend imports passed on Node 22, Ollama 0.40.1 official archive acquired
  (167,470,715 bytes), EfficientDet-Lite0 int8 v1 acquired (4,602,795 bytes),
  Qwen3 0.6B local layers acquired (522,653,767 bytes). Local archive/executable,
  vision and Qwen manifest/layer integrity checks passed again in this chat.
  Acquired full hashes are tracked in `assets/runtime-manifest.json`; per-layer
  receipts remain local. Qwen's acquired licence layer contains Apache-2.0.
  This is acquisition/import evidence, not model inference or offline acceptance.
- Slice 2 startup/metadata checkpoint passed in owner Terminal: Ollama 0.40.1
  serves the exact acquired `qwen3:0.6b` manifest digest. The supplied startup
  log reports `Ollama cloud disabled: true`, a listener on 127.0.0.1:11434 and
  Apple M1 Metal discovery. This chat independently observed only the loopback
  listener on port 11434 and read the saved passing metadata check. GPU discovery
  is not GPU inference evidence, and cloud-disable configuration is not a network
  firewall or an offline acceptance result. No camera or generation was invoked.
- Slice 3 implementation: explicit AVFoundation webcam worker with one latest
  frame, exact-hash MediaPipe person detector and native development preview.
  Nine fake-camera lifecycle/expiry/threading checks passed, including pause/restart,
  failed capture/release and stale-frame removal. No real camera was accessed.
  Model-only blank-pixel check in this command sandbox was Blocked on
  `Could not create an NSOpenGLPixelFormat`; owner Terminal model and webcam
  checks subsequently passed. See [camera spike](CAMERA_SPIKE.md).
- Owner model-only check passed in Terminal: load 145.16 ms, first blank-input
  inference 30.89 ms, warm calls 14.76-15.22 ms, peak RSS 157.3 MB.
  An initial camera permission request failed because device opening ran in a
  worker thread. Corrected Start opens/configures on the main UI thread; reads
  remain on the worker. Regression checks passed.
- Corrected owner webcam run: 156 captured / 46 analysed frames, all 46 with
  person results, 10.93 active seconds, 4.21 analysed frames/s, median 34.06 ms,
  P95 36.37 ms, peak process RSS 339.8 MB (excludes Ollama), release true and
  errors empty. Saved aggregate diagnostics match the supplied output. The owner
  confirmed boxes disappear on leaving the view, P turns off the camera light,
  and S restores live preview. Slice 3 basic checkpoint is complete. These owner
  observations are separate from aggregate counts; broader detection quality,
  live camera/model failure handling and offline acceptance remain pending.
- Slice 4 implementation: async loopback-only Qwen adapter, versioned prompt and
  dynamic fact-ID schema, unchanged rule severity/provenance, bounded context/output,
  single client request slot, deadline, labelled fallback and stale-event discard.
  Twelve injected HTTP tests passed; these are fixtures, not model responses.
  The owner runner prepares five genuine calls on synthetic event records and
  optional concurrent blank-pixel detector/RSS measurements. No camera is opened
  by that runner. Initial genuine owner calls ran; acceptance is partial; see
  [local Qwen spike](LLM_SPIKE.md). The initial contract selects supplied evidence;
  displayed wording is original facts/template, not unrestricted generated prose.
- First Slice 4 owner run matched the saved report: 2/5 synthetic examples met
  expected selection (arrival and urgent); bell, identity question and warm bell
  triggered invalid/unsupported-response fallback. Status is needs_review, not
  Passed. First request took 2914.58 ms with 2072.74 ms model load; accepted warm
  urgent request took 599.09 ms. The three fallback timings are not accepted Qwen
  answer benchmarks. The original report lacked raw rejection diagnostics; cause
  is not yet established. Opt-in bounded developer diagnostics are now implemented,
  with a twelfth fixture ensuring rejected text stays out of the displayed answer.
  Corrective diagnostics rerun is next; validation has not been relaxed.
- Diagnostic Slice 4 rerun again met 2/5 expectations. All three rejections combined
  unavailable with nonempty IDs under v1, with valid completion and no thinking/tools.
  V2 requests fact_ids only, derives answer_kind in the app, permits empty lists
  and adds one-fact bell/unsupported-identity examples. Twelve fixture checks pass;
  genuine v2 rerun is next. Invented IDs, extra fields and contradictory v1 outputs
  remain rejected. Cold request: 2250.98 ms; accepted warm urgent: 586.88 ms.
  Blank vision median 18.84 ms, P95 41.89 ms, 20 samples, no errors.
- Genuine v2 owner run met 4/5 expectations. Identity question still selected the
  presence fact, which is valid syntax but irrelevant to a name question. It did
  not invent a name, but the example remains failed. Cold request 1921.97 ms;
  accepted warm bell 170.67/177.91 ms; urgent 299.07 ms. Concurrent blank vision:
  14 samples, median 18.64 ms, P95 38.62 ms, errors empty. Spike peak RSS 174.5 MB;
  sampled daemon/children max RSS 442.1 MB (not a total physical-memory measurement).
  V3 now offers an explicit unavailable marker, rejects mixing it with facts or
  using it as an input ID, and retains the original identity-example expectation.
  Fourteen fixture tests passed. Genuine v3 semantics await owner rerun; Slice 4
  remains needs_review. V2 report preserved locally at `.runtime/llm-session-v2.json`.
- Genuine v3 owner run met 4/5 model-only expectations: all four supported event
  requests worked; name-question abstention again selected irrelevant presence
  evidence. This failed model-only result remains recorded, not marked passed.
  Cold request 1951.31 ms; accepted warm bell 172.08/168.62 ms; urgent 285.70 ms.
  Concurrent blank vision: 14 samples, median 18.83 ms, P95 38.41 ms, no errors.
  Spike peak RSS 174.2 MB; sampled daemon/children max RSS 419.1 MB.
- Added application boundary: only four tested question presets may reach Qwen.
  Other questions return application_unavailable, empty evidence and no model claim
  before any HTTP call. Fifteen fixture tests passed, including zero network calls
  on unsupported name/intent/emotion/door-permission or instruction-appended questions.
  Supported Qwen prompt/schema are unchanged from the v3 genuine run. Bounded
  adapter is ready for console integration; free-text/history QA and general model
  abstention remain unverified. Runner now distinguishes four generation cases
  from one application guard; it cannot count the guard as a Qwen response.
- Concurrent genuine blank-pixel vision in the first run: 24 samples, median 17.71 ms, P95 22.62 ms,
  errors empty. Spike process peak RSS 172.9 MB; sampled Ollama/children max RSS
  546.5 MB. These must not be summed as total physical unified memory. Loaded-model
  metadata reports context 2048 and 793,719,603 bytes size/VRAM; no complete console
  or live webcam responsiveness measurement is established by this run.
- Prepared [development sandbox](SANDBOX.md), owner installer and checks:
  exact DoorSense/temp write profile, command network disabled, no sandbox
  escalation prompts, and a supplementary destructive-operation hook.
  Owner installation is confirmed; both hooks were trusted in the CLI and the
  gate is active in this desktop chat. After selecting `doorsense`, session
  metadata confirms writes only to DoorSense and OS temporary directories,
  protected metadata paths read-only, command networking restricted, and
  approval policy `never`. The visualization directory has no write grant.

Preparation evidence for the development sandbox: the policy assertions and
16 gate cases passed, including malformed-input rejection. Documentation links
passed. Nested native probes were blocked by `sandbox_apply: Operation not
permitted`; they are not enforcement evidence. After owner installation/restart,
a direct probe in the current desktop command sandbox passed: repo/temp writes
allowed; parent-directory, `.git`, `.codex`, symlink-escape writes and command
network access denied. The desktop hook rejected a no-argument `/bin/rm` call
before execution and rejected a sandbox escape request for `/usr/bin/true`.
These probes touched only newly created disposable files. After selecting the
exact DoorSense profile, the same direct sandbox checks passed again and the
live hook again rejected a no-argument `/bin/rm`. Installed config/gate files
match the prepared sources. No additional escalation request was attempted
under approval policy `never`.

## Not implemented or verified

- Complete camera lifecycle/quality acceptance, console rendered acceptance, event
  processing, storage, recording, replay, or feedback capture.
- Full Qwen example acceptance, semantic selection quality, live daemon failure
  acceptance, console/event integration and combined resource acceptance. Fixture
  timeout/fallback checks passed; those do not establish live model behavior.
- Vision asset-specific licence and independent publisher checksum, complete
  third-party licence review, general Qwen question quality and full combined resource use.
  Genuine initial vision inference passed; asset/import checks alone do not prove
  additional model functionality.
- Full application M1 memory use/latency, broader detection quality, or offline
  network behaviour. Initial camera inference timings are measured above.
- Actual camera resolution, external display configuration and physical ESP32
  board model. Owner camera access and basic lifecycle behavior worked.
- Physical ESP32 camera capture, sensor accuracy, firmware emulation or LAN integration.
- Continuous 24/7 monitoring, threat-detection effectiveness, model training,
  reinforcement learning, mobile notifications or automatic improvement.

## External condition

The supplied briefing does not explicitly settle eligibility of simulated
hardware. Organiser clarification is pending. A submission video is required;
finalists must also be prepared for an on-site live demonstration.

## Next checkpoint

Acquisition, dependency imports, foreground Ollama startup, cloud-disable startup
configuration, loopback listener and exact Qwen availability passed. Slice 3 basic
webcam/person-detection checkpoint is complete, including owner-confirmed
entry/exit and physical pause/restart behavior.
Bounded Slice 4 adapter is ready for integration: four genuine supported requests
passed and fifteen fixture checks passed. General model abstention failed on the
identity example; the application now refuses unsupported questions deterministically.
Slices 5–7 are implemented with the source/fixture evidence above. Next is ordered
owner rendered and genuine acceptance using [Slices 6 and 7](SLICES_6_7.md).
The original [Slice 5 handoff](HANDOFF_SLICE_5.md) remains historical context.
Disconnected restart and broader camera
quality/live failure handling remain separate acceptance checkpoints.

Current command networking is blocked with no escalation, so loopback daemon
checks require owner Terminal. Ollama's first startup writes identity keys to
`~/.ollama`; all models stay in DoorSense, and Codex's protected filesystem profile
remains unchanged. Vision asset licence confirmation and live telemetry/offline
checks remain pending. Slices 6 and 7 have source/fixture implementation evidence;
incremental vision code now forms Slice 8, offline acceptance tooling Slice 9,
and local reproduction/demo preparation Slice 10. Required live/owner evidence
remains incomplete; implementation alone does not complete acceptance.
