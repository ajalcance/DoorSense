# Current demo acceptance

The [two-scenario runbook](../demo/DEMO_RUNBOOK.md) is the current demo sequence.
Earlier sensor/event acceptance reports are historical, not requirements for this
face-only presentation. See [technical overview](TECHNICAL_OVERVIEW.md).

## Evidence already available

- Owner screenshots: genuine live camera/person inference, saved face preview,
  rejected comparisons and a Family member result at distance 53.70 versus 65.
- Automated audit: backend/frontend regression, production/static builds, static
  markup, bundle invariants and documentation links. Recognition tests actually
  train/predict LBPH on synthetic textures; they do not measure human accuracy.
- Earlier local Qwen runs: four supported fact selections worked; model-only
  identity abstention failed and is constrained by application guards.

## Remaining owner live checks

Record actual result and evidence for each item; do not mark it passed from source.

1. **Current interface:** rebuilt/refreshed console shows the parent toggle,
   camera banner and one AI Analysis view, with no activity controls or tabs.
2. **Family enrollment:** save a clear single face, preview the real image, move
   away/return and observe fresh accepted/rejected comparisons and displayed reasons.
3. **Unknown/deletion:** delete the example; subsequent fresh face becomes Unknown,
   example count becomes zero and no old/in-flight match reappears. Restart confirms deletion.
4. **Parent mode:** off gives recognition only; on gives family parent-check or
   unknown/unclear keep-closed guidance. Stop/reset disables mode and preserves enrollment.
5. **Limited evidence:** no/multiple/occluded/stale faces cannot display a valid
   current match or retain an old score. Camera failure remains explicit.
6. **Automatic text analysis:** fresh changed evidence yields actual local Qwen
   findings with provenance. A missing/unavailable model shows fallback while
   camera analysis and parent controls remain responsive; no stale text replaces new results.
7. **Offline restart:** provision assets first, disconnect external networking,
   restart both console and Ollama, then repeat fresh camera/family/unknown steps.
   Inspect requests/connections separately; a warm tab is not startup evidence.
8. **Performance/display:** measure combined camera/Qwen latency, memory and
   responsiveness on M1 8 GB; check actual external-screen readability and controls.
9. **Reproduction/submission:** check startup from documented dependencies/assets,
   disclosures and actual public repository/demo/social URLs. Publication and
   submission require separate confirmation.

The final banner/toggle/automatic-analysis live trial, disconnected restart,
traffic inspection and human recognition evaluation remain pending. A successful
single demo match does not establish a recognition rate or security effectiveness.

`scripts/acceptance.py init` prepares the current face-demo observation checklist
with every outcome initially not run. It writes only to ignored `.runtime/` and
does not open the camera or test the app. Use a new observations filename if an
earlier report already exists; old v1 reports remain explicitly historical.
`scripts/reproduction_check.py` checks local source/assets for the face-only demo;
a passing inventory does not establish clean-machine or offline reproduction.

## Hackathon requirements

The supplied AppBuildersPH Hackathon 2026 Participant Briefing requires meaningful
local inference, a working product, model/tool disclosure and substantially
hackathon-built work (page 9). It specifies a five-minute finalist pitch plus
three-minute Q&A (page 15), repository/demo/social-video submission requirements
and 2026-10-10 10:00 AM Philippine-time deadline/code freeze (pages 16, 24–25).
An on-site representative and laptop are required for finalists (page 26); public
live deployment is unnecessary with recreation instructions (page 28).

Keep the private briefing outside Git. Prepared files do not prove submission.
