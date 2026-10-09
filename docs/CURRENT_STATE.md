# DoorSense current state

Updated: 2026-10-09, Asia/Manila.

This document records delivered work and current evidence. Planned features
belong in the working plan and specifications.

## Confirmed decisions

- User-approved product: a local doorway safety assistant with an indoor console.
- User-approved prototype: laptop webcam, local AI, external display, simulated
  door sensors, no internet required during core operation.
- User-confirmed computer: Apple M1 with 8 GB unified memory.
- Resource preference: smallest practical downloads.
- User-approved local LLM: Qwen3 0.6B via Ollama for explanations and local
  event-history questions, with short output, thinking disabled and template fallback.
- GitHub deliverable must expose genuine local LLM integration and offline setup;
  repository: https://github.com/ajalcance/DoorSense . Runtime integration is pending.

## Delivered

- Updated working plan preserving the future roadmap.
- Project README, judge guide and documentation index.
- Dedicated Hackathon/DoorSense workspace and repository scaffold, with
  ignore rules, contribution guidance and documentation-link checker.
- Offline architecture and component contracts.
- Console layout, state and interaction specification.
- Ordered implementation checkpoints.
- Offline acceptance and demo disclosure checklist.
- Qwen/Ollama integration specification, resource checks and GitHub evidence plan.

## Not implemented or verified

- Application code, camera access, model inference, console rendering, event
  processing, storage, recording, replay, or feedback capture.
- Ollama installation/configuration, Qwen weights, adapter, local generation,
  prompt quality, timeout/fallback behaviour or combined resource use.
- Package/model versions, installed dependencies, local asset inventory or sizes.
  The published 523 MB Qwen download size is a reference, not a local measurement.
- M1 memory use, inference latency, detection quality, or offline network behaviour.
- Camera resolution, macOS/Python version, camera permissions, external display
  configuration, and physical ESP32 board model.
- Physical camera capture, sensor accuracy, firmware emulation or LAN integration.
- Continuous 24/7 monitoring, threat-detection effectiveness, model training,
  reinforcement learning, mobile notifications or automatic improvement.

## External condition

The supplied briefing does not explicitly settle eligibility of simulated
hardware. Organiser clarification is pending. A submission video is required;
finalists must also be prepared for an on-site live demonstration.

## Next checkpoint

Preflight the remaining dependencies and assets. Build and measure genuine
camera/vision and Qwen local-inference loops, then integrate them with the event
engine and console. No runtime acceptance check has passed yet.
