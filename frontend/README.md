# DoorSense frontend

The local React 19.3.0 / Vite 8.3.4 console presents three columns: parent demo
controls, live camera, and one automatic **AI Analysis** view.

## Current experience

- Save, preview or delete one Family member reference.
- Enable Child safety mode independently of camera recognition.
- Show green family or amber unknown/unclear guidance over the camera when the
  mode is on; show recognition-only status when it is off.
- Explain the decision with measured LBPH distance, threshold and learning count.
  Detector percentages are separate; no safety or recognition probability is invented.
- Request bounded local text-model findings automatically when fresh evidence
  changes. Stale/superseded responses cannot replace current camera analysis.
- Keep detailed measurements expandable; no separate Qwen/evidence/learning tabs,
  manual questions, sensor controls or activity simulations in the production demo.

Stop/reset disable child guidance and preserve enrollment. Unavailable text
inference leaves camera analysis usable. Historical event presentation remains
only for compatibility/test paths; it is not the current demo workflow.

## Build and verify

Use Node 22 (>=22.12, <23), with dependencies installed from `package-lock.json`.
From this directory:

```sh
npm run test
npm run build
```

The backend serves `dist/`; refresh the browser after rebuilding. The repository
[source audit](../scripts/audit.py) also checks static rendering and bundle
invariants. Those checks do not replace a live browser/camera trial.

See [startup and demo](../docs/FAMILY_REFERENCE.md),
[technical overview](../docs/TECHNICAL_OVERVIEW.md) and
[acceptance](../docs/DEMO_AND_ACCEPTANCE.md).
