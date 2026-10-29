"""Trends shown in POE (ART-PLAN §11): this year's new, growing, fading and
argued-over trends. Years end in September (cases.year_to_september), so
the open year is a whole one. Describes the present; forecasts nothing."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Iterable, Mapping

from .art_series import Claim
from .cases import year_to_september

LEAST_WRITERS = 12       # the breadth floor (36 writers over three years) for one year
NEW_FROM = 2021
GROWING = 1.5
FADING = 0.5
BEFORE = 3               # years compared with this one
LEAST_VERDICTS = 10
FITS = 0.5               # share of this year's sampled claims about the trend's name
LISTS = ("new", "growing", "fading", "argued")


@dataclass
class Cell:
    writers: set = field(default_factory=set)
    papers: set = field(default_factory=set)
    approval: int = 0
    disapproval: int = 0


@dataclass(frozen=True)
class YearStats:
    cells: Mapping[tuple[int, int], Cell]     # (trend, year to September)
    writers: Mapping[int, set]                # every writer each year

    def share(self, trend: int, year: int) -> float:
        cell = self.cells.get((trend, year))
        return len(cell.writers) / len(self.writers[year]) if cell else 0.0

    def n(self, trend: int, year: int) -> int:
        cell = self.cells.get((trend, year))
        return len(cell.writers) if cell else 0


def year_stats(claims: Iterable[Claim]) -> YearStats:
    cells: dict = defaultdict(Cell)
    writers: dict = defaultdict(set)
    for c in claims:
        y = 2000 + year_to_september(c.month)
        cell = cells[(c.concept, y)]
        cell.writers.add(c.writer)
        cell.papers.add(c.paper)
        writers[y].add(c.writer)
        if c.force == "judges" and c.stance == "approval":
            cell.approval += 1
        elif c.force == "judges" and c.stance == "disapproval":
            cell.disapproval += 1
    return YearStats(dict(cells), dict(writers))


def candidates(stats: YearStats, start: Mapping[int, int], now: int) -> dict[str, list[int]]:
    """Each list's trends in order, before names are judged. START is each
    trend's first broad year."""
    before = range(now - BEFORE, now)
    broad = [t for t in start if stats.n(t, now) >= LEAST_WRITERS]

    def growth(t):
        past = sum(stats.share(t, y) for y in before) / BEFORE
        return stats.share(t, now) / past if past else float("inf")

    def best(t):
        return max(before, key=lambda y: stats.share(t, y))

    def verdicts(t):
        cell = stats.cells.get((t, now))
        return (cell.approval + cell.disapproval) if cell else 0

    def minority(t):
        cell = stats.cells[(t, now)]
        return min(cell.approval, cell.disapproval) / verdicts(t)

    fading = [t for t in start
              if stats.n(t, best(t)) >= LEAST_WRITERS and stats.share(t, now) <= FADING * stats.share(t, best(t))]
    argued = [t for t in broad if verdicts(t) >= LEAST_VERDICTS]
    return {
        "new": sorted((t for t in broad if start[t] >= NEW_FROM), key=lambda t: -stats.n(t, now)),
        "growing": sorted((t for t in broad if growth(t) >= GROWING), key=lambda t: -growth(t)),
        "fading": sorted(fading, key=lambda t: -stats.share(t, best(t))),
        "argued": sorted(argued, key=lambda t: -minority(t)),
    }


def shown(lists: Mapping[str, list[int]], kinds: Mapping[int, str], fit: Mapping[int, float],
          names: Mapping[int, str], broad: set[int]) -> dict[str, list[int]]:
    """Themes whose name fits at least FITS of this year's sampled claims
    (ART-PLAN §11, deviation 2), each name once a list; a fading trend
    whose name a BROAD trend (12+ writers this year) shares has carried on
    under another number and is left out (deviation 4). A candidate without
    a judged name, or a theme never checked, is an error: name and check
    every candidate first."""
    def missing(keys) -> None:
        if keys:
            raise KeyError(f"trends not yet judged: {keys[:10]}{'...' if len(keys) > 10 else ''}")
    every = {t for ts in lists.values() for t in ts}
    missing(sorted(every - set(kinds)))
    themes = {t for t in every if kinds[t] == "theme"}
    missing(sorted(themes - set(fit)))
    alive = {names[t] for t in broad if t in names}
    out = {}
    for k, ts in lists.items():
        seen: set = set()
        out[k] = []
        for t in ts:
            if t not in themes or fit[t] < FITS or names[t] in seen:
                continue
            if k == "fading" and names[t] in alive and t not in broad:
                continue
            seen.add(names[t])
            out[k].append(t)
    return out
