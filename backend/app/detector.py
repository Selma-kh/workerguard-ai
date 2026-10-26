"""Finds people (with stable IDs) and PPE items (helmet, vest) in a frame."""

from dataclasses import dataclass

from ultralytics import YOLO

from . import config


@dataclass
class Person:
    id: int
    box: tuple[int, int, int, int]  # x1, y1, x2, y2 in pixels
    confidence: float


@dataclass
class PPEItem:
    kind: str  # "helmet" or "vest"
    box: tuple[int, int, int, int]
    confidence: float


class Detector:
    def __init__(self) -> None:
        self.person_model = YOLO(str(config.PERSON_MODEL_PATH))
        self.ppe_model = YOLO(str(config.PPE_MODEL_PATH))

    def track_people(self, frame) -> list[Person]:
        """Detect people and give each an ID that persists between frames."""
        results = self.person_model.track(
            frame,
            persist=True,
            classes=[config.PERSON_CLASS_ID],
            tracker=config.TRACKER,
            conf=config.CONFIDENCE,
            device=config.DEVICE,
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

    def find_ppe(self, frame) -> list[PPEItem]:
        """Detect helmets and hi-vis vests anywhere in the frame."""
        result = self.ppe_model.predict(
            frame, conf=config.PPE_CONFIDENCE, device=config.DEVICE, verbose=False
        )[0]
        items: list[PPEItem] = []
        for xyxy, cls, conf in zip(
            result.boxes.xyxy.tolist(), result.boxes.cls.tolist(), result.boxes.conf.tolist()
        ):
            kind = config.PPE_CLASS_NAMES.get(self.ppe_model.names[int(cls)])
            if kind is None:
                continue  # ignore the model's other classes (human, no-helmet)
            x1, y1, x2, y2 = (int(v) for v in xyxy)
            items.append(PPEItem(kind, (x1, y1, x2, y2), float(conf)))
        return items

    def reset(self) -> None:
        """Forget all tracked IDs (used when the source changes or restarts)."""
        predictor = self.person_model.predictor
        if predictor is not None and hasattr(predictor, "trackers"):
            for tracker in predictor.trackers:
                tracker.reset()
