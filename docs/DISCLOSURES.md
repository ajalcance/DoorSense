# Models, tools and disclosures

Updated: 2026-10-10. See the [technical overview](TECHNICAL_OVERVIEW.md) for the
current face-only demo, stack, evidence status and improvement roadmap.

## Model inventory

| Asset | Selection/status | Licence/source | Local version, digest, size and performance |
| --- | --- | --- | --- |
| Qwen3 0.6B via Ollama (`qwen3:0.6b`, listed Q4_K_M) | Acquired, local bytes/served availability verified; four genuine v3 event examples worked; identity-question abstention failed; application guard handles unsupported questions | Apache-2.0, acquired licence layer checked; https://huggingface.co/Qwen/Qwen3-0.6B and https://ollama.com/library/qwen3:0.6b | Layers total 522,653,767 bytes; manifest `7df6b6e09427a769808717c0a93cadc4ae99ed4eb8bf5ca557c90846becea435`; initial cold request 2914.58 ms; accepted warm urgent request 599.09 ms; complete acceptance pending |
| EfficientDet-Lite0 int8 v1 | Local bytes verified; blank-pixel and actual webcam inference worked on M1; basic lifecycle owner-confirmed; broader quality/failure/offline acceptance pending | Google MediaPipe model distribution; asset-specific licence confirmation pending | 4,602,795 bytes; locally measured SHA-256 `0720bf247bd76e6594ea28fa9c6f7c5242be774818997dbbeffc4da460c723bb`; real run median 34.06 ms, P95 36.37 ms, process peak RSS 339.8 MB, excludes Ollama |
| Face Landmarker float16 v1 | Local asset acquired; owner live screenshots show face availability and LBPH matching; quality/offline acceptance remain unverified | Official MediaPipe versioned source in `assets/scene-models.json`; weight-specific licence review pending | 3,758,596 bytes; acquisition receipt SHA-256 `64184e229b263107bc2b804c6625db1341ff2bb731874b0bcc2fe6544e0bc9ff`; locally measured, not an independent publisher checksum |
| OpenCV LBPH recognizer | Installed and used to train/predict one parent-labeled local face example; not RL | Part of OpenCV contrib; no additional downloaded recognition weights | OpenCV 4.11.0.86; prototype distance threshold 65; measured scores are not calibrated confidence |
| Pose Landmarker Lite | Historical optional integration; not enabled in the current demo and not acquired in the inspected scene receipt | Official source in `assets/scene-models.json`; weight-specific licence review pending | No current pose-inference evidence claimed |

Use actual model hashes/digests, runtime versions and asset sizes once provisioned.
Text-model weights do not provide camera vision or automatic reinforcement learning.

## Tools and existing assets

- OpenAI Codex assisted planning, documentation, repository organisation and
  generation of setup/checkers and the initial camera/person-detection spike.
  Initial owner webcam/model run worked, with a first-permission threading bug
  subsequently fixed and a clean rerun verified. The owner confirmed entry/exit
  and physical pause/restart behavior. Broader camera quality/live failure handling,
  offline acceptance and the final unified console live trial remain pending. The Qwen
  evidence-selection adapter, schema/prompt, fallback fixtures and owner runner
  are implemented. Four supported v3 Qwen examples worked; model-only identity abstention failed.
  An application guard now returns unavailable for unsupported questions. General
  question quality, live failure and offline acceptance remain pending.
- Git and the GitHub connection are used for source control and repository setup.
- Ollama 0.40.1 CLI (MIT) is acquired; official archive checksum and extracted
  executable bytes verified. Archive is 167,470,715 bytes, SHA-256
  `66e1587711f3a06315b23782ba74897001da6c8b8edf6c0371f7533015a076dd`.
  Foreground daemon startup, cloud-disable startup configuration, loopback-only
  port 11434 listener and exact local Qwen metadata passed. Outbound-network
  behaviour and disconnected restarts remain unverified. First genuine generation
  is recorded above; full example acceptance is pending.
  Qwen layers are in the repository store and verified against registry digests.
