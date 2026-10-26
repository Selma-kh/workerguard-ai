"""The incidents recorded during this session (kept in memory, empty at every start)."""

from dataclasses import asdict, dataclass
from datetime import datetime

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

    def clear(self) -> None:
        self._events = []

    def add(self, event_type: str, person_id: int) -> Event:
        event = Event(
            id=len(self._events) + 1,
            time=datetime.now().strftime("%H:%M:%S"),
            type=event_type,
            label=LABELS[event_type],
            person_id=person_id,
        )
        self._events.append(event)
        return event

    @property
    def all(self) -> list[Event]:
        return list(self._events)

    def __len__(self) -> int:
        return len(self._events)
