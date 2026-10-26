"""The incidents recorded during this session.

Events are kept in memory and a snapshot image of each one is saved in
backend/data/snapshots/. Both are emptied when a new session starts.
"""

import csv
import io
from dataclasses import asdict, dataclass
from datetime import datetime

import cv2

from . import config

ZONE_ENTRY = "zone_entry"
NO_HELMET = "no_helmet"
NO_VEST = "no_vest"

LABELS = {
    ZONE_ENTRY: "Entered danger zone",
    NO_HELMET: "Missing helmet",
    NO_VEST: "Missing vest",
}


@dataclass
class Event:
    id: int
    time: str  # HH:MM:SS
    type: str
    label: str
    person_id: int
    snapshot_file: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


class EventStore:
    def __init__(self) -> None:
        self._events: list[Event] = []
        self._seen_people: set[int] = set()
        config.SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)

    def clear(self) -> None:
        """Start a new session: forget all events and delete their snapshots."""
        self._events = []
        self._seen_people = set()
        config.SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
        for file in config.SNAPSHOT_DIR.glob("*.jpg"):
            file.unlink()

    def note_people(self, person_ids) -> None:
        """Remember who has been on camera this session (for the compliance figure)."""
        self._seen_people.update(person_ids)

    def add(self, event_type: str, person_id: int, snapshot_frame=None) -> Event:
        event = Event(
            id=len(self._events) + 1,
            time=datetime.now().strftime("%H:%M:%S"),
            type=event_type,
            label=LABELS[event_type],
            person_id=person_id,
        )
        if snapshot_frame is not None:
            name = f"event_{event.id:03d}_{event_type}.jpg"
            cv2.imwrite(
                str(config.SNAPSHOT_DIR / name),
                snapshot_frame,
                [int(cv2.IMWRITE_JPEG_QUALITY), 85],
            )
            event.snapshot_file = name
        self._events.append(event)
        return event

    @property
    def all(self) -> list[Event]:
        return list(self._events)

    def __len__(self) -> int:
        return len(self._events)

    def summary(self) -> dict:
        """Totals for this session. Compliance = share of people seen with no violation."""
        counts = {ZONE_ENTRY: 0, NO_HELMET: 0, NO_VEST: 0}
        for event in self._events:
            counts[event.type] += 1
        offenders = {e.person_id for e in self._events}
        seen = self._seen_people | offenders
        compliant = len(seen - offenders)
        return {
            "total": len(self._events),
            "no_helmet": counts[NO_HELMET],
            "no_vest": counts[NO_VEST],
            "zone_entry": counts[ZONE_ENTRY],
            "workers_seen": len(seen),
            "compliance_percent": round(100 * compliant / len(seen)) if seen else None,
        }

    def to_csv(self) -> str:
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(["time", "type", "description", "worker_id", "snapshot_file"])
        for e in self._events:
            writer.writerow([e.time, e.type, e.label, e.person_id, e.snapshot_file or ""])
        return buffer.getvalue()