- Direct Python/frontend pins are prepared in `backend/requirements.in` and
  `frontend/package.json`. The backend hash lock was generated and backend packages
  installed; imports passed on ARM64. Frontend integrity lock, installation and
  imports also passed. Initial vision and Qwen inference ran; full acceptance remains pending. MediaPipe's original universal2 wheel has an
  inconsistent Intel-only internal tag; the narrow project health check verifies
  the publisher archive, installed primary bindings and native loading, retaining
  vendor metadata. Raw `pip check` still reports that mismatch.
- MediaPipe 0.10.21 (Apache-2.0) is installed; its selection considered an
  [upstream telemetry report](https://github.com/google-ai-edge/mediapipe/issues/6291);
  no zero-telemetry claim has been verified. OpenCV contrib is the sole cv2 provider;
  NumPy/JAX/JAXlib pins address dependency compatibility, not training functionality.
- FastAPI/Uvicorn/HTTPX, React/Vite and their dependencies have a local metadata
  inventory in `.runtime/runtime-checks.json` (44 Python and 44 npm lock entries).
  Missing declarations still require review. Source packages and downloaded binaries
  must not be assumed to share the same licence as their model assets.
- The supplied participant briefing informed requirement summaries. Its PDF stays
  in local, ignored reference material; it is not redistributed in the repository.
- No model weights, private camera footage or personal event history are committed.

## Current demo and evidence boundaries

The production demo uses genuine webcam/person/face inference and one explicit
parent-enrolled LBPH reference. Family member/Unknown appearance matching drives
parent-controlled Child safety mode guidance, camera banners and one automatic
AI Analysis view. Sensors, occupancy alerts, manual visitor categories and tabs
are excluded. Owner screenshots show a real accepted family distance of 53.70
against cutoff 65; other comparisons were rejected. These observations are not
recognition benchmarks. Current source/build/static checks pass; final unified
UI, automatic Qwen, full offline and human accuracy acceptance remain pending.
No physical device/lock or autonomous learning is demonstrated.

## Historical implementation and simulation evidence (superseded)

The following records earlier slices and their tests. Simulated sensors and
manual snapshot labels described here are disabled in normal production use.


Slice 8 scene/dashboard code and Slice 9/10 acceptance/reproduction/demo tooling
are implemented/prepared. [Current contracts](SLICES_8_10.md) and
[audit](SLICES_8_10_AUDIT.md) retain all live acceptance blockers. Owner labels are
manual expected-visitor snapshots in that earlier slice. The approved
[two-scenario face demo](FAMILY_REFERENCE.md) now uses installed OpenCV LBPH:
parent-labeled crop enrollment, learned local histograms and fresh crop prediction.
No new dependencies or models were acquired. This is supervised appearance matching,
not RL, calibrated identity confidence or friendly-intent recognition. Synthetic
fit/predict checks are not human accuracy benchmarks. Child recommendations remain
application guidance. The owner declined heavier VLM acquisition: no cap/glasses classifier.

Slices 5–7 implement the owner-approved React/Vite console, local FastAPI service,
deterministic simulated bell/impact/contact and genuine-person occupancy rules,
and local SQLite event/feedback/explicit JPEG media storage. Presentation fixtures no longer ship. Test doubles remain test-only;
functional sensor simulations are visibly labelled and never genuine inference. Recording
is explicit; no automatic footage or model retraining. [Contracts and limits](SLICES_6_7.md).
76 backend and 24 frontend automated tests and 25 static markup checks passed;
rendered/genuine integration and offline acceptance remain pending. Browser policy
blocked Codex loopback rendering. Existing model-only identity abstention failed.

The real laptop webcam represents the future ESP32 camera. Doorbell, contact and
vibration inputs are explicitly simulated. No physical ESP32 firmware or sensor
performance is validated. Do not claim ESP32 inference or camera emulation.

Documentation checks are separate from runtime checks. Initial camera inference
timings are measured; comprehensive quality benchmarks, offline acceptance, video
recording, public social posts and hackathon submission remain pending. Update this disclosure to actual delivered work before submission.

## Project licence

No project source-code licence has been selected. Third-party models and tools
remain subject to their own licences; public repository visibility is not a
project licence choice.
