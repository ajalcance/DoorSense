"""One local person detector. No downloads, identity, intent or severity decisions."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time

import cv2
import mediapipe as mp

ROOT = Path(__file__).resolve().parents[2]


class PersonDetector:
    def __init__(self, threshold=0.45, include_objects=False):
        self.include_objects = include_objects
        spec = json.loads((ROOT / "assets/runtime-manifest.json").read_text())["vision"]
        path = (ROOT / "assets/models" / spec["filename"]).resolve()
        if not path.is_relative_to(ROOT) or not path.is_file():
            raise ValueError("Local detector model missing; no automatic download.")
        with path.open("rb") as source:
            self.model_sha256 = hashlib.file_digest(source, "sha256").hexdigest()
        if self.model_sha256 != spec["acquired_sha256"]:
            raise ValueError("Detector model hash mismatch; inspect local assets before starting.")
        options = mp.tasks.vision.ObjectDetectorOptions(
            base_options=mp.tasks.BaseOptions(model_asset_path=str(path),
                                             delegate=mp.tasks.BaseOptions.Delegate.CPU),
            running_mode=mp.tasks.vision.RunningMode.IMAGE,
            category_allowlist=["person", "backpack", "handbag", "suitcase"] if include_objects else ["person"],
            score_threshold=threshold, max_results=10 if include_objects else 5)
        self.task = mp.tasks.vision.ObjectDetector.create_from_options(options)

    def detect(self, frame):
        began = time.perf_counter()
        rgb = cv2.cvtColor(frame.pixels, cv2.COLOR_BGR2RGB)
        output = self.task.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb))
        elapsed = (time.perf_counter() - began) * 1000
        people, objects = [], []
        for detection in output.detections:
            for category in detection.categories:
                if category.category_name == "person" or (getattr(self, 'include_objects', False) and category.category_name in ('backpack', 'handbag', 'suitcase')):
                    box = detection.bounding_box
                    (people if category.category_name == 'person' else objects).append({"label": category.category_name, "score": float(category.score),
                                   "box": [box.origin_x, box.origin_y, box.width, box.height]})
        return {"source": frame.source, "sequence": frame.sequence,
                "captured_at": frame.captured_at, "inferred_at": datetime.now(timezone.utc).isoformat(),
                "inference_ms": elapsed, "people": people, "objects": objects}

    def close(self):
        self.task.close()
