"""The safety rules: who wears what, who is in the danger zone, and which incidents are new.

Each person (by ID) keeps a short history, so one missed detection does not make their
status flicker, and a person who is briefly lost and found again is not counted twice.

Counting rules (see prd.md > Counting rules):
- a zone violation is created when a person ENTERS the zone (outside -> inside);
- a missing-PPE violation is created once per person per missing item, and can only be
  created again after that person has been seen wearing the item;
- two people in the zone give two violations, one per person.
"""

import time
from collections import deque
from dataclasses import dataclass, field

from . import config
from .detector import Person, PPEItem
from .events import NO_HELMET, NO_VEST, ZONE_ENTRY


@dataclass
class PersonStatus:
    id: int
    box: tuple[int, int, int, int]
    has_helmet: bool
    has_vest: bool
    in_zone: bool

    @property
    def missing(self) -> list[str]:
        missing = []
        if not self.has_helmet:
            missing.append("helmet")
        if not self.has_vest:
            missing.append("vest")
        return missing


@dataclass
class NewIncident:
    type: str
    person_id: int


@dataclass
class _History:
    helmet: deque = field(default_factory=lambda: deque(maxlen=config.PPE_HISTORY_FRAMES))
    vest: deque = field(default_factory=lambda: deque(maxlen=config.PPE_HISTORY_FRAMES))
    in_zone: bool = False  # confirmed state (after a few frames, so the edge does not flicker)
    zone_streak: int = 0  # consecutive frames that disagree with the confirmed state
    violating: dict = field(default_factory=lambda: {"helmet": False, "vest": False})
    worn_streak: dict = field(default_factory=lambda: {"helmet": 0, "vest": 0})
    last_seen: float = 0.0


def _item_belongs_to(person_box, item_box, vertical_zone: tuple[float, float]) -> bool:
    """True if the item's centre lies inside the person's box, in the given vertical band."""
    px1, py1, px2, py2 = person_box
    cx = (item_box[0] + item_box[2]) / 2
    cy = (item_box[1] + item_box[3]) / 2
    height = py2 - py1
    top = py1 + vertical_zone[0] * height
    bottom = py1 + vertical_zone[1] * height
    return px1 <= cx <= px2 and top <= cy <= bottom


def zone_pixels(frame_shape) -> tuple[int, int, int, int]:
    """The danger zone rectangle in pixels for a frame of the given (height, width, ...)."""
    height, width = frame_shape[:2]
    zx1, zy1, zx2, zy2 = config.DANGER_ZONE
    return int(zx1 * width), int(zy1 * height), int(zx2 * width), int(zy2 * height)


class RulesEngine:
    def __init__(self) -> None:
        self._histories: dict[int, _History] = {}

    def reset(self) -> None:
        self._histories.clear()

    def update(
        self, people: list[Person], items: list[PPEItem], frame_shape
    ) -> tuple[list[PersonStatus], list[NewIncident]]:
        now = time.time()
        zone = zone_pixels(frame_shape)
        statuses: list[PersonStatus] = []
        incidents: list[NewIncident] = []

        for person in people:
            history = self._histories.setdefault(person.id, _History())
            history.last_seen = now
            history.helmet.append(
                any(
                    i.kind == "helmet"
                    and _item_belongs_to(person.box, i.box, config.HELMET_ZONE)
                    for i in items
                )
            )
            history.vest.append(
                any(
                    i.kind == "vest"
                    and _item_belongs_to(person.box, i.box, config.VEST_ZONE)
                    for i in items
                )
            )
            has_helmet = self._worn(history.helmet)
            has_vest = self._worn(history.vest)

            # Zone: the person's feet (bottom-centre of the box) must be inside the rectangle.
            fx = (person.box[0] + person.box[2]) / 2
            fy = person.box[3]
            inside_now = zone[0] <= fx <= zone[2] and zone[1] <= fy <= zone[3]
            if inside_now == history.in_zone:
                history.zone_streak = 0
            else:
                history.zone_streak += 1
                needed = (
                    config.ZONE_ENTER_FRAMES if inside_now else config.ZONE_EXIT_FRAMES
                )
                if history.zone_streak >= needed:
                    history.in_zone = inside_now
                    history.zone_streak = 0
                    if inside_now:
                        incidents.append(NewIncident(ZONE_ENTRY, person.id))

            # PPE: one incident per person per missing item, until it is seen worn again.
            # The person must then be seen wearing it for a sustained time before a new
            # incident is possible, so a wrongly detected "vest" for a moment cannot
            # reset the rule and create a duplicate.
            for item_name, worn, incident_type in (
                ("helmet", has_helmet, NO_HELMET),
                ("vest", has_vest, NO_VEST),
            ):
                if not worn:
                    history.worn_streak[item_name] = 0
                    if not history.violating[item_name]:
                        history.violating[item_name] = True
                        incidents.append(NewIncident(incident_type, person.id))
                else:
                    history.worn_streak[item_name] += 1
                    if history.worn_streak[item_name] >= config.PPE_REARM_FRAMES:
                        history.violating[item_name] = False

            statuses.append(
                PersonStatus(
                    id=person.id,
                    box=person.box,
                    has_helmet=has_helmet,
                    has_vest=has_vest,
                    in_zone=history.in_zone,
                )
            )

        # Forget people who have not been seen for a while.
        for person_id in [
            pid
            for pid, h in self._histories.items()
            if now - h.last_seen > config.FORGET_AFTER_SECONDS
        ]:
            del self._histories[person_id]

        return statuses, incidents

    @staticmethod
    def _worn(seen: deque) -> bool:
        # Until the person has been watched long enough, give them the benefit of the doubt.
        if len(seen) < config.PPE_MIN_FRAMES_SEEN:
            return True
        return sum(seen) / len(seen) >= config.PPE_SEEN_FRACTION
