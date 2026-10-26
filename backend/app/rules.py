"""Decides, for each tracked person, whether they wear a helmet and a vest.

Each person (by ID) keeps a short history of what was seen on them in recent frames,
so a single missed detection does not make their status flicker.
"""

from collections import deque
from dataclasses import dataclass, field

from . import config
from .detector import Person, PPEItem


@dataclass
class PersonStatus:
    id: int
    box: tuple[int, int, int, int]
    has_helmet: bool
    has_vest: bool

    @property
    def missing(self) -> list[str]:
        missing = []
        if not self.has_helmet:
            missing.append("helmet")
        if not self.has_vest:
            missing.append("vest")
        return missing


@dataclass
class _History:
    helmet: deque = field(default_factory=lambda: deque(maxlen=config.PPE_HISTORY_FRAMES))
    vest: deque = field(default_factory=lambda: deque(maxlen=config.PPE_HISTORY_FRAMES))


def _item_belongs_to(person_box, item_box, vertical_zone: tuple[float, float]) -> bool:
    """True if the item's centre lies inside the person's box, in the given vertical band."""
    px1, py1, px2, py2 = person_box
    cx = (item_box[0] + item_box[2]) / 2
    cy = (item_box[1] + item_box[3]) / 2
    height = py2 - py1
    top = py1 + vertical_zone[0] * height
    bottom = py1 + vertical_zone[1] * height
    return px1 <= cx <= px2 and top <= cy <= bottom


class RulesEngine:
    def __init__(self) -> None:
        self._histories: dict[int, _History] = {}

    def reset(self) -> None:
        self._histories.clear()

    def update(self, people: list[Person], items: list[PPEItem]) -> list[PersonStatus]:
        statuses: list[PersonStatus] = []
        for person in people:
            history = self._histories.setdefault(person.id, _History())
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
            statuses.append(
                PersonStatus(
                    id=person.id,
                    box=person.box,
                    has_helmet=self._worn(history.helmet),
                    has_vest=self._worn(history.vest),
                )
            )
        return statuses

    @staticmethod
    def _worn(seen: deque) -> bool:
        # Until the person has been watched long enough, give them the benefit of the doubt.
        if len(seen) < config.PPE_MIN_FRAMES_SEEN:
            return True
        return sum(seen) / len(seen) >= config.PPE_SEEN_FRACTION
