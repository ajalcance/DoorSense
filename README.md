# DoorSense

DoorSense is a local AI doorway assistant that helps children pause and ask a
parent before opening the door. A live camera detects a person and compares a
clear face with one parent-enrolled family example. Parents can turn **Child
safety mode** on when guidance is needed; recognition continues while it is off.

## Current demo

- **Family member:** a fresh appearance match displays a green camera banner
  and asks the child to check with a parent before opening.
- **Unknown:** an unenrolled or rejected face displays a parent-check warning
  when Child safety mode is on: keep the door closed and get a parent.
- Unclear or stale faces show limited/waiting analysis rather than a valid match.
- One **AI Analysis** view explains the result, measured match distance,
  supervised-learning example and automatically selected local text-model facts.

Unknown does not mean dangerous. Familiarity does not prove safety or authorize
opening. Learning is explicit supervised enrollment, not reinforcement learning
or automatic learning from repeated visits. Sensors and activity simulations are
excluded from the current demo.

## How it works

Laptop webcam → OpenCV capture → MediaPipe EfficientDet person detection →
Face Landmarker localization → OpenCV LBPH appearance matching → React camera
banner and AI Analysis. Python/FastAPI serves the local console; SQLite stores
one enrolled reference. Qwen3 0.6B through local Ollama selects supplied text
facts automatically; it receives no camera images and does not decide identity.

All core processing is local. Packages and models need initial provisioning;
complete disconnected restart and traffic inspection remain pending. Owner
screenshots demonstrate genuine camera inference and a successful family match.
Source/build checks pass; final banner, parent-toggle and automatic-analysis
acceptance still require a live owner trial. See the
[technical overview](docs/TECHNICAL_OVERVIEW.md) for versions and evidence limits.

## Run locally

Use Python 3.12 and Node 22 (>=22.12, <23). Complete
[local preparation](docs/PREPARATION.md) before starting; no model is downloaded
at runtime. With the prepared environment and built frontend:

```sh
.venv/bin/python scripts/console.py
```

Open `http://127.0.0.1:8765`. Camera capture remains off until **Start**.
For automatic local text findings, start the prepared Ollama service in a
separate owner Terminal as described in preparation. The
[demo runbook](demo/DEMO_RUNBOOK.md) covers both scenarios and parent controls.

## Check the repository

```sh
.venv/bin/python scripts/check_docs.py
.venv/bin/python scripts/audit.py
```

The audit runs backend/frontend regression, builds and static checks without
starting services or opening the camera. Its report is saved under ignored
`.runtime/`. Fixtures and static rendering do not establish live accuracy or
end-to-end offline operation.

## Repository guide

- [Technical overview](docs/TECHNICAL_OVERVIEW.md): current features, stack and roadmap.
- [Documentation index](docs/README.md): current references and historical reports.
- [Submission draft](demo/SUBMISSION_DRAFT.md): description and technical disclosures.
- [Model/tool disclosures](docs/DISCLOSURES.md): provenance and licensing status.
- [Acceptance checklist](docs/DEMO_AND_ACCEPTANCE.md): remaining live checks.
- `backend/doorsense/`: camera, local vision, recognition, storage and service.
- `frontend/`: React console and session logic.
- `scripts/`: preparation, startup and verification tools.
- `assets/`: tracked model manifests; downloaded weights are ignored.
- `security/`: repository-specific development sandbox tooling.
- `hardware/`: future integration notes; no physical device is implemented.

Saved faces, private history, recordings, models, credentials and runtime reports
must remain outside Git. The project license has not been selected; model-weight
license confirmation remains pending. No publication or submission is implied.
