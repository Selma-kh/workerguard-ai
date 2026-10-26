"""Runs the camera -> detector -> rules -> renderer loop in a background thread.

The loop starts when the dashboard presses Start and stops on Stop. The newest
JPEG frame is kept in memory so /video can stream it to the browser.
"""

import threading
import time

import cv2

from . import config, renderer
from .detector import Detector
from .rules import PersonStatus, RulesEngine


class Pipeline:
    def __init__(self) -> None:
        self._detector: Detector | None = None
        self._rules = RulesEngine()
        self._thread: threading.Thread | None = None
        self._stop = threading.Event()
        self._lock = threading.Lock()
        self._jpeg: bytes | None = None
        self.status = "stopped"  # stopped | running | unavailable
        self.statuses: list[PersonStatus] = []

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
        self.statuses = []
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
        self._rules.reset()
        try:
            while not self._stop.is_set():
                ok, frame = capture.read()
                if not ok:
                    self.status = "unavailable"
                    return
                frame = renderer.resize(frame)
                people = self._detector.track_people(frame)
                items = self._detector.find_ppe(frame)
                statuses = self._rules.update(people, items)
                self.statuses = statuses
                jpeg = renderer.to_jpeg(renderer.draw(frame, statuses))
                with self._lock:
                    self._jpeg = jpeg
                time.sleep(0.001)  # let other threads breathe
        finally:
            capture.release()


pipeline = Pipeline()
