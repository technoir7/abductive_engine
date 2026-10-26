"""
The weekly observations each scheme predicts and is scored on (DESIGN §3).

Each Friday the engine apprehends what became public since the last one.
For each series that published a new value, the observation is its change
since its previous value: the latest value now against the value that was
latest a week ago, both as known now, so a revision made this week counts
on both sides. A series with nothing new is not observed that week, so
monthly CPI is observed monthly.

The language of observation is chosen by us, on purpose, so that rival
schemes have common ground to be compared on (EPISTEMOLOGY.md §3).
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Mapping, Sequence

from .observations import Row


class Change(Enum):
    LOG = "log"                 # positive series: prices, indexes, balances
    DIFFERENCE = "difference"   # rates and spreads, which can cross zero

    def between(self, before: float, after: float) -> float:
        return math.log(after) - math.log(before) if self is Change.LOG else after - before


@dataclass(frozen=True)
class Week:
    friday: date
    changes: dict[str, float]   # only the series that published something new


def weeks(rows: Sequence[Row], fridays: Sequence[date], series: Mapping[str, Change]) -> list[Week]:
    """One Week per Friday, in order. Sweeps the rows once in order of
    publication rather than asking 'as of' each Friday afresh."""
    pending = sorted((r for r in rows if r.series in series), key=lambda r: r.public)
    known: dict[str, dict[date, float]] = {s: {} for s in series}
    latest: dict[str, date] = {}
    latest_before: dict[str, date] = {}
    out, i = [], 0
    for friday in fridays:
        while i < len(pending) and pending[i].public <= friday:
            r = pending[i]
            known[r.series][r.measured] = r.value
            latest[r.series] = max(latest.get(r.series, r.measured), r.measured)
            i += 1
        changes = {}
        for s, change in series.items():
            if s not in latest:
                continue
            before = latest_before.get(s)
            if before is not None and latest[s] != before:
                changes[s] = change.between(known[s][before], known[s][latest[s]])
            latest_before[s] = latest[s]
        out.append(Week(friday, changes))
    return out
