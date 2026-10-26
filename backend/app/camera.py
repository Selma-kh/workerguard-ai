"""Runs the camera -> detector -> rules -> renderer loop in a background thread.

Two sources, one at a time:
- "live": the laptop camera;
- "recorded": the first video found in backend/media/ (it loops).

The loop starts when the dashboard presses Start and stops on Stop. Switching source
while running restarts the loop on the new source but keeps the session's log.
The newest JPEG frame is kept in memory so /video can stream it to the browser.
"""

import threading
import time

import cv2

from . import config, renderer
from .detector import Detector
from .events import EventStore
from .rules import PersonStatus, RulesEngine


class Pipeline:
    def __init__(self) -> None:
        self._detector: Detector | None = None
        self._rules = RulesEngine()
        self.events = EventStore()
        self._thread: threading.Thread | None = None
        self._stop = threading.Event()
        self._lock = threading.Lock()
        self._jpeg: bytes | None = None
        self.source = "live"  # live | recorded
        self.status = "stopped"  # stopped | running | unavailable
        self.statuses: list[PersonStatus] = []

    # --- control -----------------------------------------------------------
    def start(self) -> None:
        """Start a new session: the log begins empty."""
        if self._thread and self._thread.is_alive():
            return
        self.events.clear()
        self._rules.new_session()  # worker numbers start again at 1
        self._launch()

    def stop(self) -> None:
        self._halt()
        self.status = "stopped"
        self.statuses = []
        with self._lock:
            self._jpeg = None

    def set_source(self, source: str) -> None:
        """Choose live or recorded. If running, continue the same session on the new source."""
        if source not in ("live", "recorded"):
            raise ValueError("source must be 'live' or 'recorded'")
        was_running = self._thread is not None and self._thread.is_alive()
        self.source = source
        if was_running:
            self._halt()
            self._launch()
        elif self.status == "unavailable":
            self.status = "stopped"  # clear an old failure message; Start will retry

    def latest_jpeg(self) -> bytes | None:
        with self._lock:
            return self._jpeg

    # --- internals ---------------------------------------------------------
    def _launch(self) -> None:
        self._stop.clear()
        self.status = "running"
        self._thread = threading.Thread(target=self._run, args=(self.source,), daemon=True)
        self._thread.start()

    def _halt(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=5)
        self._thread = None

    def _open(self, source: str):
        if source == "recorded":
            clip = config.find_clip()
            return cv2.VideoCapture(str(clip)) if clip else None
        return cv2.VideoCapture(config.CAMERA_SOURCE)

    def _run(self, source: str) -> None:
        capture = self._open(source)
        if capture is None or not capture.isOpened():
            self.status = "unavailable"
            return
        if self._detector is None:
            self._detector = Detector()
        self._detector.reset()
        self._rules.reset()
        is_file = source == "recorded" or isinstance(config.CAMERA_SOURCE, str)
        frame_time = 1 / (capture.get(cv2.CAP_PROP_FPS) or 25) if is_file else 0
        try:
            while not self._stop.is_set():
                started = time.time()
                ok, frame = capture.read()
                if not ok and is_file and not self._stop.is_set():
                    # end of the clip: start it again, with fresh IDs
                    if source == "recorded":
                        capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        self._detector.reset()
                        self._rules.reset()
                        ok, frame = capture.read()
                if not ok:
                    self.status = "unavailable"
                    return
                frame = renderer.resize(frame)
                people = self._detector.track_people(frame)
                items = self._detector.find_ppe(frame)
                statuses, incidents = self._rules.update(people, items, frame.shape)
                annotated = renderer.draw(frame, statuses)
                self.events.note_people(s.id for s in statuses)
                for incident in incidents:
                    # the snapshot is the annotated frame at the moment of the incident
                    self.events.add(incident.type, incident.person_id, annotated)
                self.statuses = statuses
                jpeg = renderer.to_jpeg(annotated)
                with self._lock:
                    self._jpeg = jpeg
                if is_file:  # play files at their own speed, not as fast as possible
                    time.sleep(max(0.0, frame_time - (time.time() - started)))
                else:
                    time.sleep(0.001)
        finally:
            capture.release()


pipeline = Pipeline()
