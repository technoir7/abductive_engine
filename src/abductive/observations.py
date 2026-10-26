"""
Observations, as POE serves them (DESIGN §2): a series, the date a value
measures, the value, and the date it became public. A revised value has one
row per published version.

The one query is everything public as of a date, where the newest version
public by then is the one that counts. That is what keeps a replay honest:
no week sees a number before it was published, or a revision before it was
made.
"""
from __future__ import annotations

import csv
from datetime import date
from pathlib import Path
from typing import Iterable, NamedTuple


class Row(NamedTuple):
    series: str
    measured: date
    value: float
    public: date


def read_csv(path: Path) -> list[Row]:
    """POE's export (`evals.observations`)."""
    with Path(path).open() as f:
        return [Row(r["series"], date.fromisoformat(r["measured"]), float(r["value"]),
                    date.fromisoformat(r["public"])) for r in csv.DictReader(f)]


def as_of(rows: Iterable[Row], day: date) -> dict[str, list[tuple[date, float]]]:
    """Each series as known on DAY: (measured, value), oldest first."""
    known: dict[str, dict[date, tuple[date, float]]] = {}
    for r in rows:
        if r.public > day:
            continue
        seen = known.setdefault(r.series, {}).get(r.measured)
        if seen is None or r.public >= seen[0]:
            known[r.series][r.measured] = (r.public, r.value)
    return {s: [(m, v) for m, (_, v) in sorted(by.items())] for s, by in known.items()}
