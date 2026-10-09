#!/usr/bin/env python3
"""Slice 3 native preview: S start, P pause/release, Q quit. No media is saved."""
import argparse
from collections import deque
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import resource
import statistics
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
cache = (ROOT / ".runtime").resolve()
if not cache.is_relative_to(ROOT):
    raise ValueError("Runtime cache escapes DoorSense")
os.environ["MPLCONFIGDIR"] = str(cache / "matplotlib")
os.environ["XDG_CACHE_HOME"] = str(cache / "cache")
sys.path.insert(0, str(ROOT / "backend"))

import cv2
import numpy as np
from doorsense.camera import Frame, Webcam, frame_is_fresh
from doorsense.vision import PersonDetector

WINDOW = "DoorSense - camera and person detection spike"
MAX_AGE = 0.8


def save_report(filename, report):
    destination = (cache / filename).resolve()
    if not destination.is_relative_to(ROOT):
        raise ValueError("Diagnostic destination escapes DoorSense")
    cache.mkdir(exist_ok=True)
    destination.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2), flush=True)


def self_check():
    began = time.perf_counter()
    detector = PersonDetector()
    load_ms = (time.perf_counter() - began) * 1000
    try:
        outputs = []
        for index in range(4):
            frame = Frame(index, datetime.now(timezone.utc).isoformat(), time.monotonic(),
                          np.zeros((480, 640, 3), dtype=np.uint8), source="synthetic_blank_check")
            outputs.append(detector.detect(frame))
        report = {"status": "passed", "source": "synthetic_blank_check",
                  "scope": "genuine model calls on blank pixels; no webcam or detection-quality evidence",
                  "model_sha256": detector.model_sha256, "load_ms": round(load_ms, 2),
                  "inference_ms": [round(o["inference_ms"], 2) for o in outputs],
                  "person_counts": [len(o["people"]) for o in outputs],
                  "peak_process_rss_mb": round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024**2, 1)}
        save_report("vision-self-check.json", report)
    finally:
        detector.close()


def line(image, text, y, colour=(215, 215, 215), scale=0.5):
    cv2.putText(image, text[:105], (16, y), cv2.FONT_HERSHEY_SIMPLEX, scale, colour, 1, cv2.LINE_AA)


