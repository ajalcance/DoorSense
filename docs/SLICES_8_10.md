# Slices 8–10: vision, acceptance and demonstration

## Latest child-mode and visit-scenario contract (2026-10-10)

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


Updated 2026-10-10, Asia/Manila. The owner expanded scope through Slice 10.
Source implementation and automated audit are separate from genuine model,
rendered, disconnected-startup and submission acceptance. Missing evidence is
Blocked or Not run, never Passed.

## Delivered Slice 8 contracts

The existing person detector remains independent of optional scene features.
Explicit owner startup configuration enables one feature at a time:

| Feature | Actual implementation | Availability/limitations |
| --- | --- | --- |
| Facial movement | MediaPipe Face Landmarker v1; open mouth, lowered eyelids, raised mouth corners from selected blendshape coefficients | No emotion, identity or family recognition. Requires one detected person, one face, complete in-frame landmarks, score threshold 0.65 and two consecutive sampled frames |
| Body posture | MediaPipe Pose Landmarker Lite v1; one/both wrists above shoulder level | Both shoulders/wrists in frame, visibility/presence ≥0.7, vertical margin 0.08; two sampled frames. No action/intent or standing/crouching classification |
| Objects | Existing EfficientDet weights; backpack, handbag, suitcase allowlist | Model-reported objects only; no ownership/carrying inference or hood/glasses detection. Separate held-out quality checks required |

Face/pose/object features are off by default until owner preparation and staged
resource/quality checks. No model acquisition at runtime. Missing files, receipt
mismatch, task construction/inference failure and partial visibility are explicit.
Person detection and sensor alert severity remain independent of optional models.
Description stabilization resets on gaps ≥0.8s, disappearance, multiple people
and camera restart. It is not persistent identity tracking.

All observations attach to the exact assessed JPEG/frame/time and expire with
that frame. Camera-to-Qwen contexts contain up to eight original facts; the UI
uses those supplied facts. Qwen still selects evidence IDs and receives no image.
Changed scene descriptions/availability supersede pending camera answers even
when person count stays constant. Sensor-event explanations retain their own
recorded facts; facial appearance cannot override a sensor alert.

Model tasks run sequentially in the bounded vision worker, never the API thread.
Optional inference over 600ms, or over 200ms on three consecutive attempts,
disables that feature and attempts cleanup; restart with fewer enabled features.
These are resource safeguards, not measured M1 performance claims. Session
diagnostics export actual combined and per-feature latency/counts/hashes. RSS is
the app process high-water mark; it excludes Ollama and total unified memory.

