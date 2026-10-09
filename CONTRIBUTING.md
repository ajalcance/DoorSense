# Contributing to DoorSense

This repository is a bounded hackathon prototype. Read the
[working plan](WORKING_PLAN.md), [architecture](docs/ARCHITECTURE.md) and
[current state](docs/CURRENT_STATE.md) before changing scope.

## Git workflow

- `main` is the shared, reviewable baseline.
- Use focused branches such as `codex/local-llm` or `codex/console` for new work.
- Under the current DoorSense sandbox, `.git` is read-only: preserve the existing
  dirty checkout; do not create branches, commits, resets or Git worktrees through
  commands. A future owner Git workflow must respect the active permissions.
- Keep commits small and descriptive: `docs:`, `feat:`, `fix:` or `chore:`.
- Describe the resulting behaviour, relevant validation and remaining limitations
  in a pull request. Attach actual evidence; mark checks not run when appropriate.
- Update current-state and setup instructions when a capability becomes usable.

## Implementation standards

Keep camera, recognition, LLM adapter and presentation separate. Bound queues,
request timeouts and model output. All runtime assets and inference must be local.
Do not auto-download models, introduce cloud fallbacks or commit credentials,
recordings, private event history or large model binaries.

Preserve source/replay provenance and fresh-frame checks. The production demo
uses Family member/Unknown appearance matching; Child safety mode gates guidance.
Do not reactivate sensor/occupancy rules or manual category selection. Qwen selects
supplied text facts; it cannot change the camera verdict. Do not infer intent,
criminality, safety or opening permission from a face. Enrollment is explicit
supervised learning, not RL or autonomous learning from repeated visits.

## Verification

Run `python3 scripts/check_docs.py` for documentation changes. Select meaningful
checks for actual code changes; do not claim fixtures prove live inference.
Use the [acceptance checklist](docs/DEMO_AND_ACCEPTANCE.md) for runtime evidence.
Owner camera/matching and earlier bounded Qwen evidence are recorded; final
unified UI, automatic text flow, combined performance and offline acceptance remain
pending. Follow the
[handoff ways of working](docs/HANDOFF_SLICE_5.md): design-first UI review, honest
evidence labels, contained writes and complete owner command blocks.

Do not add a project licence without the owner's choice. Record third-party
licences and exact downloaded model/runtime versions during preflight.
