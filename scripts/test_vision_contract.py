"""Fixture contract tests; these do not establish real model detection quality."""
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import os

ROOT = Path(__file__).resolve().parents[1]
os.environ["MPLCONFIGDIR"] = str(ROOT / ".runtime/matplotlib")
os.environ["XDG_CACHE_HOME"] = str(ROOT / ".runtime/cache")
sys.path.insert(0, str(ROOT / "backend"))
import numpy as np
from doorsense.camera import Frame
from doorsense.vision import PersonDetector
import doorsense.vision as vision


class VisionTests(unittest.TestCase):
    def test_model_hash_mismatch_blocks_before_task_creation(self):
        manifest = {"vision": {"filename": "efficientdet_lite0.int8.v1.tflite", "acquired_sha256": "0" * 64}}
        with patch.object(vision.json, "loads", return_value=manifest), patch.object(vision.mp.tasks.vision.ObjectDetector, "create_from_options") as create:
            with self.assertRaisesRegex(ValueError, "hash mismatch"):
                PersonDetector()
            create.assert_not_called()

    def test_person_output_keeps_exact_source_frame_and_ignores_other_labels(self):
        task = SimpleNamespace(detect=lambda image: SimpleNamespace(detections=[
            SimpleNamespace(categories=[SimpleNamespace(category_name="person", score=0.7)],
                            bounding_box=SimpleNamespace(origin_x=2, origin_y=3, width=4, height=5)),
            SimpleNamespace(categories=[SimpleNamespace(category_name="car", score=0.9)])]))
        detector = PersonDetector.__new__(PersonDetector)
        detector.task = task
        frame = Frame(17, "fixture-capture-time", 10, np.zeros((10, 10, 3), dtype=np.uint8))
        result = detector.detect(frame)
        self.assertEqual(result["sequence"], 17)
        self.assertEqual(result["captured_at"], "fixture-capture-time")
        self.assertEqual(result["source"], "laptop_webcam")
        self.assertEqual(len(result["people"]), 1)
        self.assertEqual(result["people"][0]["box"], [2, 3, 4, 5])
        self.assertNotIn("severity", result)
        self.assertNotIn("intent", result)


if __name__ == "__main__":
    unittest.main()
