"""The safety rules: who wears what, who is in the danger zone, and which incidents are new.

Each person keeps a short history, so one missed detection does not make their
status flicker, and a person who is briefly lost and found again is not counted twice.

The tracker sometimes gives the same person a new ID (for example when the box suddenly
changes size). Three safeguards sit on top of it:
- a person only counts after CONFIRM_FRAMES frames, so brief ghost detections are ignored;
- a newly confirmed person who appears close to someone lost a moment ago takes over that
  person's number, with their history, instead of becoming a "new worker";
- the numbers shown ("Worker 1", "Worker 2"...) are our own and start at 1.

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
        self._histories: dict[int, _History] = {}  # keyed by our own worker number
        self._frames_seen: dict[int, int] = {}  # tracker ID -> frames seen
        self._number_of: dict[int, int] = {}  # tracker ID -> worker number
        self._last_box: dict[int, tuple] = {}  # worker number -> last box
        self._next_number = 1

    def reset(self) -> None:
        """Forget current people (e.g. when the source changes). Numbers keep counting."""
        self._histories.clear()
        self._frames_seen.clear()
        self._number_of.clear()
        self._last_box.clear()

    def new_session(self) -> None:
        self.reset()
        self._next_number = 1

    def _assign_number(self, person: Person, present_numbers: set[int], now: float) -> int:
        """Give a newly confirmed person a number: take over a nearby lost person's, or a new one."""
        px1, py1, px2, py2 = person.box
        pcx, pcy = (px1 + px2) / 2, (py1 + py2) / 2
        size = max(px2 - px1, py2 - py1)
        best, best_distance = None, None
        for number, history in self._histories.items():
            if number in present_numbers or now - history.last_seen > config.ADOPT_SECONDS:
                continue
            bx1, by1, bx2, by2 = self._last_box[number]
            distance = ((pcx - (bx1 + bx2) / 2) ** 2 + (pcy - (by1 + by2) / 2) ** 2) ** 0.5
            limit = config.ADOPT_DISTANCE * max(size, bx2 - bx1, by2 - by1)
            if distance <= limit and (best_distance is None or distance < best_distance):
                best, best_distance = number, distance
        if best is not None:
            return best
        number = self._next_number
        self._next_number += 1
        return number

    def update(
        self, people: list[Person], items: list[PPEItem], frame_shape
    ) -> tuple[list[PersonStatus], list[NewIncident]]:
        now = time.time()
        zone = zone_pixels(frame_shape)
        statuses: list[PersonStatus] = []
        incidents: list[NewIncident] = []

        # Who is on screen with a number already, so nobody takes over their number.
        present_numbers = {
            self._number_of[p.id] for p in people if p.id in self._number_of
        }

        for person in people:
            self._frames_seen[person.id] = self._frames_seen.get(person.id, 0) + 1
            if person.id not in self._number_of:
                if self._frames_seen[person.id] < config.CONFIRM_FRAMES:
                    continue  # not confirmed yet: ignore (could be a ghost detection)
                number = self._assign_number(person, present_numbers, now)
                self._number_of[person.id] = number
                present_numbers.add(number)
            number = self._number_of[person.id]
            self._last_box[number] = person.box

            history = self._histories.setdefault(number, _History())
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
                        incidents.append(NewIncident(ZONE_ENTRY, number))

            # PPE: one incident per person per missing item.
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
                        incidents.append(NewIncident(incident_type, number))
                else:
                    history.worn_streak[item_name] += 1
                    if history.worn_streak[item_name] >= config.PPE_REARM_FRAMES:
                        history.violating[item_name] = False

            statuses.append(
                PersonStatus(
                    id=number,
                    box=person.box,
                    has_helmet=has_helmet,
                    has_vest=has_vest,
                    in_zone=history.in_zone,
                )
            )

        # Forget people who have not been seen for a while.
        for number in [
            n
            for n, h in self._histories.items()
            if now - h.last_seen > config.FORGET_AFTER_SECONDS
        ]:
            del self._histories[number]
            self._last_box.pop(number, None)

        return statuses, incidents

    @staticmethod
    def _worn(seen: deque) -> bool:
        # Until the person has been watched long enough, give them the benefit of the doubt.
        if len(seen) < config.PPE_MIN_FRAMES_SEEN:
            return True
        return sum(seen) / len(seen) >= config.PPE_SEEN_FRACTION
