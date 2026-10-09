# Backend

Application implementation pending. Planned Python modules will cover camera
capture, vision observations, deterministic events, local storage and the Qwen
adapter served through FastAPI. Keep those responsibilities independently testable.

The planned `local_llm.py` calls loopback Ollama with Qwen3 0.6B, supplied facts,
short output, thinking disabled, validation and template fallback. It must never
assign alert severity or block camera/event processing.

See [architecture](../docs/ARCHITECTURE.md) and [build plan](../docs/BUILD_PLAN.md).
Add actual dependency and startup files after the compatibility spike.
