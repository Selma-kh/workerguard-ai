"""Draws the boxes and labels on a frame and turns it into a JPEG for the browser."""

import cv2

from . import config
from .rules import PersonStatus, zone_pixels

# Colors are BGR (OpenCV order).
OK_COLOR = (200, 130, 30)  # deep blue: the person wears everything
WARN_COLOR = (11, 158, 245)  # yellow/orange: a helmet or vest is missing
DANGER_COLOR = (38, 38, 220)  # red: the person is inside the danger zone
TEXT_COLOR = (255, 255, 255)
WARN_TEXT_COLOR = (20, 20, 20)


def _label(frame, text: str, x: int, y: int, color, text_color) -> None:
    (w, h), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
    top = max(y - h - 10, 0)
    cv2.rectangle(frame, (x, top), (x + w + 10, top + h + 10), color, -1)
    cv2.putText(
        frame, text, (x + 5, top + h + 3), cv2.FONT_HERSHEY_SIMPLEX, 0.6, text_color, 2
    )


def draw_zone(frame, occupied: bool) -> None:
    """The fixed red danger zone: a see-through red area with a border and a name."""
    x1, y1, x2, y2 = zone_pixels(frame.shape)
    overlay = frame.copy()
    cv2.rectangle(overlay, (x1, y1), (x2, y2), DANGER_COLOR, -1)
    cv2.addWeighted(overlay, 0.35 if occupied else 0.2, frame, 0.65 if occupied else 0.8, 0, frame)
    cv2.rectangle(frame, (x1, y1), (x2, y2), DANGER_COLOR, 3 if occupied else 2)
    _label(frame, "DANGER ZONE", x1, y1 + 32, DANGER_COLOR, TEXT_COLOR)


def draw(frame, statuses: list[PersonStatus]):
    draw_zone(frame, occupied=any(s.in_zone for s in statuses))
    for status in statuses:
        x1, y1, x2, y2 = status.box
        missing = status.missing
        if status.in_zone:
            color, text_color = DANGER_COLOR, TEXT_COLOR
        elif missing:
            color, text_color = WARN_COLOR, WARN_TEXT_COLOR
        else:
            color, text_color = OK_COLOR, TEXT_COLOR
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        label = f"Worker {status.id}"
        if status.in_zone:
            label += " - IN DANGER ZONE"
        elif missing:
            label += " - no " + " / no ".join(missing)
        _label(frame, label, x1, y1, color, text_color)
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
