"""Explicit webcam lifecycle with one replaceable frame, never a frame queue."""
from dataclasses import dataclass
from datetime import datetime, timezone
import threading
import time

import cv2


@dataclass(frozen=True)
class Frame:
    sequence: int
    captured_at: str
    captured_monotonic: float
    pixels: object
    source: str = "laptop_webcam"


def frame_is_fresh(frame, state, now, maximum_age=0.8):
    return (state == "monitoring" and frame is not None and
            0 <= now - frame.captured_monotonic <= maximum_age)


class Webcam:
    def __init__(self, index=0, capture_factory=None):
        self.index = index
        self.factory = capture_factory or (lambda index: cv2.VideoCapture(index, cv2.CAP_AVFOUNDATION))
        self.lock = threading.Lock()
        self.stop_requested = threading.Event()
        self.thread = None
        self.frame = None
        self.state = "paused"
        self.message = "Camera is off. Press S to start."
        self.frames_captured = 0
        self.sequence = 0
        self.release_completed = True

    def start(self):
        # AVFoundation's first TCC permission request must spin the main run loop.
        # Only opening/configuring the device is synchronous; reads stay in a worker.
        if threading.current_thread() is not threading.main_thread():
            raise RuntimeError("Start webcam on the main UI thread for macOS camera permission.")
        with self.lock:
            if self.state == "starting" or (self.thread and self.thread.is_alive()) or not self.release_completed:
                return False
            self.stop_requested.clear()
            self.release_completed = True
            self.frame = None
            self.state = "starting"
            self.message = "Opening camera; allow the macOS camera prompt."
        camera = None
        try:
            camera = self.factory(self.index)
            with self.lock:
                self.release_completed = False
            if not camera.isOpened():
                raise RuntimeError("Cannot open camera. Check Camera permission and other camera apps.")
            camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            camera.set(cv2.CAP_PROP_FPS, 15)
            with self.lock:
                self.thread = threading.Thread(target=self._capture, args=(camera,), daemon=True)
                self.thread.start()
            return True
        except Exception as error:
            with self.lock:
                self.state = "unavailable"
                self.message = str(error)
                self.frame = None
            if camera is not None:
                self._release(camera)
            return False

    def snapshot(self):
        with self.lock:
            return self.state, self.message, self.frame

    def stop(self):
        self.stop_requested.set()
        with self.lock:
            self.frame = None
            self.state = "stopping"
            self.message = "Releasing camera..."
            thread = self.thread
        if thread:
            thread.join(timeout=2)
        with self.lock:
            if thread and thread.is_alive():
                self.state = "unavailable"
                self.message = "Camera release pending. Quit if it does not finish."
                return False
            if not self.release_completed:
                self.state = "unavailable"
                self.message = "Camera release failed; quit and check the camera indicator."
                return False
            self.state = "paused"
            self.message = "Camera released. Press S to restart."
            return True

    def _release(self, camera):
        try:
            camera.release()
            with self.lock:
                self.release_completed = True
        except Exception as error:
            with self.lock:
                self.state = "unavailable"
                self.message = "Camera release failed: " + str(error)
                self.frame = None

    def _capture(self, camera):
        try:
            failures = 0
            while not self.stop_requested.is_set():
                began = time.monotonic()
                success, pixels = camera.read()
                if not success or pixels is None:
                    failures += 1
                    if failures >= 4:
                        raise RuntimeError("Camera stopped returning frames; monitoring unavailable.")
                    self.stop_requested.wait(0.05)
                    continue
                failures = 0
                with self.lock:
                    if self.stop_requested.is_set():
                        break
                    self.sequence += 1
                    self.frames_captured += 1
                    self.frame = Frame(self.sequence, datetime.now(timezone.utc).isoformat(),
                                       time.monotonic(), pixels)
                    self.state = "monitoring"
                    self.message = "Real laptop webcam. Person detection only."
                self.stop_requested.wait(max(0, 1 / 15 - (time.monotonic() - began)))
        except Exception as error:
            with self.lock:
                self.state = "unavailable"
                self.message = str(error)
                self.frame = None
        finally:
            self._release(camera)
            if self.stop_requested.is_set() and self.release_completed:
                with self.lock:
                    self.state = "paused"
                    self.message = "Camera released. Press S to restart."
                    self.frame = None
