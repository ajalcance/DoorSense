# Slices 1–10 audit and remaining acceptance

## Latest child-mode and visit-scenario contract (2026-10-10)

The [current console contract](CONSOLE_SPEC.md) supersedes earlier arming,
door-open urgency and visitor-label wording below. Parent-enabled Child safety
mode is optional; camera viewing remains available while it is off. Simulation is
one visitor-category/camera/sensor workflow, with only Family member and Unknown.
Categories are parent-confirmed snapshots, not database recognition or intent.
Urgent requires fresh person detection plus three simulated impacts on a known
closed door within five seconds. Events contain webcam and sensor provenance;
opening is not required. Missing/stale camera evidence prevents combined urgent.
Earlier saved history is preserved. [Owner checks](SIMULATION_CONSOLE_ACCEPTANCE.md)
for genuine combined camera/Qwen/browser/offline acceptance remain pending.


Updated 2026-10-10. Scope: owner-authorised Slice 8 implementation, Slice 9
acceptance tooling, Slice 10 reproduction/demo preparation and approved dashboard
redesign. No new dependency, model acquisition, service/capture startup, Git
mutation, publication or sandbox change was performed.

## Findings and corrections

| Finding | Correction/evidence |
| --- | --- |
| Camera answer could survive a service restart with identical counts/revisions | Include service token in frontend context key; regression added |
| Additional face/pose facts could change without person count changing | Backend and frontend signatures include scene facts/availability; discard pending answer; regressions added |
| Reusing stabilizer state after camera restart could imply continuity | Reset in the sequential worker on session revision; gaps/count/visibility loss reset descriptions |
| Optional model missing/failing could break person monitoring | Separate per-feature availability, task failure/cleanup and loaded hashes; injected failure coverage |
| Slow optional inference could repeatedly expire the entire preview | Per-feature measured budget and explicit disable/cleanup; no cloud fallback or unbounded queue |
| Partial/multiple faces or off-frame wrists could produce overconfident descriptions | Complete in-frame face mesh; single-person/single-face/body and wrist/shoulder visibility requirements; conservative two-frame confirmation |
| Person text used “1 people” | Shared original frame facts use singular/plural correctly |
| Dashboard confidence could imply safety | Actual detector-score range only; no danger score, Qwen confidence or family recognition |
| Manual expected-visit label could be mistaken for live recognition | Label is explicitly an owner-confirmed snapshot with frame/time/source; expires, clears on Stop/loss/count change; cannot reduce severity |
| Parent guidance could depend on Qwen or vanish on camera failure | Screen banner derives from active rule independent of camera/Qwen; remains during outage |
| New API requests could bypass local protections | Reuse bounded JSON, token, same-origin/host enforcement; unsupported labels/freshness rejected |
| Acceptance tooling could mark unrun tests complete | Every owner checkpoint defaults Not run; require concrete outcomes/time and session metadata; injected checks are rejected as owner evidence |
| Reproduction inventory could include private artifacts | Explicit source allowlist excludes weights, data/media, caches, credentials, protected metadata and obsolete presentation modules |
| Offline restart documentation omitted Ollama's activation flag | Owner commands use `scripts/start_ollama.py --serve`; plan-only invocation is not a daemon startup |

The integrated synthetic regression exercises sensor review/urgent creation,
scene-independent severity, explain route, real JPEG encoding/storage, snapshot/
clip API, replay, acknowledgement, feedback, camera Stop, database reopen and
media deletion. It opens no device, model or listening port. It is not offline
runtime proof or new genuine inference.

## Evidence boundaries

Simulation-console automated run passed: **109 backend regression tests, 32 frontend session
tests and 43 static markup checks**, production build, live-bundle invariants and
documentation links. Existing earlier 44 Python/44 npm metadata records/imports and pinned
Ollama/Qwen/EfficientDet bytes passed recheck. Reproduction inventory correctly
reports face and pose assets missing/unverified; those are genuine blockers.
The five obsolete production presentation/preview paths were verified absent.
Owner-requested assessment header is now two compact logical rows, with responsive
wrapping for long real rule reasons and explicit historical/source labels.

The approved persistent simulation column/header navigation is implemented with
backend contact, rolling input windows, occupancy freshness and six recent replies.
New regression checks cover debounce/expiry, contact across cancel/re-arm,
pre-arm open exclusion, refresh/API reply consistency, newer input state versus
stale polls, late replies after service restart, reset and stale Qwen responses.
Input revision is separate from alert revision to preserve explanation behavior.
No rule thresholds changed. Prior audit JSON was preserved before the new run.
`git diff --check` passed. No services/camera, network, dependency/model installation,
protected-file changes or Git mutations were performed. Owner checks for the new
layout and red urgent flow are [still pending](SIMULATION_CONSOLE_ACCEPTANCE.md).

Run [audit.py](../scripts/audit.py) for the current regression/build/static-markup
results and exact source fingerprints in ignored `.runtime/source-audit.json`.
Tests cover all ten slices' implemented boundaries; only owner execution can
establish their live acceptance. Static markup checks do not click browser tabs
or prove screen fit, focus behaviour or genuine inference. Browser policy blocked
Codex loopback rendering; no workaround was attempted.

The owner's 2026-10-09 23:46 screenshot shows a genuine integrated webcam frame,
person box/count and Qwen-selected evidence. This is owner-observed partial
integration, not a storage/restart or offline test. Existing model-only identity
abstention failure remains documented; an application guard is a separate check.

## Ready versus blocked

| Area | State |
| --- | --- |
| Existing Slices 1–7 source contracts | Preserved and covered by regression, including integrated synthetic persistence/media flow |
| Slice 8 person/scene code and dashboard | Implemented; injected/source checks; face/pose assets and genuine quality/resource trials missing |
| Slice 9 acceptance recorder/reviewer | Implemented; full disconnected restart, traffic and live failure evidence not run |
| Slice 10 local reproduction/demo package | Prepared; clean-machine reproduction, licence review, actual video/publication/submission not complete |
| Family recognition, emotion and cap/glasses image classification | Outside delivered lightweight scope; no VLM added by owner choice |

Therefore Slices 1–10 cannot be labelled fully accepted or reliable protection
yet. Next owner step: acquire/test Face Landmarker, then pose, then combined
pipeline, following [exact commands and checkpoints](SLICES_8_10.md).
