# Slices 1–7 MVP readiness audit

Historical 1–7 baseline. The owner expanded scope through Slice 10; current commands,
dashboard/model contracts and evidence are in [Slices 8–10](SLICES_8_10.md) and
[the cross-slice audit](SLICES_8_10_AUDIT.md). The rows below preserve earlier evidence.

Updated 2026-10-09. Owner scope: complete Slices 1–7, audit defects, prepare the
live prototype, then owner frontend acceptance. Additional vision models,
physical hardware, publication and submission are outside this implementation.

## Answers to the readiness questions

| Question | Finding | Evidence still needed |
| --- | --- | --- |
| Is the hackathon prototype ready? | The live-path implementation is ready for owner acceptance, not yet fully accepted. No production presentation mode or canned answers remain. | Rendered controls, genuine integrated inference/media and disconnected restart; hardware-simulation eligibility and vision licence review remain open |
| Is there evidence it works? | Genuine webcam spike: 156 captured / 46 inferred frames, 34.06 ms median, 36.37 ms P95, release true. Four supported genuine Qwen calls passed on supplied synthetic event records. Existing reports preserved. | A new integrated service evidence report, actual screen recording and acceptance outcomes |
| Can it handle a few webcam situations? | One webcam; person entry/count, person exit/count returning zero, and sustained fresh presence for 30 seconds. No identity, face/pose or additional object capability. | Owner reproduction in the console; misses/false detections remain unmeasured |
| Does local Qwen analyse them? | Qwen selects supplied detector/event facts using four presets. It is text-only and does not see images or decide severity. Accepted selection, fallback and application-unavailable remain distinct. | Fresh console responses labelled Qwen-selected evidence, actual digest/timing in exported evidence |
| Does it work offline now? | Runtime has local assets/UI, loopback inference, no CDN or cloud fallback. Provisioned bytes/imports passed recheck. | Offline acceptance remains NOT RUN: app/Ollama must restart disconnected and make a fresh genuine request; inspect external requests |

The model-only identity question failed. Application guards do not repair the
model. A no-person detection or no-alert status does not prove absence or safety.
This audit does not establish reliable 24/7 security performance.

## Slices reviewed

1. Workspace/protection: active project path/current managed profile; prepared
   sandbox/gate checks passed. Actual gate enforced file-deletion rejection.
   No protection changes, escalations, Git mutations or worktree creation.
2. Provisioning: existing Node 22/repo Python; imports, package pins and all local
   model bytes rechecked. Known MediaPipe publisher-wheel metadata exception
   retained and verified; no installation/download.
3. Capture/vision: main-thread macOS opening, worker capture, one latest frame,
   exact image/box packets, expiry, release/restart and person-only hash validation.
   Existing genuine owner reports inspected; no new capture performed here.
4. Qwen: exact model/version/digest, bounded context/output, deadline, single
   request slot, no queue, fact-ID validation, source labels, stale-result guards
   and deterministic unsupported-question rejection.
5. Console: compact Overview, dedicated Events, service-only operation, persistent
   action errors, disabled unavailable controls, ordered status acceptance and
   generation-safe responses/replay. No synthetic presentation in shipped assets.
6. Rules: labelled timestamped simulation inputs, debounce, armed gating,
   duration/window corroboration, severity separate from availability, expiry and
   acknowledgement. No fake camera detections or appearance-based escalation.
7. Persistence: temporary SQLite reopen tests; stable history order, acknowledgement,
   feedback, explicit active-event snapshots/short JPEG clips, replay/deletion,
   recording caps/timer, storage failure and camera Stop independence.

Review fixes and historical baseline are in [the audit report](SLICE_5_AUDIT.md).
Current automated evidence: 76 backend regression tests, 24 frontend session tests,
25 static markup checks, production build, live-bundle invariants and docs checks.
Test-only injected data is not shipped or presented as genuine inference.
Browser rendering, keyboard/focus/fullscreen and genuine playback require owner
acceptance: admin browser policy blocks Codex loopback access.

## Cleanup status and safety gate

