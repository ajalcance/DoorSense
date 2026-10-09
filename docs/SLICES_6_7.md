# Slices 6 and 7: event rules and local evidence

Implemented 2026-10-09 at the owner's request, after the console audit fixes.
Source, fixture/regression and static markup checks passed. Genuine rendered
integration and offline acceptance remain pending. [Audit evidence](SLICE_5_AUDIT.md).

## Slice 6 contract

Explicit Start/Stop still control the webcam. Start does not arm rules. Overview →
Enable Child safety mode is a separate explicit action; Stop disarms.
Rules can be armed while the camera is unavailable to demonstrate simulated
sensor alerts. This never creates fake person observations.

| Rule | Default demo condition while armed | Active duration |
| --- | --- | --- |
| repeated_bell | 3 accepted simulated bell presses within 10 seconds | 60 seconds, review |
| sustained_occupancy | Fresh person detections continuously present for 30 seconds, with no gap of 0.8 seconds or more | 60 seconds, review |
| person_closed_door_impacts | Fresh camera person detection + 3 simulated impacts on a known closed door within 5 seconds | 120 seconds, urgent |

Duplicate same-kind inputs within 250 ms are debounced. An unchanged contact
state cannot refresh corroboration. Disarmed inputs do not carry into the next
arming session. The thresholds are configurable constructor parameters in
`backend/doorsense/events.py`; the UI exposes the implemented defaults, not an
unimplemented settings editor. These are unvalidated prototype rules.

One active event per rule avoids duplicate alerts. Urgent outranks review.
Acknowledgement and disarming do not erase raised alerts: their explicit expiry
remains in force. Camera/model loss does not erase sensor severity. Restart starts
camera-off and disarmed, with no revived active alerts; saved history remains.
An expiry is a display lifetime, not a claim that an incident was resolved.
Storage failure is explicit and preserves active alerts in session memory; such
alerts are labelled not persisted, with persistent acknowledgement/media/feedback
unavailable until storage works. A failed media save never prevents camera Stop.

Inputs have IDs, server timestamps, values, armed state and `simulated_sensor`
provenance. Event facts retain their own timestamps/sources and authoritative
rule reason. Appearance, identity, inferred intent and detector confidence never
raise severity. No-alert status is not a guarantee of safety.

Qwen is called only for resident requests using four existing presets. It receives
text facts, never media, and cannot change severity. Sensor events can be explained
without a camera. Selected recent history supplies its exact event reference;
records older than 60 seconds return application unavailable with their stored
facts still visible. Superseded/expired in-flight live contexts are discarded.
Qwen selection, template fallback, application unavailable and discarded remain
distinct. No free-text question box or automatic generation per frame.

## Slice 7 contract

The owner-started service creates `data/events.sqlite3`. SQLite persists event
metadata, triggering fact summaries, acknowledgement and explicit feedback.
History is paginated in groups of 25; the newest 10,000 raw simulated inputs are
retained, while event summaries remain. Feedback defaults to unknown; only Useful
alert, Unnecessary alert and Incorrect detection are accepted. Nothing retrains.

Overview stays compact. Events provides record details, media and feedback, with
an independent current-alert strip so historical inspection cannot hide urgency.
The shipped app is service-backed only. Synthetic presentation scenarios and
canned answers are removed from production imports; [cleanup status](MVP_READINESS.md).

No automatic footage storage. For the current active event, Events offers:

- Save current snapshot: save one fresh assessed JPEG captured after the event.
- Record up to 10s: explicitly collect current/future assessed JPEG frames, then
  save a local clip. Ends after 10 seconds, 50 frames, camera loss, Stop or shutdown.
  A Stop & save clip control is available during recording. No pre-event buffer.
- View existing snapshot/clip: actual stored frames in a labelled recorded-webcam
  viewer, with Play/Pause for clips. Replay does not run inference or create events.
- Delete media: remove that saved media from SQLite; preserve event metadata.

Clips are sampled JPEG sequences (up to 20 MiB decoded image data), not MP4 or
full-rate video; no audio. Recording buffers stay in memory until saved. No hidden
replay control appears for missing media. Camera Stop remains available in Events.
Local media is stored inside SQLite, eliminating arbitrary file-path access.
Deletion is logical local deletion with SQLite secure_delete; it is not a claim
of forensic erasure of OS backups. Existing private assets are never deleted.

## Owner restart

Use the Terminal currently running the console: click Stop in the console first,
then Ctrl+C in that Terminal. Leave the existing Ollama Terminal running. No Codex
restart, installation or model download is needed. In the console Terminal:

```bash
cd "/Users/anymind/Documents/ChatGPT/Albert Space 2/Hackathon/DoorSense"
(cd frontend && /opt/homebrew/opt/node@22/bin/node node_modules/vite/bin/vite.js build) && .venv/bin/python scripts/console.py
```

Expected: successful build and `http://127.0.0.1:8765`, camera OFF, event rules
DISARMED, no recording. Reload the owner's browser tab. The local database is
created at service startup; no pre-existing events are invented.

## Ordered owner checkpoints

Advance one checkpoint at a time. Report the visible state/source and any error;
do not mark later rows passed merely because the source tests passed.

1. **Rendered rules, no camera needed:** Overview → Enable Child safety mode.
   Click Simulate bell three times about one second apart. Keep the analysis visible. Expect
   review, repeated-bell reason and simulated_sensor facts. Events contains a real
   locally saved rule record, not a UI fixture. Acknowledge; severity remains.
2. **Urgency and availability:** While armed, click Simulate impact three times
   about half a second apart within five seconds, with simulated contact closed
   and a fresh genuinely detected person in view. Expect urgent before opening. Click camera Stop if running; urgent remains until its displayed
   120-second expiry. Rules become disarmed. Events retains the historical record.
3. **Genuine camera and language integration:** Start webcam explicitly and arm
   rules. Confirm fresh person boxes and entry/exit. Stay visible for 30 seconds
   with fresh assessed frames for occupancy review. Create a new bell/impact event
   when needed; ask a supported question within 60 seconds. Accepted response must
   be labelled Qwen-selected evidence to prove Qwen; template fallback is a separate
   failure-handling result. Diagnostics records actual returned source/timing.
4. **Actual local media:** With fresh webcam and a current active event, open its
   Events detail. Save snapshot; record a short clip; Stop & save clip. View both:
   image changes/timestamps must match genuine captured footage, with recorded
   provenance and no new detections. Delete media; View control disappears.
5. **Persistence and feedback:** Select feedback. Stop camera, Ctrl+C, run the
   restart command, reload. Expect camera off/disarmed; event/ack/feedback and any
   undeleted saved media remain. History is historical, not an active alert.
6. **Offline acceptance, still separate:** Follow [offline demo acceptance](DEMO_AND_ACCEPTANCE.md),
   including disconnected restart of app and Ollama, fresh genuine inference,
   network observations and combined M1 resource measurements. Do not count static
   markup, simulated sensors or template fallback as genuine inference evidence.

Slices 8–10 (additional vision, offline acceptance, reproduction/submission) are
not implemented by this change. No publication, Git mutation or submission.

Current live-only scope, camera situations, evidence export and gate-blocked
cleanup are in [MVP readiness](MVP_READINESS.md).
