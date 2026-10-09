# DoorSense transition to Slice 5

Snapshot: 2026-10-09, Asia/Manila. The owner requested a new chat for Slice 5.
This handoff authorizes continuation preparation and a console proposal, not
silent UI implementation before the owner sees the design. No Slice 5 code was
created in the handoff session.

## Read and verify first

Use the existing checkout:
`/Users/anymind/Documents/ChatGPT/Albert Space 2/Hackathon/DoorSense`.
First read README.md, WORKING_PLAN.md, docs/CURRENT_STATE.md and this handoff,
then docs/CONSOLE_SPEC.md, docs/BUILD_PLAN.md, docs/ARCHITECTURE.md,
docs/SANDBOX.md and docs/LLM_SPIKE.md. Inspect applicable AGENTS.md if present.
Treat source code and current session permissions as authoritative; this is a
snapshot, not permission to override the next session environment.

Verify cwd/repository, Git status, active filesystem roots, protected paths,
approval mode and command networking. Last confirmed: branch main, origin
https://github.com/ajalcance/DoorSense.git, dirty/uncommitted implementation and
docs. Preserve all changes and ignored local assets. Do not reset, clean,
checkout another branch, create a worktree or discard files. `.git` is protected;
no commit/branch/push was performed. Public/remote synchronization is unverified.

The selected doorsense profile in this session has workspace-write and approval
policy never. Writes are confined to DoorSense, /private/tmp and the OS TMPDIR
(`/private/var/folders/cj/qp3wb8ts3hl_vnn5zdb0lgh40000gn/T`). Repo .git, .codex,
.agents and .aws are read-only. Other filesystem paths are readable. The attached
visualization directory has no write grant. Command networking, including
loopback, is blocked; never means no escalation/approval escape, not full access.
Do not request sandbox_permissions, change profiles or disable protection.

The owner trusted PreToolUse and PermissionRequest hooks. Native boundary probes
previously passed; the gate rejected destructive commands and escape requests.
Hooks are supplementary accident guards, not complete shell parsing or an app
sandbox. If a hook cannot parse a documentation heredoc, use a clear scoped
apply_patch; never disable the gate. Verify current session state without repeating
destructive probes or changing security setup. Browser/connectors have separate
permissions; do not treat them as a command-network workaround.

## Product and current code

M1 MacBook Air, 8 GB, macOS 14.1.2 ARM64. Real laptop webcam substitutes for a future
ESP32 camera. Labelled simulated sensors are later work. The resident console
targets a cable-connected external display; actual display size/configuration
has not been confirmed. Core offline operation is a target, not passed acceptance.

- Slice 1: read-only preflight complete.
- Slice 2: packages/assets/imports and owner Ollama startup/metadata verified.
- Slice 3: genuine person inference and basic owner camera lifecycle confirmed.
- Slice 4: bounded Qwen adapter ready for integration; see limits below.
- Slice 5: console foundation/design review is next; frontend has no app source,
  Vite config, build scripts or rendered console yet. No full application server.

Existing code: backend/doorsense/camera.py, vision.py, local_llm.py;
scripts/camera_spike.py, llm_spike.py, start_ollama.py and check_runtime.py.
No event engine, real sensor controls, persistence, recording, replay or feedback.
Use existing React 19.3.0/React DOM, Vite 8.3.4 and plugin-react 6.1.2 packages/lock.
Python .venv is 3.12.13; existing Node 22.23.1 is at
/opt/homebrew/opt/node@22/bin/node. Default shell Node/Python differ; explicitly
use the repo .venv and Node 22. No dependency installation, upgrade, model download
or new UI framework is required for warm-up/design.

MediaPipe 0.10.21 has a retained vendor-wheel metadata exception: original
universal2 wheel internally says Intel-only. runtime_health.py verifies exact
publisher archive/native bindings/imports. Raw pip check still reports that
mismatch; do not edit vendor metadata or reinstall to suppress it.

