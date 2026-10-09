"""Lifecycle/expiry checks with fake camera input; never access a real device."""
from pathlib import Path
import sys
import time
import threading
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
import numpy as np
from doorsense.camera import Frame, Webcam, frame_is_fresh


class FakeCapture:
    def __init__(self, opened=True, frames=True, release_error=False):
        self.opened = opened
        self.frames = frames
        self.released = False
        self.release_error = release_error

    def isOpened(self):
        return self.opened

    def set(self, *args):
        return True

    def read(self):
        return (True, np.zeros((4, 4, 3), dtype=np.uint8)) if self.frames else (False, None)

    def release(self):
        if self.release_error:
            raise RuntimeError("fixture release failure")
        self.released = True


def wait_for(predicate):
    deadline = time.monotonic() + 2
    while time.monotonic() < deadline:
        if predicate():
            return
        time.sleep(0.01)
    raise AssertionError("Fixture lifecycle did not reach expected state")


class CameraTests(unittest.TestCase):
    def test_no_capture_before_explicit_start(self):
        calls = []
        camera = Webcam(capture_factory=lambda index: calls.append(index))
        self.assertEqual(camera.snapshot()[0], "paused")
        self.assertEqual(calls, [])

    def test_pause_releases_and_discards_frame(self):
        capture = FakeCapture()
        camera = Webcam(capture_factory=lambda index: capture)
        camera.start()
        self.addCleanup(camera.stop)
        wait_for(lambda: camera.snapshot()[2] is not None)
        self.assertFalse(camera.start())
        self.assertTrue(camera.stop())
        self.assertTrue(capture.released)
        self.assertIsNone(camera.snapshot()[2])
        self.assertEqual(camera.snapshot()[0], "paused")

    def test_open_failure_visible_and_release_attempted(self):
        capture = FakeCapture(opened=False)
        camera = Webcam(capture_factory=lambda index: capture)
        camera.start()
        self.addCleanup(camera.stop)
        wait_for(lambda: camera.snapshot()[0] == "unavailable")
        self.assertTrue(capture.released)
        self.assertIsNone(camera.snapshot()[2])

    def test_device_open_main_thread_but_reads_worker_thread(self):
        threads = {}
        class Capture(FakeCapture):
            def read(self):
                threads["read"] = threading.current_thread()
                return super().read()
        def factory(index):
            threads["open"] = threading.current_thread()
            return Capture()
        camera = Webcam(capture_factory=factory)
        self.addCleanup(camera.stop)
        camera.start()
        wait_for(lambda: camera.snapshot()[2] is not None)
        self.assertIs(threads["open"], threading.main_thread())
        self.assertIsNot(threads["read"], threading.main_thread())

    def test_background_start_rejected_without_opening_device(self):
        calls, errors = [], []
        camera = Webcam(capture_factory=lambda index: calls.append(index))
        def start():
            try:
                camera.start()
            except RuntimeError as error:
                errors.append(str(error))
        thread = threading.Thread(target=start)
        thread.start()
        thread.join(timeout=1)
        self.assertEqual(calls, [])
        self.assertEqual(len(errors), 1)

    def test_failed_reads_clear_availability(self):
        capture = FakeCapture(frames=False)
        camera = Webcam(capture_factory=lambda index: capture)
        camera.start()
        self.addCleanup(camera.stop)
        wait_for(lambda: camera.snapshot()[0] == "unavailable")
        camera.thread.join(timeout=1)
        self.assertTrue(capture.released)
        self.assertIsNone(camera.snapshot()[2])

    def test_release_failure_not_reported_as_released(self):
        capture = FakeCapture(release_error=True)
        camera = Webcam(capture_factory=lambda index: capture)
        camera.start()
        self.addCleanup(camera.stop)
        wait_for(lambda: camera.snapshot()[2] is not None)
        self.assertFalse(camera.stop())
        self.assertEqual(camera.snapshot()[0], "unavailable")

    def test_restart_never_reuses_previous_frame_identity(self):
        captures = []
        def factory(index):
            capture = FakeCapture()
            captures.append(capture)
            return capture
        camera = Webcam(capture_factory=factory)
        self.addCleanup(camera.stop)
        camera.start()
        wait_for(lambda: camera.snapshot()[2] is not None)
        previous = camera.snapshot()[2].sequence
        camera.stop()
        camera.start()
        wait_for(lambda: camera.snapshot()[2] is not None)
        self.assertGreater(camera.snapshot()[2].sequence, previous)
        self.assertEqual(len(captures), 2)

    def test_expired_paused_and_future_frames_hidden(self):
        frame = Frame(1, "fixture", 10.0, None)
        self.assertTrue(frame_is_fresh(frame, "monitoring", 10.2))
        self.assertFalse(frame_is_fresh(frame, "monitoring", 11.0))
        self.assertFalse(frame_is_fresh(frame, "paused", 10.2))
        self.assertFalse(frame_is_fresh(frame, "monitoring", 9.0))


if __name__ == "__main__":
    unittest.main()
