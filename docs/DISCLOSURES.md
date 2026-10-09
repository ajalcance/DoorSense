# Models, tools and disclosures

Updated: 2026-10-09. This is an initial inventory, not proof of installation.

## Model inventory

| Asset | Selection/status | Licence/source | Local version, digest, size and performance |
| --- | --- | --- | --- |
| Qwen3 0.6B via Ollama (`qwen3:0.6b`, listed Q4_K_M) | Approved; not downloaded or tested | Apache-2.0; https://huggingface.co/Qwen/Qwen3-0.6B and https://ollama.com/library/qwen3:0.6b | Pending; published download 523 MB, not a local RAM measurement |
| Vision detector | Candidate small MediaPipe-compatible model; exact asset unselected | Record selected asset's publisher and licence | Pending |
| Face/Pose Landmarker | Incremental candidate features; not downloaded or validated | Record each model bundle's publisher and licence | Pending |

Use actual model hashes/digests, runtime versions and asset sizes once provisioned.
Text-model weights do not provide camera vision or automatic reinforcement learning.

## Tools and existing assets

- OpenAI Codex assisted planning, documentation, repository organisation and
  generation of the documentation-link checker. Application code is not built yet.
- Git and the GitHub connection are used for source control and repository setup.
- Ollama is the selected local LLM runtime; installation and configuration pending.
- Python/FastAPI/OpenCV/MediaPipe/SQLite and React/Vite are proposed application
  components; pin versions and record relevant licences after compatibility checks.
- The supplied participant briefing informed requirement summaries. Its PDF stays
  in local, ignored reference material; it is not redistributed in the repository.
- No model weights, private camera footage or personal event history are committed.

## Simulation and evidence boundaries

The real laptop webcam represents the future ESP32 camera. Doorbell, contact and
vibration inputs will be explicitly simulated. No physical ESP32 firmware or sensor
performance is validated. Do not claim ESP32 inference or camera emulation.

Documentation checks are separate from runtime checks. No inference benchmark,
offline acceptance run, video recording, public social post or hackathon submission
has been completed. Update this disclosure to actual delivered work before submission.

## Project licence

No project source-code licence has been selected. Third-party models and tools
remain subject to their own licences; public repository visibility is not a
project licence choice.
