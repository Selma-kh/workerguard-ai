"""Draws the boxes and IDs on a frame and turns it into a JPEG for the browser."""

import cv2

from . import config
from .detector import Person

# Colors are BGR (OpenCV order). Blue accent from the app's look and feel.
BOX_COLOR = (200, 130, 30)
TEXT_COLOR = (255, 255, 255)


def draw(frame, people: list[Person]):
    for person in people:
        x1, y1, x2, y2 = person.box
        cv2.rectangle(frame, (x1, y1), (x2, y2), BOX_COLOR, 2)
        label = f"Worker {person.id}"
        (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
        top = max(y1 - h - 10, 0)
        cv2.rectangle(frame, (x1, top), (x1 + w + 10, top + h + 10), BOX_COLOR, -1)
        cv2.putText(
            frame, label, (x1 + 5, top + h + 3),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, TEXT_COLOR, 2,
        )
    return frame


def resize(frame):
    height, width = frame.shape[:2]
    if width <= config.STREAM_WIDTH:
        return frame
    scale = config.STREAM_WIDTH / width
    return cv2.resize(frame, (config.STREAM_WIDTH, int(height * scale)))


def to_jpeg(frame) -> bytes:
    ok, buffer = cv2.imencode(
        ".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), config.JPEG_QUALITY]
    )
    if not ok:
        raise RuntimeError("Could not encode frame as JPEG")
    return buffer.tobytes()
