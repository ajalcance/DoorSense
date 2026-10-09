# Child safety mode: combined simulation acceptance

Updated 2026-10-10, Asia/Manila. Source/in-process/static checks are separate
from genuine camera/Qwen, rendered-browser and offline acceptance.

## Owner restart

Click Stop, then Ctrl+C in the console Terminal. Keep Ollama running.

```sh
cd "/Users/anymind/Documents/ChatGPT/Albert Space 2/Hackathon/DoorSense"
DOORSENSE_FACE=1 .venv/bin/python scripts/console.py
```

Refresh the existing browser tab. Expected: capture off, Child safety mode off,
contact unknown; saved history/media/feedback remain. Frontend is already built.

## Ordered owner checks

1. Overview: controls/camera/analysis remain visible. Parent controls offer
   Enable Child safety mode. Start the camera while mode is off: genuine camera
   analysis remains available; new child activity alerts are disabled.
2. Simulate door closed. Enable Child safety mode: waiting state, no alert.
   Stay visible to the real camera and verify fresh person detection.
3. Click Simulate impact once: Accepted/time/colour, 1/3, countdown. No urgent.
   Refresh promptly: authoritative progress/contact/reply remain. Wait beyond
   five seconds: progress expires.
4. While detected, keep simulated contact closed and click Simulate impact
   three times at least 300ms apart within five seconds. Do not open the door.
   Expect urgent review BEFORE opening, mixed Webcam + simulated sensors source,
   actual person/impact/closed-contact facts and parent guidance.
5. Ask the supported urgent evidence question in Qwen. Confirm Qwen-selected
   evidence references supplied webcam/sensor facts; distinguish template fallback
   and application unavailable. Qwen does not inspect images or set severity.
6. Turn off Child safety mode: pending progress/replies clear, contact remains;
   existing alerts expire normally. Mode off prevents new child activity alerts.
   Turning off is a parent-facing manual switch, not authenticated parental access.
7. Reset session. Start again, set contact closed, enable the mode, then leave
   the camera frame. Three impacts without fresh person evidence must NOT produce
   combined urgent. Return within the remaining impact window: fresh real
   detection can complete the combination. Expired impacts cannot be reused.
8. With an alert active, Simulate door open: guidance changes to Step back from
   the doorway and get a parent. Opening does not create this urgent rule and
   cannot erase an existing alert. Open/close clears pending impact sequences.
9. View active event: Events/Evidence with matching facts/times. Overview restores
   three columns. Reset: capture off, mode off, contact unknown, temporary labels
   and active alerts cleared; saved history, feedback and media remain. Explicit
   recordings finalize through Stop behavior.
10. Mode on: three bells within ten seconds, at least 300ms apart, produce review;
    thirty seconds of continuous fresh person detections also produce review.
    Verify face/snapshot/Qwen behavior, Diagnostics/keyboard focus and stale-answer
    clearing. No normal simulation action should open an analysis-obstructing overlay.

## Current two-scenario face demonstration

Follow [the face demo](FAMILY_REFERENCE.md): Start with face analysis enabled,
enroll one face, verify a later live match and green child guidance, delete it,
and verify Unknown plus parent-check guidance. No sensor activities or arming
are needed. Also test a different person, face loss, Stop/reset/restart and stale
observations. Record actual outcomes; synthetic tests do not prove human accuracy.

## Historical expected visitor demonstration (superseded)

On a fresh single-person frame, follow Simulate a doorway visit and manually
confirm Family member or Unknown. Show original frame/time and owner_label source.
One ordinary knock (one simulated impact with closed contact) does not trigger
an activity rule, so the assessment can remain green/no configured alert.
The label does not recognize future frames or grant permission to open. It expires
within sixty seconds and never suppresses an active alert. No family recognition
database is implemented. The impact simulation does not measure force: three
ordinary knocks can also satisfy the unvalidated demo threshold.

Report the first failed step, expected/actual behavior and actual timestamps.
Full offline restart, saved-media workflow, pose/object quality and integrated
acceptance remain pending; do not label all Slices 1–10 accepted.
