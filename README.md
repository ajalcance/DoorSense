# DoorSense

Local AI doorway monitoring with a modern indoor console.

DoorSense is designed to help residents see what is happening outside their door,
understand alerts and review supporting evidence, with processing on a local hub.
The hackathon prototype targets an Apple M1 with 8 GB RAM: a laptop webcam stands
in for the planned ESP32 camera, and clearly labelled controls simulate door sensors.

**Status: repository scaffold and specifications. Application implementation has
not started. Offline inference, performance and security effectiveness are unverified.**

## Start here

| Reader | Recommended route |
| --- | --- |
| Judges | [Judge guide](docs/JUDGES_GUIDE.md) → [current evidence](docs/CURRENT_STATE.md) → [demo checklist](docs/DEMO_AND_ACCEPTANCE.md) |
| Developers | [Preparation](docs/PREPARATION.md) → [architecture](docs/ARCHITECTURE.md) → [ordered build plan](docs/BUILD_PLAN.md) |
| Product reviewers | [Working plan](WORKING_PLAN.md) → [console specification](docs/CONSOLE_SPEC.md) |

[Documentation index](docs/README.md) · [Models and disclosures](docs/DISCLOSURES.md)

## Intended prototype

```text
Laptop webcam → local vision observations ─┐
Labelled simulated sensors ────────────────┴→ event rules → console alerts
                                                 │
                                                 └→ structured facts
                                                       │
                                                 Qwen3 0.6B / Ollama
                                                       │
                                                 local explanations
```

- **Vision:** small local models provide supported observations.
- **Alerts:** event rules assign severity and retain the supporting evidence.
- **Language model:** Qwen3 0.6B explains supplied facts and answers questions about
  local event history. It is text-only; it does not inspect frames or set severity.
- **Console:** planned React/Vite interface served by the local Python/FastAPI app,
  shown on an HDMI/USB-C external display.
- **Offline operation:** all packages, models and UI assets are prepared beforehand;
  core operation must work after restarting with internet connections disabled.

Monitoring and alerts stay usable if the LLM fails; explanations fall back to
labelled templates. Clothing, facial movements and posture alone do not establish
intent or dangerousness. Green means no configured alert condition was detected,
not a guarantee that opening the door is safe.

## Repository map

```text
backend/       Planned camera, vision, events, storage and local LLM integration
frontend/      Planned resident console
hardware/      Future ESP32 camera and physical-sensor integration
assets/        Model acquisition and asset inventory instructions
scripts/       Repository maintenance utilities
demo/          Recording guide and eventual public demo links
docs/          Architecture, setup, evidence and judging navigation
WORKING_PLAN.md Approved prototype and future product roadmap
```

Folders currently contain scope notes, not working application modules. The model
weights, private recordings, local data and supplied briefing are excluded from Git.

## Run and verify

There is no application start command yet. Follow [preparation](docs/PREPARATION.md)
for the implementation checkpoint and model setup plan. To validate repository
Markdown links using Python 3, run from the repository root:

```sh
python3 scripts/check_docs.py
```

This check verifies documentation links only; it is not an offline-runtime test.

## Demo and roadmap

[Demo preparation](demo/README.md) tracks the recording and live demonstration.
No demo video or measured inference results are available yet.

Physical ESP32 streaming over local Wi-Fi, extended unattended operation,
household adaptation and bounded reinforcement learning are future milestones.
Resident feedback storage does not itself retrain a model.

## Contributing and licensing

See [contributing](CONTRIBUTING.md) for scope, Git workflow and verification rules.
Third-party model/tool licences are tracked in [disclosures](docs/DISCLOSURES.md).
A project source-code licence has not yet been selected.
