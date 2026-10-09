# Console implementation audit

Updated 2026-10-09. Scope: Slice 5 foundation followed by the owner-authorized
Slices 6 and 7. Audit means source review and automated workflow simulation;
it does not establish absence of every defect or substitute for owner acceptance.

## Environment and preserved work

Active workspace: `/Users/anymind/Documents/ChatGPT/Albert Space 2/Hackathon/DoorSense`.
Existing dirty checkout and local assets preserved. No Git mutations, installations,
model downloads, service startup, camera access or protection changes performed.
Writes confined to the repository and OS temporary directories. `.git`, `.codex`,
`.agents`, `.aws` remain read-only; command networking remains blocked, approval
policy never. Existing Node 22 and repository Python environment used.

## Defects corrected

| Finding | Correction / regression evidence |
| --- | --- |
| Asking/changing questions erased acknowledgement; revisiting records lost it | Per-fixture session marks; persistent event acknowledgement independent of question/source/media/feedback |
| Normal polling erased action failures | Separate persistent action errors and connection errors |
| POSTs could leave busy controls indefinitely | Bounded control/explanation deadlines; honest timeout and server-work notice |
| Network transit was omitted from frame age | Age includes elapsed time from request start; malformed/stale frames rejected |
| Earlier polls could restore a stopped camera or regress an alert | Request-start ordering plus service token, camera revision and event revision checks |
| Prior detector session failure could poison a restarted session | Apply failure only to its own camera revision |
| Detector cleanup failure could terminate worker or permit unsafe reuse | Visible sticky restart requirement; worker survives |
| Busy shutdown could skip camera/adapter release | Cleanup runs directly in lifecycle finally blocks |
| Stale imagery could imply available assessment | Separate fresh packet validation and explicit waiting/unavailable state |
| Large bodies were allocated before size validation | Streamed 1 KiB JSON budget |
| Camera failure invalidated sensor-only explanations | Event context independent of webcam freshness |
| History selection could hide a current urgent event | Persistent active-alert strip in Events; history clearly labelled historical severity |
| Feedback could reorder old history through SQLite replacement | Stable UPSERT preserves original history order |
| Unrelated old records could receive newly captured footage | Capture only for the current active event; frame must be captured after event creation |
| Storage failure could suppress alerts or block Stop | Session alert cache and explicit storage errors; clip-save failure does not prevent camera release |
| Clip limit depended on detector returning | Independent 10-second event-loop timer, plus 50-frame/20 MiB bounds |

## Evidence boundaries

- Backend: 76 automated tests using mocks/in-process transports, synthetic pixels,
  temporary SQLite and injected clocks. No genuine inference, camera or network.
- Frontend: 24 service-backed session tests. Earlier presentation-fixture tests
  were retired when the owner requested a live-only production app.
- Markup: 25 server-rendered checks of presentation states/controls. No browser
  layout, keyboard, fullscreen, focus, playback timing or external-screen proof.
- Production build: passed using existing Node 22/Vite dependencies.
- Documentation links and whitespace: checked before handoff.
- Owner screenshots provide paused/fixture rendering evidence only.
- Genuine console camera/Qwen integration, actual saved webcam replay, failure
  injection, combined M1 performance and disconnected restart remain pending.

Browser automation of `http://127.0.0.1:8765/` was rejected by the admin-enforced
browser policy. Local file preview was also rejected earlier. No alternate browser,
raw protocol or networking workaround was used. Rendered audit remains Blocked
in Codex; follow the owner checkpoints in [Slices 6 and 7](SLICES_6_7.md).

## Reproduce automated checks

Run in owner Terminal (does not start services or capture):

```bash
cd "/Users/anymind/Documents/ChatGPT/Albert Space 2/Hackathon/DoorSense"
.venv/bin/python -m unittest discover -s scripts -p 'test_*.py'
/opt/homebrew/opt/node@22/bin/node --test frontend/src/session.test.js
cd frontend
/opt/homebrew/opt/node@22/bin/node node_modules/vite/bin/vite.js build
/opt/homebrew/opt/node@22/bin/node node_modules/vite/bin/vite.js build --ssr src/ConsoleView.jsx --outDir .runtime/console-render
/opt/homebrew/opt/node@22/bin/node scripts/check_console_markup.mjs
cd ..
.venv/bin/python scripts/check_docs.py
```

Expected: 76 backend tests, 24 frontend tests, successful production/SSR builds,
25 markup checks and resolving documentation links. Mock download messages in
preparation tests describe injected fixture responses; they do not fetch assets.

## Live-only MVP follow-up

Owner narrowed completion to Slices 1–7 and asked to remove presentation stubs.
The production imports/mode/canned responses/preview path are removed. The safety
gate blocked physical file deletion; obsolete files remain unreferenced until the
owner runs the exact cleanup in [MVP readiness](MVP_READINESS.md). No bypass used.
Additional fixes guard late media fetches after navigation/service restart, disable
unavailable actions, and preserve actual response evidence across camera Stop.
Asset/package checks were reverified. Source review and existing genuine reports
support readiness for acceptance; they do not pass offline or rendered acceptance.