def preview(index, inference_hz):
    camera = Webcam(index)
    detector = None
    detector_error = None
    try:
        detector = PersonDetector()
    except Exception as error:
        detector_error = str(error)
    samples = deque(maxlen=300)
    processed = 0
    person_frames = 0
    active_seconds = 0.0
    previous_time = time.monotonic()
    result = None
    result_frame = None
    last_sequence = -1
    next_inference = 0.0
    errors = deque(maxlen=20)
    last_camera_error = None
    released = True
    cv2.namedWindow(WINDOW, cv2.WINDOW_AUTOSIZE)
    print("Camera OFF. Focus the preview, press S to start, P to pause/release, Q to quit. "
          "Only aggregate diagnostics are saved; no images, clips or per-frame history.", flush=True)
    try:
        while True:
            now = time.monotonic()
            state, message, latest = camera.snapshot()
            if state == "unavailable" and message != last_camera_error:
                errors.append(message)
                last_camera_error = message
            if state == "monitoring":
                active_seconds += now - previous_time
            previous_time = now
            if latest and detector and now >= next_inference and latest.sequence != last_sequence:
                if now - latest.captured_monotonic <= MAX_AGE:
                    try:
                        result = detector.detect(latest)
                        result_frame = latest
                        samples.append(result["inference_ms"])
                        processed += 1
                        person_frames += bool(result["people"])
                        last_sequence = latest.sequence
                    except Exception as error:
                        detector_error = str(error)
                        errors.append(detector_error)
                        camera.stop()
                        result = result_frame = None
                        detector.close()
                        detector = None
                    # At most one inference per period; never catch up a backlog.
                    next_inference = time.monotonic() + 1 / inference_hz
            state, message, latest = camera.snapshot()
            image = np.zeros((640, 640, 3), dtype=np.uint8)
            fresh = frame_is_fresh(result_frame, state, time.monotonic(), MAX_AGE)
            if fresh:
                pixels = result_frame.pixels.copy()
                for person in result["people"]:
                    x, y, w, h = person["box"]
                    cv2.rectangle(pixels, (x, y), (x + w, y + h), (225, 190, 85), 2)
                    line_text = f"person | model score {person['score']:.2f}"
                    cv2.putText(pixels, line_text, (max(0, x), max(18, y - 6)),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (225, 190, 85), 1, cv2.LINE_AA)
                # Results stay attached to the exact analysed frame, not a newer visitor.
                image[:480] = cv2.resize(pixels, (640, 480))
                line(image, f"People detected: {len(result['people'])} | Frame: {result['sequence']} | Age: {time.monotonic() - result_frame.captured_monotonic:.2f}s", 530)
                line(image, f"Capture UTC: {result['captured_at']}", 550)
                line(image, f"Inference UTC: {result['inferred_at']}", 570)
            else:
                line(image, "DOORSENSE | REAL WEBCAM SPIKE", 160, scale=0.65)
                line(image, "Preview paused or assessment unavailable", 195)
                line(image, "S: start   P: pause and release   Q: quit", 230)
                line(image, "No images or recordings are saved.", 265)
            if detector_error:
                state, message = "model unavailable", detector_error
            elif state == "monitoring" and not fresh:
                state, message = "assessment limited", "Waiting for fresh model output; stale results hidden."
            line(image, state.upper() + " | " + message, 505, (180, 180, 180))
            median = statistics.median(samples) if samples else 0
            fps = processed / active_seconds if active_seconds > 0 else 0
            line(image, f"Median inference: {median:.0f}ms | Measured inference rate: {fps:.1f}/s | cap: {inference_hz}/s", 596)
            peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024**2
            line(image, f"Peak process RSS: {peak:.0f}MB (excludes Ollama) | Scores are not danger probabilities", 620, scale=0.43)
            cv2.imshow(WINDOW, image)
            key = cv2.waitKey(15) & 0xFF
            if key in (ord("q"), ord("Q"), 27) or cv2.getWindowProperty(WINDOW, cv2.WND_PROP_VISIBLE) < 1:
                break
            if key in (ord("s"), ord("S")) and detector:
                camera.start()
            elif key in (ord("p"), ord("P")):
                released = camera.stop()
                result = result_frame = None
    finally:
        released = camera.stop()
        cv2.destroyAllWindows()
        if detector:
            detector.close()
        ordered = sorted(samples)
        save_report("vision-session.json", {
            "source": "laptop_webcam", "scope": "owner-run aggregate spike diagnostics; no stored media",
            "camera_frames": camera.frames_captured, "inferred_frames": processed,
            "frames_with_person": person_frames, "camera_released": released,
            "model_sha256": detector.model_sha256 if detector else None,
            "inference_cap_hz": inference_hz, "active_seconds": round(active_seconds, 2),
            "measured_inference_hz": round(processed / active_seconds, 2) if active_seconds else 0,
            "timing_sample_count": len(samples), "timing_sample_limit": 300,
            "median_inference_ms": round(statistics.median(samples), 2) if samples else None,
            "p95_inference_ms": round(ordered[max(0, int(len(ordered) * 0.95) - 1)], 2) if ordered else None,
            "peak_process_rss_mb": round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024**2, 1),
            "errors": list(errors) + ([detector_error] if detector_error else []),
            "acceptance": "requires owner confirmation of fresh detection, pause/restart and failure states"})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-check", action="store_true", help="run blank-image model calls without any camera/UI")
    parser.add_argument("--camera", type=int, default=0)
    parser.add_argument("--inference-hz", type=float, default=5)
    args = parser.parse_args()
    if args.camera < 0 or not 0.5 <= args.inference_hz <= 10:
        parser.error("Use camera index >=0 and inference rate between 0.5 and 10 Hz")
    if args.self_check:
        self_check()
    else:
        preview(args.camera, args.inference_hz)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Stopped by owner.")
    except Exception as error:
        print(f"Camera spike unavailable: {error}", file=sys.stderr)
        if "--self-check" in sys.argv:
            save_report("vision-self-check.json", {"status": "blocked", "source": "synthetic_blank_check",
                        "reason": str(error), "camera_opened": False,
                        "scope": "model self-check failure; no webcam or quality evidence"})
        raise SystemExit(1)
