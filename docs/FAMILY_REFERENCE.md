# Two-scenario local face learning demo

## Final presentation and parent control

The parent-controlled Child safety mode is restored. Off: camera learning and
recognition continue without child alerts. On: the live camera banner and the
single AI Analysis panel show familiar-visitor guidance or an Unknown visitor
parent-check warning. Stop/reset turn this mode off and preserve enrollment.
This toggle controls guidance only, never sensor/occupancy rules.

AI Analysis has no tabs or manual question controls. It combines the verdict,
child recommendation, acceptance/rejection reason, live distance/threshold and
supervised-learning summary. Measurements remain in one expandable section.
The local text model is requested automatically when fresh evidence changes;
requests are throttled and unavailable results cannot replace the camera verdict.
Results near the cutoff receive a parent-confirmation note. The person-detector
percentage is explicitly separate from the face distance.

The supplied live screenshots showed both rejection (75.12/95.12 > 65) and a
successful Family member result (53.70 ≤ 65) under the existing recognizer.
The saved face and recognizer are preserved for this presentation pass. Decision
rounding now agrees with the displayed two-decimal score. No threshold was raised,
no new normalization/model was deployed, and no calibrated accuracy is claimed.
An attempted offline screenshot face-landmark run could not initialize MediaPipe's
graphics service inside this session; it supplied no recognition evidence.
The new UI, toggle and automatic request flow still need owner live acceptance.

## Current implementation (supersedes the photo-only notes below)

The camera detects one person and face landmarks locally. Installed OpenCV LBPH
learns a parent-labeled crop and compares later live crops. This is supervised
appearance enrollment/matching, not RL or friendly-intent analysis. The child
recommendations are application guidance based on the local match.

Use the [current runbook](../demo/DEMO_RUNBOOK.md) to start, refresh and Start.
Enable Child safety mode to show child guidance; recognition also works while
the mode is off. No sensor activities are needed. The controls now contain only:

1. **Learn a family member:** save your face, then wait for subsequent camera
   frames. A close appearance match gives a green Family member / familiar visitor
   assessment: ask your parent before opening. View captured face verifies the
   saved original JPEG. Move away and return to test another live observation.
2. **Try an unknown visitor:** delete the reference and stay in view. The same
   face returns to Unknown: keep the door closed and get your parent to check.
   Unknown alone does not mean dangerous.

AI Analysis shows the actual LBPH distance and rejection threshold (65; lower is closer).
Landmarks bound the face crop; at least 64 by 64 pixels are required. A 128 by 128
grayscale sample trains local texture histograms. Missing, multiple, small,
unavailable or stale faces cannot establish a match. One example works best with
similar frontal pose and lighting; false and missed matches remain possible.
The threshold is provisional, not calibrated identity confidence or safety.

Explicit enrollment stores the original JPEG including background plus the face
sample in the existing local reference table. Stop/reset/restart preserve it;
Delete removes it and invalidates live matching. Older photo-only references need
explicit deletion and reenrollment for photo-only records. Old history remains;
sensor and manual category APIs return 410 in production. The armed endpoint now
controls only the parent guidance toggle. Occupancy cannot emit an alert;
only fresh face analysis drives current child guidance. No new downloads,
dependencies, cloud calls or automatic enrollment were introduced.

Tests exercise genuine LBPH training/prediction on synthetic textures, plus API,
storage, freshness and recognition-dependent guidance. These are not human
recognition accuracy measurements. Owner live capture, return/rejection,
delete/restart and offline browser/camera/Qwen trials remain pending.

The Supervised face learning summary shows enrolled-example count, current distance
and configured rejection threshold. The unified panel's measurement details expose
the captured example, actual training/comparison timings and the current decision. Missing/stale results
show no score. Person-detector percentages are separate from LBPH distance;
no recognition probability is invented.

## Historical photo-only delivery

Implemented 2026-10-10, Asia/Manila, after the owner authorized using their own
face for the simulation. The assistant has not captured a live face in this
session: the owner must explicitly click Save in the owner-started console.

## Historical photo-only save/delete instructions (do not use for the current demo)

Stop capture, Ctrl+C the console Terminal, keep Ollama running, then restart:

```sh
cd "/Users/anymind/Documents/ChatGPT/Albert Space 2/Hackathon/DoorSense"
DOORSENSE_FACE=1 .venv/bin/python scripts/console.py
```

Refresh, Start, show only your own face and wait for available face analysis.
Under Simulate a doorway visit, click **Save my face as Family member**.
Expected: saved time/original frame, View saved reference and Delete saved
reference. View verifies the actual JPEG that was saved. The full assessed frame,
including its background, is saved; this is not a cropped biometric template.
Save is rejected for stale/no frame, zero/multiple people or unavailable face
analysis. A saved reference cannot be silently overwritten; delete it explicitly.

One reference is stored in the existing ignored `data/events.sqlite3`, in a
separate `family_reference` table. Schema creation happens when the owner starts
the updated service; no live owner database was opened/migrated by the assistant.
No photo is written merely by camera viewing, person detection or repeated visits.
Status returns metadata only. Viewing the photo requires the protected local API.
Runtime evidence export does not include the photo. Save, view and delete reuse
the existing token, same-origin/host and bounded-request protections.

Reset, Stop and restart preserve the saved reference. Delete removes only this
reference and clears an active manual Family member snapshot confirmation;
existing event history, saved media and feedback remain. This does not
claim deletion of filesystem backups or forensic erasure.

## Historical intended next demo (recognition is now implemented above)

The owner intends to show the same person/activity with a learned household
profile, then delete that profile and repeat as Unknown. The larger direction is
visitor memory, real face matching, temporal activity interpretation and parent
feedback. The user asked to step back and settle that design before further
learning implementation. Photo storage alone is not face recognition, supervised
training, RL or automatic household learning. Current Face Landmarker measures
availability/movement, not personal identity. No embedding/matching model,
recognition accuracy, trained policy, automatic profile enrollment or calibrated
suspicious-intent probability is delivered.

The reference supports preparation for that design; it does not alter alert
severity, mark later frames as recognized or authorize opening. The current
manual Family member/Unknown confirmation remains bound to an assessed snapshot.
Deleting this reference is not yet a recognition-model deletion experiment.

Automated checks use temporary SQLite, synthetic JPEGs and injected model states.
Owner photo saving/preview/restart/deletion and rendered acceptance remain pending.