## Evidence and integration constraints

Camera: latest clean owner run captured 156/analyzed 46 frames, all analyzed
frames had person results; 4.21 analyzed frames/s, median 34.06 ms, P95 36.37 ms,
peak process RSS 339.8 MB, release true and no errors. Owner separately confirmed
boxes disappear on leaving view, P turns the camera light off, S restores live
preview. These are basic acceptance, not comprehensive miss/false-positive quality.
Webcam.start must open/configure AVFoundation on the main thread; only reads run
in the worker. A first-start permission failure from worker opening was fixed.
Do not call start from a FastAPI worker thread. Propose the service/camera control
bridge explicitly if needed; explicit Start/Stop and release remain required.
One latest frame, matching analyzed frame/overlays and 0.8-second freshness are
existing contracts. Never put old results over a newer unrelated frame.

Qwen: Ollama 0.40.1, model qwen3:0.6b, Q4_K_M, manifest digest
7df6b6e09427a769808717c0a93cadc4ae99ed4eb8bf5ca557c90846becea435.
Last observed in this handoff session: owner daemon PID 62540 listening only at
127.0.0.1:11434. Process state is drift-prone; recheck, do not restart/kill blindly.
Cloud-disabled startup was owner-verified, but external traffic/offline isolation
are unverified. Owner launcher models are repo-local; Ollama creates identity
keys under ~/.ollama outside this Codex sandbox. Owner Terminal is not sandboxed.

Latest genuine v3 test: four supported examples worked; model-only identity
abstention failed (4/5). Cold 1951.31 ms; warm bell 172.08/168.62 ms; urgent
285.70 ms. Concurrent real detector on blank pixels: 14 samples, median 18.83 ms,
P95 38.41 ms, no errors, no camera. Spike RSS 174.2 MB, sampled Ollama/child RSS
419.1 MB; do not sum these as physical unified memory. Loaded model metadata
reported context 2048 and size/VRAM 793,719,603 bytes. These are short spike figures,
not complete console/live webcam performance or zero-telemetry evidence.

Current prompt evidence-selection-v3 selects fact IDs (or unavailable alone).
Original fact/template wording is rendered; no unrestricted generated prose.
Application guard now accepts only these exact tested presets (case/outer-space
normalization is allowed):

- Explain this event.
- What was observed?
- Why does this event require review?
- Which evidence supports the existing urgent event?

Other questions return application_unavailable before any HTTP call, with empty
evidence and no model claim. Fifteen injected fixture tests passed, including this
boundary. Do not add a free-text box or pretend the model learned abstention.
Event-history retrieval is deferred. Model-only failed reports remain failed.
Latest ignored .runtime/llm-session.json predates the guard and records 4/5;
preserved first/v1/v2/v3 reports are listed in docs/LLM_SPIKE.md. Revised runner
would report four generations plus one application guard; it has not been owner
rerun and must not be described as five successful Qwen generations.

Requests use think false, stream false, num_ctx 2048, num_predict 128, temperature
0, 45-second total deadline, 60-second freshness, one shared adapter/one client
request slot and no queue. Supply is_current(event_id, revision) during integration
to discard superseded results. Client cancellation does not prove server work
stopped. Preserve qwen_evidence_selection, template_fallback,
application_unavailable and discarded as distinct states; rejected raw diagnostics
never belong in resident answers. Severity/reason/source/uncertainty are authoritative
outside Qwen. No identity, emotion, intent, danger percentage or safe-to-open claim.

## Slice 5 scope and first response

First report verified workspace/permissions and a short evidence summary. Then
show a concrete console concept: layout/wireframe, visual direction, an element
table explaining each control, the state matrix, fixture/live boundaries, and a
focused implementation/verification plan. Review typography, spacing, placement,
copy, necessity, keyboard/focus, contrast and external-display fit. Obtain design
approval before broad UI code. Once approved, proceed without repeated permission
requests for routine reversible work within that scope.