Production imports no longer reference `fixtures.js`; the scenario selector,
response-source selector, canned answers and standalone preview path are removed
from app code. Old files remain unreferenced on disk because the DoorSense
PreToolUse gate rejected deletion. No rename, truncation or bypass was used.
The owner can remove these exact obsolete presentation files manually.
Do not delete model assets, actual spike reports, private media, event data or
regression tests. `demo/README.md` documents the genuine recording; it is not canned
runtime data.

In the Terminal running the console: click Stop first, then Ctrl+C. Leave the
existing Ollama Terminal running. Paste this complete block in the console Terminal:

```bash
cd "/Users/anymind/Documents/ChatGPT/Albert Space 2/Hackathon/DoorSense"
rm -f -- frontend/src/fixtures.js frontend/src/fixtures.test.js scripts/console_preview.py .runtime/console-preview.html frontend/.runtime/check-console.mjs
(cd frontend && /opt/homebrew/opt/node@22/bin/node node_modules/vite/bin/vite.js build) && .venv/bin/python scripts/console.py
```

Expected: successful build, localhost URL, camera OFF, rules DISARMED, no recording.
Reload the browser. Header: Start, Stop, Fullscreen, Diagnostics, Inputs; no
Demo/fixture selector. Nothing automatically opens the camera. No Codex restart,
dependency installation or model pull is needed.

Inputs includes functioning, explicitly simulated bell/impact/contact controls.
These create actual rule records, not canned outputs. Physical sensors do not
exist. For a camera-only demonstration, use Arm event rules and leave sensor
simulation buttons untouched.

## First owner frontend checkpoint

Use the live console before recording or disconnecting:

1. Click Start. Enter view: fresh person box/count appears. Ask What was observed.
   Expect Qwen-selected evidence; fallback is a separate result to report.
2. Leave view: old box disappears, detector count becomes zero. Ask again.
   No-person wording must not imply safety or identify anyone.
3. Inputs → Arm event rules; remain present for at least 30 seconds with fresh
   frames. Expect occupancy review with laptop_webcam facts. Acknowledge; event
   evidence/history remain. Check severity and camera availability separately.
4. Events → current event. Save a snapshot and short clip explicitly. View actual
   footage, delete media, save feedback. No pre-event buffer/audio/full-rate video
   or retraining claim. Restart and verify metadata persistence.
5. Diagnostics → Download runtime evidence. JSON contains measured accepted vision
   samples, frame counts, app-process RSS scope and the last 20 actual response
   records. No images/private token. Responses survive camera Stop, but not a
   service restart. The report cannot attest offline use.

Report which step passed, actual response source and any error. Detailed sensor
checks: [Slices 6 and 7](SLICES_6_7.md). Advance one checkpoint at a time.

## Offline proof after live frontend acceptance

In the existing Ollama Terminal, Ctrl+C. Stop the console and Ctrl+C in its
Terminal. Disable Wi-Fi and disconnect Ethernet/tethering. Start Ollama in its Terminal:

```bash
cd "/Users/anymind/Documents/ChatGPT/Albert Space 2/Hackathon/DoorSense"
.venv/bin/python scripts/start_ollama.py --serve
```

Expected: foreground daemon, loopback 127.0.0.1:11434, cloud disabled, local models.
If port is occupied, inspect the owner-running daemon; do not launch a duplicate.

In the console Terminal while still disconnected:

```bash
cd "/Users/anymind/Documents/ChatGPT/Albert Space 2/Hackathon/DoorSense"
.venv/bin/python scripts/check_runtime.py --assets --ollama && .venv/bin/python scripts/console.py
```

Expected: hashes/model metadata pass and camera-off console starts. Reload, Start,
produce new webcam observations and a fresh Qwen-selected response. Save runtime
evidence and show disconnected status. Browser developer tools must show local
app requests only; inspect connections alongside the owner daemon. Cloud-disable
configuration is not a traffic measurement. Follow [full acceptance](DEMO_AND_ACCEPTANCE.md)
for limits/performance/disclosures.
