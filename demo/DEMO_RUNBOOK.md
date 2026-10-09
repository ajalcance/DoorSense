# DoorSense live demo runbook

## Opening problem

A camera shows who is at the door, but a child may not know how to respond.
DoorSense adds local face analysis and a clear reminder to pause and involve a
parent. Parents choose when Child safety mode is needed.

## Prepare

Use the prepared local Python environment, built React frontend, EfficientDet,
Face Landmarker and Qwen assets. Follow [preparation](../docs/PREPARATION.md).
Start the console from the repository root:

```sh
.venv/bin/python scripts/console.py
```

Open `http://127.0.0.1:8765` and refresh. Start the prepared local Ollama service
in another Terminal for automatic text findings. Do not run a second instance
on an occupied port. Capture starts only when Start is clicked.

Use your own consented face. Enrollment stores the original frame, including
background, plus a face sample locally. Keep private images and runtime data out
of Git and the submission; review what a recorded demo will show.

## Live sequence

1. **Show the camera:** click Start and face the camera with one person in view.
   Show fresh frames, person detection and the actual detector score.
2. **Show parent control:** enable Child safety mode. With no enrolled match,
   the banner asks the child to keep the door closed and get a parent. Explain
   that Unknown means unrecognized, not dangerous.
3. **Learn a family member:** save your face when analysis is available. If an
   example already exists, preview it or explicitly delete it before enrollment.
   Wait for subsequent live frames; a successful match shows Family member in
   green and asks the child to check with a parent before opening.
4. **Explain the AI:** point to the single AI Analysis view: the comparison reason,
   lower-is-closer distance, provisional cutoff 65 and one labeled example. Local
   text findings appear automatically when available. No manual tab/question is needed.
5. **Try Unknown:** delete the reference and remain in view. The next fresh clear
   face is Unknown because the recognizer has no enrolled family example. Show
   the parent-check warning and changed learning count; no score should be invented.
6. **Finish:** turn Child safety mode off to show recognition without child alerts.
   Stop/reset turns the mode off; enrollment otherwise survives Stop/reset/restart.

Allow time for fresh results and bounded text inference. Pose/lighting changes can
reject even an enrolled face; show the actual distance and parent-check guidance,
never raise the threshold just to force a green result. Unclear/no/stale faces
should show waiting/limited analysis rather than an accepted identity.

## Brief technical explanation

Python/FastAPI and React/Vite run locally. EfficientDet detects a person, Face
Landmarker locates a face, and OpenCV LBPH learns the parent-labeled example and
compares live crops. SQLite keeps the reference on the device. Qwen3 0.6B through
Ollama selects supporting text facts; the application maps the observed match to
child guidance. This is supervised enrollment, not RL or autonomous learning.

Owner screenshots show a real family comparison at 53.70 against cutoff 65.
Automated checks pass; final unified UI/automatic text flow and complete offline
restart still need live acceptance. Follow the
[acceptance checklist](../docs/DEMO_AND_ACCEPTANCE.md) and record actual outcomes.

## Submission

Use the [approved description and disclosures](SUBMISSION_DRAFT.md). Add actual
repository, demo and required social-video URLs. Confirm model/tool disclosures,
remaining license status and build chronology. No physical lock, sensor, CCTV
feed, notification delivery or measured safety/recognition accuracy is claimed.
