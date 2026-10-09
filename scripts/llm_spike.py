#!/usr/bin/env python3
"""Owner-run Qwen inference on explicitly synthetic event records; no camera capture."""
import argparse
import asyncio
from dataclasses import replace
from datetime import datetime, timezone
import json
from pathlib import Path
import resource
import statistics
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from doorsense.local_llm import BASE_URL, DIGEST, MODEL, PROMPT_VERSION, EventContext, Fact, LocalLLM


def examples():
    stamp = datetime.now(timezone.utc).isoformat()
    def fact(id, text, source="simulated_sensor"):
        return Fact(id, text, source, stamp)
    return [
        (EventContext("synthetic-arrival", 1, "monitoring", "No configured alert condition.",
                      (fact("person", "A person was detected in the laptop webcam view.", "laptop_webcam"),
                       fact("bell_zero", "The simulated doorbell count is zero."))),
         "What was observed?", "evidence", {"person"}),
        (EventContext("synthetic-bell", 1, "review", "Three simulated bell presses within ten seconds.",
                      (fact("bell", "Three simulated doorbell presses occurred within ten seconds."),)),
         "Why does this event require review?", "evidence", {"bell"}),
        (EventContext("synthetic-urgent", 1, "urgent", "Repeated impacts and contact opening while armed.",
                      (fact("impacts", "Three simulated door impacts occurred while armed."),
                       fact("contact", "The simulated door contact changed to open while armed."),
                       fact("camera", "Camera assessment is unavailable.", "system")),
                      ("Camera assessment is unavailable.", "Identity and intent are not established.")),
         "Which evidence supports the existing urgent event?", "evidence", {"impacts", "contact"}),
        (EventContext("synthetic-identity-question", 1, "monitoring", "No configured alert condition.",
                      (fact("person", "A person was detected in the laptop webcam view.", "laptop_webcam"),)),
         "What is this person's name?", "unavailable", set()),
    ]


def ollama_process_rss():
    """Current aggregate RSS of the repository daemon and descendants, not unified RAM."""
    executable = str(ROOT / ".runtime/ollama-0.40.1/ollama")
    completed = subprocess.run(["/bin/ps", "-axo", "pid=,ppid=,rss=,command="],
                               capture_output=True, text=True, timeout=2, check=True)
    rows = []
    for line in completed.stdout.splitlines():
        parts = line.strip().split(None, 3)
        if len(parts) == 4:
            try:
                rows.append((int(parts[0]), int(parts[1]), int(parts[2]), parts[3]))
            except ValueError:
                continue
    included = {pid for pid, parent, rss, command in rows if command == executable + " serve"}
    if not included:
        return None
    while True:
        children = {pid for pid, parent, rss, command in rows if parent in included}
        if children <= included:
            break
        included |= children
    return round(sum(rss for pid, parent, rss, command in rows if pid in included) / 1024, 1)


