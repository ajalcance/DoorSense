# Offline demo and acceptance

Status: checklist only; every runtime check is Not run.

## Conditions

All packages, models and UI assets must be present before disconnecting. Use the
laptop webcam and a cable-connected external display. Disable Wi-Fi and disconnect
Ethernet/mobile tethering. Do not use Wokwi as a core runtime dependency. Stop and
restart both the application and Ollama while disconnected; an already-warm
browser tab is not sufficient startup evidence. Verify cloud features are disabled
and the model is already local; a template fallback does not prove Qwen inference.

## Ordered acceptance

| Check | Required evidence | Current result |
| --- | --- | --- |
| Local startup | App and assets load after restart without external connections | Not run |
| Fresh camera input | New webcam frames visibly produce actual model results | Not run |
| Local Qwen call | Fresh request reaches loopback Ollama and returns genuine Qwen3 0.6B output after offline restart | Not run |
| Explanation grounding | Distinct supplied events/questions preserve facts and provenance; missing evidence is explicit | Not run |
| LLM failure handling | Missing model, daemon failure, timeout and invalid output trigger labelled fallback without blocking alerts | Not run |
| LLM configuration | Actual model digest, cloud-disabled configuration, bounded context/output and thinking disabled recorded | Not run |
| Supported observations | Selected face/body/object outputs checked on fresh attempts | Not run |
| Sensor provenance | Simulated input controls and derived events remain labelled | Not run |
| Orange event | Defined repeated-bell/occupancy rule fires with recorded evidence | Not run |
| Red event | Corroborated simulated impact/contact rule fires with recorded evidence | Not run |
| Availability | Camera/model failure produces explicit unavailable state | Not run |
| Severity persistence | Urgent sensor event stays visible during video failure | Not run |
| Local evidence | Actual saved media can be replayed/deleted; missing media is explicit | Not run |
| Feedback | Explicit resident labels save locally without a claim of automatic retraining | Not run |
| External requests | Inspect runtime requests/connections; no external dependency in core workflow | Not run |
| Performance | Record vision/Qwen cold and warm latency, combined memory, responsiveness and stale-response handling on M1 8 GB | Not run |
| GitHub reproduction | Actual adapter/prompts/schema/checks and local setup instructions recreate inference; model/asset disclosures included | Not run |
| Model quality | Record misses/false alerts on distinct normal and staged-event examples | Not run |
| Display usability | Actual external-screen layout, readable states and working controls | Not run |

Observations and measurements must reflect the actual implementation. Do not use
fake benchmarks, prerecorded predictions, invented model scores or simulated
sensor events presented as camera-detected activities. A short demo does not
establish reliable 24/7 protection or a measured probability of danger.

## Demonstration sequence

1. Show disconnected networking and launch the application.
2. Start monitoring and enter the webcam view; show live local inference.
3. Demonstrate only validated visible facial/body/object observations.
4. Press the labelled simulated doorbell repeatedly; show the orange event reason
   and a genuine Qwen explanation grounded in those inputs. Show actual model
   identity/timing in diagnostics and ask a question about that local event.
5. Trigger labelled impact/contact events; show the red event and supporting inputs.
6. Demonstrate a camera outage while preserving the urgent event.
7. Acknowledge, review available local evidence and record explicit feedback.

The recording may be concise, but the software must remain interactive for a
potential live finalist demonstration. Actual unimplemented steps should be
removed from the recording or identified as roadmap work.

## Suggested disclosure, to amend to actual delivered capabilities

> This prototype uses the laptop webcam in place of the planned ESP32 door camera.
> Vision inference and event processing run locally on an Apple M1 laptop.
> Qwen3 0.6B via local Ollama explains structured events; it does not inspect
> camera images or determine alert severity. Templates handle LLM failures.
> Doorbell, vibration and door-contact events are simulated and labelled.
> The core console operates without internet after dependencies and assets are
> prepared. Physical ESP32 integration and reinforcement learning are future work.

If model integrations do not all work, list exactly which ones run. Do not claim
ESP32 emulation unless firmware actually runs in an emulator. Do not claim AI
runs on the ESP32 when it runs on the laptop.

## Hackathon requirements from supplied briefing

Source: AppBuildersPH Hackathon 2026 Participant Briefing.pdf (supplied by the participant; local reference under private/reference/)

- Page 9: working product, meaningful local inference, substantially built during
  the hackathon, and disclosed models/tools.
- Page 15: finalist pitch and live demo, five minutes plus three minutes Q&A.
- Pages 16/24/25: demo video, required X or LinkedIn video post with stated tags,
  public GitHub repository and disclosures; submission deadline is 2026-10-10
  10:00 AM Philippine time, one submission, deadline code freeze.
- Page 26: finalists need an on-site representative and laptop.
- Page 28: public live deployment is unnecessary if recreation instructions exist.
- Hardware-simulation eligibility is not explicitly settled; organiser
  clarification remains pending. Do not represent it as approved.

Submission/publication requires internet separately. Repository setup is separate
from submitting an entry; no demo video, social post or hackathon submission exists yet.
