"""Finds people in a frame and gives each one an ID that stays the same over time."""

from dataclasses import dataclass

from ultralytics import YOLO

from . import config


@dataclass
class Person:
    id: int
    box: tuple[int, int, int, int]  # x1, y1, x2, y2 in pixels
    confidence: float


class Detector:
    def __init__(self) -> None:
        self.model = YOLO(str(config.PERSON_MODEL_PATH))

    def track(self, frame) -> list[Person]:
        """Run detection + tracking on one frame (persist=True keeps IDs between frames)."""
        results = self.model.track(
            frame,
            persist=True,
            classes=[config.PERSON_CLASS_ID],
            tracker=config.TRACKER,
            conf=config.CONFIDENCE,
            verbose=False,
        )
        boxes = results[0].boxes
        people: list[Person] = []
        if boxes is None or boxes.id is None:
            return people  # nobody tracked yet
        for xyxy, track_id, conf in zip(
            boxes.xyxy.tolist(), boxes.id.tolist(), boxes.conf.tolist()
        ):
            x1, y1, x2, y2 = (int(v) for v in xyxy)
            people.append(Person(int(track_id), (x1, y1, x2, y2), float(conf)))
        return people

    def reset(self) -> None:
        """Forget all tracked IDs (used when the source changes or restarts)."""
        predictor = self.model.predictor
        if predictor is not None and hasattr(predictor, "trackers"):
            for tracker in predictor.trackers:
                tracker.reset()