async def run(args):
    report = {"scope": "four genuine local Qwen calls and one application question guard on synthetic records; no camera, integrated console or offline acceptance",
              "endpoint": BASE_URL, "model": MODEL, "digest": DIGEST, "prompt_version": PROMPT_VERSION,
              "question_contract": "bounded-presets-v1; unsupported questions handled by application, not Qwen",
              "configuration": {"think": False, "stream": False, "num_ctx": 2048, "num_predict": 128,
                                "temperature": 0, "deadline_seconds": 45, "keep_alive": "60s"},
              "wording": "Qwen selects evidence IDs; displayed wording is supplied facts/template.",
              "cold_unload_requested": args.cold, "cases": []}
    llm = LocalLLM()
    stop = asyncio.Event()
    tasks = []
    detector = None
    memory = []
    vision_times = []
    vision_errors = []
    began = time.monotonic()

    async def sample_memory():
        while not stop.is_set():
            try:
                sample = await asyncio.to_thread(ollama_process_rss)
                if sample is not None:
                    memory.append(sample)
                    if len(memory) > 300:
                        del memory[0]
            except (OSError, subprocess.SubprocessError):
                pass
            try:
                await asyncio.wait_for(stop.wait(), 0.5)
            except TimeoutError:
                pass

    async def vision_loop():
        import numpy as np
        from doorsense.camera import Frame
        pixels = np.zeros((480, 640, 3), dtype=np.uint8)
        sequence = 0
        while not stop.is_set():
            started = time.monotonic()
            sequence += 1
            frame = Frame(sequence, datetime.now(timezone.utc).isoformat(), started, pixels)
            try:
                result = await asyncio.to_thread(detector.detect, frame)
                vision_times.append(result["inference_ms"])
                if len(vision_times) > 300:
                    del vision_times[0]
            except Exception as error:
                vision_errors.append(str(error))
                break
            try:
                await asyncio.wait_for(stop.wait(), max(0.001, 0.2-(time.monotonic()-started)))
            except TimeoutError:
                pass

    try:
        # Pinned metadata checked before explicit unload or model generation.
        from check_runtime import ollama
        report["preflight"] = await asyncio.to_thread(ollama)
        if args.cold:
            async with asyncio.timeout(15):
                await llm._json("POST", "/api/generate", {"model": MODEL, "keep_alive": 0})
        if args.with_vision:
            import os
            os.environ["MPLCONFIGDIR"] = str(ROOT / ".runtime/matplotlib")
            os.environ["XDG_CACHE_HOME"] = str(ROOT / ".runtime/cache")
            from doorsense.vision import PersonDetector
            detector = PersonDetector()
            tasks.append(asyncio.create_task(vision_loop()))
        tasks.append(asyncio.create_task(sample_memory()))
        cases = examples()
        # Same bell facts repeated to measure a subsequent request without unloading.
        cases.append((replace(cases[1][0], event_id="synthetic-bell-warm"), *cases[1][1:]))
        for index, (context, question, kind, required_ids) in enumerate(cases):
            context = replace(context, received_monotonic=time.monotonic())
            result = await llm.explain(context, question, diagnostics=True)
            selected_ids = {f["id"] for f in result.get("evidence", [])}
            if kind == "unavailable":
                passed = (result["source"] == "application_unavailable" and
                          result["answer_kind"] == "unavailable" and not selected_ids)
            else:
                passed = (result["source"] == "qwen_evidence_selection" and result["answer_kind"] == kind
                          and required_ids <= selected_ids)
            report["cases"].append({"label": context.event_id, "question": question,
                                    "input": {"severity": context.severity, "rule_reason": context.rule_reason,
                                              "facts": [f.__dict__ for f in context.facts],
                                              "uncertainties": list(context.uncertainties)},
                                    "response": result, "expected_selection_met": passed,
                                    "check_kind": "application_guard" if kind == "unavailable" else "genuine_generation",
                                    "request_position": index+1})
            print(f'{context.event_id}: {result["source"]}, {result.get("elapsed_ms", 0):.0f} ms, expected selection {passed}', flush=True)
            if result.get("diagnostics"):
                print("Rejection diagnostic: " + json.dumps(result["diagnostics"]), flush=True)
        report["status"] = "passed_bounded_examples" if all(c["expected_selection_met"] for c in report["cases"]) else "needs_review"
        async with asyncio.timeout(5):
            report["loaded_models"] = await llm._json("GET", "/api/ps")
    except Exception as error:
        report["status"] = "blocked"
        report["error"] = str(error)
    finally:
        stop.set()
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        if detector:
            detector.close()
        await llm.close()
    report["measurement_seconds"] = round(time.monotonic()-began, 2)
    scale = 1024*1024 if sys.platform == "darwin" else 1024
    report["spike_process_peak_rss_mb"] = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/scale, 1)
    report["ollama_daemon_and_children_sampled_max_rss_mb"] = max(memory) if memory else None
    report["memory_note"] = "Process RSS, sampled up to 300 observations; excludes a true unified/GPU memory peak. Do not sum shared mappings as physical RAM."
    if args.with_vision:
        report["concurrent_vision"] = {"source": "synthetic_blank_pixels", "camera_opened": False,
                                        "inference_cap_hz": 5, "bounded_sample_count": len(vision_times),
                                        "median_inference_ms": round(statistics.median(vision_times), 2) if vision_times else None,
                                        "p95_inference_ms": round(sorted(vision_times)[max(0, int(len(vision_times)*0.95)-1)], 2) if vision_times else None,
                                        "errors": vision_errors,
                                        "scope": "genuine concurrent detector calls; no webcam responsiveness or quality evidence"}
        if report["status"] != "blocked" and (not vision_times or vision_errors):
            report["status"] = "needs_review"
    destination = (ROOT / ".runtime/llm-session.json").resolve()
    if not destination.is_relative_to(ROOT):
        raise ValueError("Report destination escapes DoorSense")
    destination.parent.mkdir(exist_ok=True)
    destination.write_text(json.dumps(report, indent=2)+"\n")
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "passed_bounded_examples" else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", action="store_true", help="explicitly send local generation requests")
    parser.add_argument("--cold", action="store_true", help="unload pinned local model first to request a cold start")
    parser.add_argument("--with-vision", action="store_true", help="concurrent blank-pixel detector calls; no camera")
    args = parser.parse_args()
    if not args.run:
        print("Plan only: --run sends four local Qwen requests and checks one application question guard on synthetic events. "
              "--cold explicitly unloads Qwen first; --with-vision measures concurrent blank-pixel detection. "
              "No downloads, camera capture or offline acceptance. Keep the owner Ollama terminal running.")
        return 0
    return asyncio.run(run(args))


if __name__ == "__main__":
    raise SystemExit(main())
