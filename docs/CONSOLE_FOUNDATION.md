# Slice 5 console foundation

Historical Slice 5 checkpoint. Current implementation and owner acceptance are in
[Slices 6 and 7](SLICES_6_7.md), with the [audit](SLICE_5_AUDIT.md). The camera-only
limitations below describe that earlier slice, not current delivered capabilities.

Implemented after owner approval on 2026-10-09 (Asia/Manila). Scope: React/Vite
console, explicitly labelled UI fixtures, volatile camera/person observation
bridge and bounded Qwen preset requests. No sensor rules, event history,
recordings, saved media, feedback or additional vision models.

## Evidence

- Production Vite build passed using existing Node 22.23.1 and packages.
- Nine in-process service checks and two frontend fixture checks passed.
  Fake camera/injected LLM only; no port, device or model opened by these checks.
- Existing 15 Qwen boundary fixtures, nine camera lifecycle checks and two vision
  contract checks passed as regression checks. These do not rerun genuine inference.
- Rendered QA is **Blocked** in Codex: the browser URL policy rejected the local
  `file:` fixture preview. Command networking, including loopback, remains blocked.
  No alternate browser or network workaround was used.
- Genuine rendered camera/Qwen integration, physical release/restart and external
  display acceptance are **Pending owner run**. Offline acceptance remains Slice 9.

## Owner Terminal: build and launch

Keep the existing foreground Ollama Terminal running. In a **second Mac Terminal**:

```sh
cd "/Users/anymind/Documents/ChatGPT/Albert Space 2/Hackathon/DoorSense" &&
(cd frontend && /opt/homebrew/opt/node@22/bin/node node_modules/vite/bin/vite.js build) &&
.venv/bin/python scripts/console.py
```

Expected: Vite prints a successful build; DoorSense prints
`http://127.0.0.1:8765`, camera OFF, no recording; uvicorn binds only to loopback.
Open that URL in a normal browser. Capture begins only when you click Start.
No dependency installation or model download is performed. No Codex or Ollama
restart is needed. If this console service is already running, click Stop,
confirm the camera indicator turns off, press Ctrl+C in its Terminal, then run
the complete block again. Never terminate an unrelated process if the port is busy.

## Ordered owner acceptance

Latest owner-approved layout: a left Overview/Events navigation rail, global
Start/Stop/Fullscreen/Diagnostics/Demo controls in the header, and a balanced
camera/assessment workspace. Assessment sections share one panel; source labels
and assessment limits are retained. Events has a dedicated empty/history-fixture
view; no persistent event history was added. Diagnostics and Demo open anchored
panels beneath the header. Close, Escape or outside click dismisses them; Close
and Escape restore focus to the triggering control.

At browser content sizes of at least 1100 × 740 CSS pixels, the shell uses the
available viewport height. The camera is contained without cropping; long
assessment text, event lists or diagnostics can scroll inside their own region
so evidence is not truncated. Smaller windows use an accessible scrolling layout.
Production build, two existing frontend fixtures and 16 server-rendered markup
smoke checks passed. Markup checks do not establish browser layout or interaction
acceptance; revised visual fit is pending owner refresh. No real camera/model ran.
For this CSS/copy update, keep the console/Ollama services running, rebuild with
the Node 22 build command above and refresh the browser; no restart is needed.

Latest styling refinement following the paused Overview screenshot: desktop
navigation is 176–208 CSS pixels wide, body text 14 px, metadata 12 px, section
headings 16 px and status headings 20 px. Header controls keep 40 px height and
navigation targets 44 px. Panel proportions, spacing and subdued borders were
adjusted without changing behavior. Production build passed; revised browser
appearance still requires owner refresh/review.

Start with **checkpoint A**, fixture/rendered acceptance:

1. Open the URL. Confirm camera off, paused state and no saved media/history claim.
2. In the header, click Demo → Console mode → UI fixture. Close the panel or press
   Escape to inspect Overview.
3. Select each state: paused, monitoring, review, urgent, unavailable, urgent plus
   camera unavailable, permission denied and detector unavailable. No webcam
   image appears. The UI fixture banner and synthetic evidence labels remain visible.
4. Acknowledge review/urgent. Confirm severity/evidence remain visible. Click
   Events in the left navigation, select a fixture record and confirm its details
   replace the previous fixture. Return to Overview without starting capture.
5. In Demo, choose each fixture response source, then close the panel and choose
   Show fixture answer. Qwen selection,
   template fallback and application unavailable each retain the UI fixture label.
6. Tab through controls; inspect visible focus, readable text, dropdowns and
   scrolling. Test Fullscreen, Escape and the actual external display.

Report checkpoint A result, browser/display size, any clipped/unclear elements,
and which fixture/control failed. Fixture success does not prove real inference.
No need to supply or save real camera screenshots.

After A is reviewed, **checkpoint B** is genuine integration:

1. Choose Demo → Console mode → Live camera foundation, close Demo, then click
   Start in the header (Start monitoring). Allow the intended macOS
   camera permission if prompted. Observe genuine frames/person boxes on entering
   and leaving view. Camera observations alone never become review/urgent alerts.
2. Select What was observed? → Ask about current observation while the scene is
   stable. Inspect the source label and Diagnostics. Accepted Qwen selection is
   genuine inference; template fallback is not. The answer names the original
   observation capture time. Count changes, Stop or stale assessment discard it.
3. Ask the review and urgent presets. With no event rules, they return Application
   unavailable without a Qwen call. No free-text question input exists.
4. Click Stop in the header. Confirm imagery/observations clear and the camera
   indicator turns off. Start again and confirm fresh input. Stop remains available
   while viewing Events; navigation itself does not stop capture. Stop before
   leaving the service.

Report actual response source/fallback reason, physical indicator behavior,
entry/exit behavior and any failure. Do not claim offline operation from this run.
Model-only identity abstention remains failed regardless of console results.

## Source and runtime boundaries

`backend/doorsense/console.py` serves built local assets and volatile JSON frame
packets. Camera opening runs directly on the main async endpoint thread;
reads remain in the existing capture worker. Detection/encoding run sequentially
in a worker at up to 5 Hz without a backlog. Each packet combines its exact
analyzed image and matching overlays; server/client discard frames older than
0.8 seconds. A stalled status request times out and clears displayed imagery.
No images or per-frame history are written to disk.

One shared LocalLLM instance preserves the pinned version/digest, request limits,
no queue, no pulls, no proxies and source labels. Resident requests use a snapshot
of a genuine observation, with capture time on the response. Current session
revision, fresh assessment and unchanged person count guard against supersession;
this is not identity tracking. Snapshot answers expire under the adapter's
60-second contract. Review/urgent questions are application unavailable until
actual event integration exists. No alerts are generated from person presence.

The loopback service has host/origin checks, no CORS, per-process control token,
no-cache frames and no public listener. These are implementation measures,
not a completed security audit or offline enforcement proof. Closing a browser
tab does not itself stop capture; use Stop or Ctrl+C in the service Terminal.

For a server-free **owner-only fixture preview** after building:

```sh
cd "/Users/anymind/Documents/ChatGPT/Albert Space 2/Hackathon/DoorSense" &&
.venv/bin/python scripts/console_preview.py
```

Open the printed `.runtime/console-preview.html` manually in a normal browser.
The standalone file uses bundled assets, disables live mode and performs no
status/API fetches. This path does not establish service integration acceptance.
