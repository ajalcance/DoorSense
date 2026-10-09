"""Keep the upstream metadata exception narrow; all other pip failures block."""
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import runtime_health as health


class HealthTests(unittest.TestCase):
    def check(self, code, stdout, stderr=""):
        return patch.object(health.subprocess, "run", return_value=subprocess.CompletedProcess([], code, stdout, stderr))

    def test_normal_success(self):
        with self.check(0, "No broken requirements found.\n"):
            self.assertEqual(health.dependencies()["status"], "passed")

    def test_known_error_requires_artifact_verification(self):
        with self.check(1, health.EXPECTED_FAILURE), patch.object(health, "verified_mediapipe_exception", return_value={"verified": True}) as verify:
            self.assertTrue(health.dependencies()["verified"])
            verify.assert_called_once()

    def test_additional_dependency_failure_blocks(self):
        with self.check(1, health.EXPECTED_FAILURE + "\nother package is broken"), patch.object(health, "verified_mediapipe_exception") as verify:
            with self.assertRaises(ValueError):
                health.dependencies()
            verify.assert_not_called()

    def test_unexpected_stderr_blocks(self):
        with self.check(1, health.EXPECTED_FAILURE, "unexpected failure"):
            with self.assertRaises(ValueError):
                health.dependencies()

    def test_modified_wheel_blocks(self):
        (health.ROOT / ".runtime").mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=health.ROOT / ".runtime") as temporary:
            root = Path(temporary)
            wheels = root / ".runtime/wheels"
            wheels.mkdir(parents=True)
            (wheels / health.MEDIAPIPE_WHEEL).write_bytes(b"not the publisher wheel")
            with patch.object(health, "ROOT", root):
                with self.assertRaisesRegex(ValueError, "publisher artifact"):
                    health.verified_mediapipe_exception()


if __name__ == "__main__":
    unittest.main()