Official API/model references:
[Face Landmarker](https://developers.google.com/edge/mediapipe/solutions/vision/face_landmarker/python),
[Pose Landmarker](https://developers.google.com/edge/mediapipe/solutions/vision/pose_landmarker/python).
[Versioned acquisition sources](../assets/scene-models.json) use the publisher's
v1 URLs. Owner acquisition records byte counts and locally measured SHA-256 in
ignored `.runtime/scene-assets.json`; no independent publisher checksum or model
weight licence has been established. Package/sample licences do not settle this.

## Owner model preparation and restart

Use ordinary Mac Terminal. No dependency installation is needed. First stop the
console with Ctrl+C in its existing Terminal. Keep the existing verified Ollama
Terminal running. Run this in another owner Terminal while internet is available:

```sh
cd "/Users/anymind/Documents/ChatGPT/Albert Space 2/Hackathon/DoorSense"
.venv/bin/python scripts/prepare_scene_models.py --feature face --online && \
DOORSENSE_FACE=1 .venv/bin/python scripts/console.py
```

Expected: an actual acquisition receipt with size/SHA-256, then camera OFF/rules
DISARMED. Reload `http://127.0.0.1:8765`, press Start. Face movement becomes
available only on genuine model output; otherwise read its limited/unavailable
message. Hold an open mouth or closed eyelids for about one second, then relax;
check disappearance, two-frame stabilization, head turning and frame edges.
Try separate held-out attempts under two lighting/framing conditions and record
misses/unwanted descriptions. Do not call this emotion recognition.

After face-only resource checks, stop the console with Ctrl+C and acquire/test
pose independently:

```sh
cd "/Users/anymind/Documents/ChatGPT/Albert Space 2/Hackathon/DoorSense"
.venv/bin/python scripts/prepare_scene_models.py --feature pose --online && \
DOORSENSE_POSE=1 .venv/bin/python scripts/console.py
```

Expected: pose receipt, paused console. Include shoulders and both wrists in the
webcam frame, raise one/both wrists, lower them and move a wrist out of frame.
Limited visibility must replace the description immediately. A close face-only
webcam crop cannot establish body posture. Test objects independently with
`DOORSENSE_OBJECTS=1 .venv/bin/python scripts/console.py`; no new weights required.
Use an actual backpack/handbag/suitcase and negative examples, recording misses.

Only after individual checks, stop the console and test the combined pipeline:

```sh
cd "/Users/anymind/Documents/ChatGPT/Albert Space 2/Hackathon/DoorSense"
DOORSENSE_FACE=1 DOORSENSE_POSE=1 DOORSENSE_OBJECTS=1 .venv/bin/python scripts/console.py
```

Expected: paused camera until Start; all enabled models remain local. Download
runtime evidence from Diagnostics after genuine trials/Qwen requests. If freshness
or responsiveness fails, disable a feature and restart; do not invent benchmarks.
Offline transfer is supported with `--feature face --import-file /absolute/model.task`
instead of `--online`; it records transferred bytes, not publisher authenticity.

## Slice 9: offline/failure acceptance

The acceptance recorder/reviewer is implemented. It prepares every live checkpoint
as Not run, validates owner outcomes, and cross-checks model/Qwen runtime metadata.
It cannot inspect disconnected networking from source tests or certify isolation.

```sh
cd "/Users/anymind/Documents/ChatGPT/Albert Space 2/Hackathon/DoorSense"
.venv/bin/python scripts/acceptance.py init
```

Expected: `.runtime/acceptance-observations.json`, all checks Not run. Existing
reports are preserved; init refuses overwrite. Fill actual outcomes and concrete
evidence after the checks below. Use a timezone-bearing tested_at timestamp.

1. Stop both console and owner Ollama with Ctrl+C. Disable Wi-Fi, unplug Ethernet
   and tethering. This is an owner action, not done by Codex.
2. In owner Terminal A, restart Ollama offline:

   ```sh
   cd "/Users/anymind/Documents/ChatGPT/Albert Space 2/Hackathon/DoorSense"
   .venv/bin/python scripts/start_ollama.py --serve
   ```

   Expected: pinned local model store, cloud disabled, loopback 127.0.0.1:11434.
   If the port is occupied, inspect the existing daemon; do not blindly kill it.
3. In owner Terminal B, verify local bytes and restart the combined console:

   ```sh
   cd "/Users/anymind/Documents/ChatGPT/Albert Space 2/Hackathon/DoorSense"
   .venv/bin/python scripts/check_runtime.py --assets --imports --ollama && \
   DOORSENSE_FACE=1 DOORSENSE_POSE=1 DOORSENSE_OBJECTS=1 .venv/bin/python scripts/console.py
   ```

   Expected: bytes/imports/served metadata pass; camera OFF. Reload, Start and
   use new webcam movements. A warm old browser tab is insufficient evidence.
4. Run face/pose/object positives, negatives, entry/exit, sustained occupancy;
   inspect responsiveness and runtime evidence. Press Ask; require the actual
   Qwen-selected source/digest/timing, not fallback.
5. Overview → left simulation controls → Arm → three bells spaced ≥300ms within 10s: Review. Three impacts
   spaced ≥300ms plus door-open within 5s: Urgent. Simulated provenance stays visible.
6. Stop camera: urgent remains until expiry, camera light turns off, rules disarm.
   Explain that event before its 60s explanation window closes. Restart capture.
7. On a current active event, save a snapshot and explicit clip. Replay/delete,
   acknowledge, save feedback, restart console and verify history/feedback/media.
   Historical severity remains distinct from an active alert after restart.
8. Stop owner Ollama while console keeps running. Ask on fresh evidence: labelled
   template fallback, camera/rules remain responsive. Restart Ollama afterward.
   Missing/corrupt models and malformed/timeout handling have automated coverage;
   live failure outcomes remain separately recorded.
9. Inspect browser Network (local assets/API only) and process connections using
   an owner tool such as Activity Monitor → Network / `lsof -nP -iTCP -iUDP`.
   Record time, processes and destinations. A single snapshot cannot prove no
   traffic throughout; observe startup and interactions separately. No external
   runtime-dependency claim follows from source inspection alone.
10. Download runtime JSON into ignored `.runtime` and review the owner record:

   ```sh
   cd "/Users/anymind/Documents/ChatGPT/Albert Space 2/Hackathon/DoorSense"
   .venv/bin/python scripts/acceptance.py review \
     --observations .runtime/acceptance-observations.json \
     --runtime .runtime/owner-runtime-evidence.json
   ```

Expected: real blockers until every required check and matching session evidence
exists. Exit 1 means incomplete acceptance, not a broken app. Reports are private;
they may contain event facts and must be reviewed before sharing.

## Slice 10: reproduction and demo preparation

[Demo runbook](../demo/DEMO_RUNBOOK.md) and [submission draft](../demo/SUBMISSION_DRAFT.md)
are prepared. The source inventory excludes private data/media, weights,
dependencies, protected metadata and obsolete presentation modules. It does not
publish, submit, choose a project licence or prove clean-machine reproduction.

```sh
cd "/Users/anymind/Documents/ChatGPT/Albert Space 2/Hackathon/DoorSense"
.venv/bin/python scripts/audit.py
.venv/bin/python scripts/reproduction_check.py
```

Expected: automated regression/build/static markup checks pass; an ignored
source-fingerprint report is written. Reproduction reports missing scene assets
until acquired. Clean-machine reproduction, model-weight licence review, actual
recording, public GitHub/social links, organiser eligibility and submission remain
owner actions. No publication or Git mutation has been performed.

The current simulation-console source audit passed 109 backend, 32 frontend and 43 static
markup checks. Existing runtime/package/model integrity recheck passed. These
checks do not run new face/pose weights or establish disconnected acceptance.

## Approved interactive dashboard and family demo

Owner approved and implementation adds detection corner brackets,
compact actual status and expandable actual scene findings. Green = armed monitoring
without a configured alert; amber = review; red = urgent rule; grey = paused/limited.
Unknown identity is not an urgent condition. Automatic family recognition is outside
Slices 1–10 and needs a separate enrollment/recognition/accuracy scope. Any manual
visitor label must be marked owner supplied, never camera recognized. No fabricated
percentages, PPE detections or relationship/emotion claims from the reference image.

Right-column Scene/Qwen/Evidence tabs expose actual measurements, supplied facts,
local-model response source/timing and existing evidence actions. Arrow keys/Home/End
move tab focus. Detector scores are model scores, not calibrated safety confidence.
Limits/session counters live in the simulation column. Green **Face analysis available ·
identity unverified** means complete landmark output. Grey **Face analysis limited ·
ask a parent before opening** means the feature cannot assess the current frame;
disabled is explicitly off. Neither determines event severity.

The left simulation column includes an owner-only-in-purpose snapshot annotation (Parent, Family member,
Expected visitor). It is not authenticated parental access, face enrollment or a
biometric database. The loopback owner must know the visitor; `owner_label` provenance,
original frame/time, 60s limit and clearing on Stop/loss/count change are explicit.
Qwen receives original snapshot facts; new events take precedence. The annotation
does not recognize later frames or reduce severity. Active review/urgent rules show
**Call a parent before opening the door** independently of Qwen and camera availability.
This is a screen warning, not an audible siren, phone call or remote notification.
The owner selected the lightweight demo; cap/sunglasses classification/VLM is deferred.
[Demo evidence sequence](../demo/DEMO_RUNBOOK.md) · [Audit](SLICES_8_10_AUDIT.md).

The header's **Reset session** stops capture (saving any explicitly started clip),
disarms rules, clears pending inputs, active demo alerts and owner annotations,
and returns the UI to Overview. Saved event history, feedback and media remain.
Unlike Reset session, **Cancel simulation · disarm** only disarms and clears the
pending rule inputs; existing alerts remain until expiry. Input button colors
show server-confirmed accepted/ignored replies and the authoritative simulated
contact state, never physical sensor readings. Progress, remaining windows and the
six recent replies now come from backend session state and survive browser refresh.
Cancellation clears pending inputs/replies but retains last accepted contact;
reset clears contact to unknown. Opening an already-open contact is ignored; close
then reopen to supply a fresh transition. Overview has persistent controls, smaller
camera and right analysis columns; navigation is in the header, with no Inputs
overlay. Owner confirmation and detailed rules/limits may collapse.
