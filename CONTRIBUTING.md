# Contributing to DoorSense

This repository is a bounded hackathon prototype. Read the
[working plan](WORKING_PLAN.md), [architecture](docs/ARCHITECTURE.md) and
[current state](docs/CURRENT_STATE.md) before changing scope.

## Git workflow

- `main` is the shared, reviewable baseline.
- Use focused branches such as `codex/local-llm` or `codex/console` for new work.
- Keep commits small and descriptive: `docs:`, `feat:`, `fix:` or `chore:`.
- Describe the resulting behaviour, relevant validation and remaining limitations
  in a pull request. Attach actual evidence; mark checks not run when appropriate.
- Update current-state and setup instructions when a capability becomes usable.

## Implementation standards

Keep camera, event rules, LLM adapter and presentation separate. Bound queues,
request timeouts and model output. All runtime assets and inference must be local.
Do not auto-download models, introduce cloud fallbacks or commit credentials,
recordings, private event history or large model binaries.

Preserve simulated/replay provenance. Alert severity belongs to the event engine;
LLM output cannot change it. Do not infer identity, actual emotion, intent or
criminality from appearance. Feedback capture is separate from training and RL.

## Verification

Run `python3 scripts/check_docs.py` for documentation changes. Select meaningful
checks for actual code changes; do not claim fixtures prove live inference.
Use the [acceptance checklist](docs/DEMO_AND_ACCEPTANCE.md) for runtime evidence.
Camera, Ollama and combined M1 performance checks remain pending until implemented.

Do not add a project licence without the owner's choice. Record third-party
licences and exact downloaded model/runtime versions during preflight.
