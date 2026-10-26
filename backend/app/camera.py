"""Runs the camera -> detector -> renderer loop in a background thread.

The loop starts when the dashboard presses Start and stops on Stop. The newest
JPEG frame is kept in memory so /video can stream it to the browser.
"""

import threading
import time

import cv2

from . import config, renderer
from .detector import Detector


class Pipeline:
    def __init__(self) -> None:
        self._detector: Detector | None = None
        self._thread: threading.Thread | None = None
        self._stop = threading.Event()
        self._lock = threading.Lock()
        self._jpeg: bytes | None = None
        self.status = "stopped"  # stopped | running | unavailable
        self.people_count = 0

    # --- control -----------------------------------------------------------
    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self.status = "running"
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=3)
        self._thread = None
        self.status = "stopped"
        self.people_count = 0
        with self._lock:
            self._jpeg = None

    def latest_jpeg(self) -> bytes | None:
        with self._lock:
            return self._jpeg

    # --- worker thread -----------------------------------------------------
    def _run(self) -> None:
        capture = cv2.VideoCapture(config.CAMERA_SOURCE)
        if not capture.isOpened():
            self.status = "unavailable"
            return
        if self._detector is None:
            self._detector = Detector()
        self._detector.reset()
        try:
            while not self._stop.is_set():
                ok, frame = capture.read()
                if not ok:
                    self.status = "unavailable"
                    return
                frame = renderer.resize(frame)
                people = self._detector.track(frame)
                self.people_count = len(people)
                jpeg = renderer.to_jpeg(renderer.draw(frame, people))
                with self._lock:
                    self._jpeg = jpeg
                time.sleep(0.001)  # let other threads breathe
        finally:
            capture.release()


pipeline = Pipeline()