Prioritize the large live-view area, clear availability plus separate severity,
concise supporting facts/reason/uncertainty, explicit monitoring controls and
source labels; expandable diagnostics keep model statistics out of the main flow.
Dark restrained surface, readable type, locally bundled assets and reduced motion.
Use supported preset questions, not free-text QA. History/media/feedback/face/pose
features need honest unavailable states or omission, not invented outputs.

Cover initial/paused, monitoring, review, urgent, unavailable, and urgent plus
camera unavailable. Foundation fixtures must be visibly labelled UI fixture;
synthetic urgent/review states are not implemented sensor-rule evidence. Missing
clips cannot offer working replay. Do not silently expand into Slice 6 event rules
or Slice 7 persistence/media. Propose the minimal local service/real-camera bridge
if needed for functional controls, and distinguish fixture UI acceptance from
genuine integrated camera/model acceptance. User camera access requires explicit
Start; no automatic monitoring or stored footage.

## Ways of working and owner operations

- One slice/checkpoint at a time; keep the original objective and accepted limits.
- Show a plan before material UI/security/product changes. This new chat begins
  with read-only warm-up and UI review, not installation or silent implementation.
- Use concise progress updates; explain what changed, how checked and what remains.
- Prefer action after scope approval; avoid repetitive permission questions.
- Preserve dirty work. Writes only to DoorSense/temp; protected metadata stays read-only.
- No new dependencies/downloads/cloud/service exposure/publication without the
  necessary owner decision; never broaden sandbox permissions to make tools work.
- Use meaningful scoped checks; do not repeatedly rerun passing spikes without
  changes/failures or a new acceptance question. Fixtures do not prove live acceptance.
- Distinguish planned, implemented, fixture-checked, owner-confirmed, model-only
  failed, integrated rendered, and offline evidence. Unavailable tests are blocked,
  not passed. Keep source/simulation labels visible at every stage.
- Owner commands: provide one complete paste-ready block starting with the exact
  cd path, name the Terminal to use, expected result and report-back. Say whether
  a Codex/Ollama restart is needed. Existing Ollama Terminal can stay running.
- Network/service/camera checks require owner Terminal under the current policy;
  commands there are outside the Codex sandbox. Never silently kill an existing
  daemon, change TCC permissions or start capture. No restart is routinely needed
  for code/docs changes; security-settings reload is a separate owner operation.
- UI-only steps: give click-by-click directions. For visual QA use fixture data;
  do not save real camera imagery as screenshots/recordings without explicit consent.
- Update current state, setup/acceptance/disclosures after genuine new evidence.
  Documentation-only check: python3 scripts/check_docs.py plus git diff --check.

Future slices: 6 sensors/events/rules; 7 history/media/feedback; 8 incremental
face/pose observations; 9 offline/failure acceptance; 10 reproduction/demo/submission.
The briefing deadline is 2026-10-10 10:00 AM Philippine time; code freeze and
organizer acceptance of simulated hardware require honest handling. No demo,
social publication, submission or remote code synchronization is established.

## Source fingerprints at handoff

SHA-256; reverify cheaply if source state differs. These fingerprints identify
the current working files, not committed/remote content.

| File | SHA-256 |
| --- | --- |
| backend/doorsense/camera.py | cd15c066d920c34da3deff37dc2000813c36a127aa88afaca449297c1e02492b |
| backend/doorsense/vision.py | a183f7c358739af39408cbc9c84186436cd02d356d4846fb8fffb7106e235ba4 |
| backend/doorsense/local_llm.py | 41fd2aa8d1488911c289c51b1a7023ba302a0fdbe003b50ee2d91e43cd9295c0 |
| scripts/llm_spike.py | 7f7f62054e209fe572091a4ec70280d0964ab8ff96845ca023fd19626a95f75c |
| assets/runtime-manifest.json | 3684ba6c0005066f29ec6b674623019bef5d1fb4f0ad7726c9b7a9954d6bbc4a |
