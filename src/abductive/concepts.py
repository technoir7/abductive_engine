"""
Defined concepts, under the fixed table of forms (DESIGN §4; EPISTEMOLOGY
§§4–5).

A defined concept is a rule assigning each week a state. It is formed by
combining choices that the table allows, and nothing else can be expressed:
- quantity: one series (unity), several taken together (plurality), or all
  of the domain's (totality);
- a schema of reproduction, how the past is held: the change over k weeks,
  the level against its trailing n weeks (a z-score), or the plain level;
- a window k or n, from a fixed set (judgment settles which, by practice);
- quality: two or three ordered degrees, separated by cut points.

Several series are taken together only as z-scores, the mean of each
one's standing against its own past: their raw changes are in unlike units
and cannot be added. A week whose state cannot be determined (too little
history, or a series not yet known) has none.

Every concept keeps its pedigree: the form it was built under and what
occasioned it.
"""
from __future__ import annotations

import math
import statistics
from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Optional, Sequence

from .weeks import Change, Week

WINDOWS = (4, 13, 26, 52)


class Reproduction(Enum):
    CHANGE = "change"
    ZSCORE = "z-score"
    LEVEL = "level"


class Quantity(Enum):
    UNITY = "unity"
    PLURALITY = "plurality"
    TOTALITY = "totality"


@dataclass(frozen=True)
class Form:
    series: tuple[str, ...]
    reproduction: Reproduction
    window: Optional[int]
    cuts: tuple[float, ...]

    def __post_init__(self) -> None:
        if not self.series or len(set(self.series)) != len(self.series):
            raise ValueError(f"a concept needs distinct series: {self.series}")
        if self.reproduction is Reproduction.LEVEL:
            if self.window is not None:
                raise ValueError("a plain level is held over no window")
        elif self.window not in WINDOWS:
            raise ValueError(f"window {self.window} is not in the table {WINDOWS}")
        if not 1 <= len(self.cuts) <= 2 or list(self.cuts) != sorted(set(self.cuts)):
            raise ValueError(f"two or three ordered degrees need one or two rising cut points: {self.cuts}")
        if len(self.series) > 1 and self.reproduction is not Reproduction.ZSCORE:
            raise ValueError("several series are taken together only as z-scores")

    @property
    def quantity(self) -> Quantity:
        return Quantity.UNITY if len(self.series) == 1 else Quantity.PLURALITY

    def quantity_in(self, domain: Mapping[str, Change]) -> Quantity:
        if len(self.series) > 1 and set(self.series) == set(domain):
            return Quantity.TOTALITY
        return self.quantity

    def describe(self) -> str:
        held = {Reproduction.CHANGE: f"change over {self.window} weeks",
                Reproduction.ZSCORE: f"z-score over {self.window} weeks",
                Reproduction.LEVEL: "level"}[self.reproduction]
        cuts = " and ".join(f"{c:g}" for c in self.cuts)
        return f"{' + '.join(self.series)}, {held}, cut at {cuts}"


@dataclass(frozen=True)
class Concept:
    form: Form
    occasion: str   # the anomaly or principle that occasioned it (DESIGN §7)

    def pedigree(self) -> str:
        return f"{self.form.describe()} ({self.occasion})"


def states(concept: Concept, weeks: Sequence[Week], kinds: Mapping[str, Change]) -> list[Optional[int]]:
    """The concept's state in each week: the number of cut points its value
    exceeds, or None where the value cannot be determined."""
    form = concept.form
    out: list[Optional[int]] = []
    for i in range(len(weeks)):
        values = [_reproduced(form, s, weeks, i, kinds[s]) for s in form.series]
        if any(v is None for v in values):
            out.append(None)
            continue
        value = sum(values) / len(values)
        out.append(sum(value > c for c in form.cuts))
    return out


def _reproduced(form: Form, series: str, weeks: Sequence[Week], i: int, kind: Change) -> Optional[float]:
    now = weeks[i].levels.get(series)
    if now is None:
        return None
    if form.reproduction is Reproduction.LEVEL:
        return now
    k = form.window
    if i < k:
        return None
    if form.reproduction is Reproduction.CHANGE:
        then = weeks[i - k].levels.get(series)
        return None if then is None else kind.between(then, now)
    past = [w.levels.get(series) for w in weeks[i - k:i]]
    if any(p is None for p in past):
        return None
    sd = statistics.stdev(past)
    if sd == 0 or not math.isfinite(sd):
        return None   # a series that did not move in the window has no standing against it
    return (now - statistics.fmean(past)) / sd
