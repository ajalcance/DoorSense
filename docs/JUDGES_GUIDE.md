# Judge guide

## What DoorSense aims to solve

A door camera shows a scene; DoorSense aims to help residents understand the event
and its supporting evidence through a local indoor console. The core workflow is
designed to remain available without internet after provisioning.

## Where to inspect

1. [Current state](CURRENT_STATE.md): delivered work and honest verification status.
2. [Architecture](ARCHITECTURE.md): camera/vision → event rules → local Qwen → console.
3. [Build plan](BUILD_PLAN.md): bounded prototype implementation sequence.
4. [Demo and acceptance](DEMO_AND_ACCEPTANCE.md): actual results will be recorded here.
5. [Demo materials](../demo/README.md): recording and live-demo links when ready.
6. [Disclosures](DISCLOSURES.md): models, tools, AI-assisted work and simulated hardware.

## Code navigation

The initial commit contains documentation and scaffolding. Application code is
pending. Its planned homes are [backend](../backend/README.md),
[frontend](../frontend/README.md) and [hardware](../hardware/README.md).
The backend local LLM adapter will expose the real loopback API call, prompts,
validation and fallback. Prepared diagrams or illustrative outputs are not
model-inference evidence.

## What the demo must establish

Fresh webcam input produces genuine local vision observations. Labelled simulated
sensors trigger evidence-based alerts. Qwen3 0.6B, running locally through Ollama,
explains supplied event facts. Restarting offline produces a fresh model response;
a template fallback cannot count as proof of Qwen inference. Record actual model
identity, response timing and combined memory use on the M1 8 GB.

The laptop webcam substitutes for the future ESP32 camera. No claim is made that
AI runs on the ESP32, that firmware is emulated, or that the prototype establishes
reliable 24/7 protection. Physical integration and learning remain roadmap work.
