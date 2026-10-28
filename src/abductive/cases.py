"""
Cases and mechanisms (ART-PLAN §8). A case is something with a history in
the discourse (a concept, an artist); its state each year is graded by the
table of forms. A mechanism says that a case in some state this year tends
to some outcome next year, for every case at once. It is judged
prequentially over all cases: each year's outcomes are predicted from the
years before, by counts (a Dirichlet(1) table), with the mechanism's
feature and without it; the gain is the log Bayes factor in nats.
"""
from __future__ import annotations

import math
import random
from collections import defaultdict
from dataclasses import dataclass, field, replace
from typing import Iterable

from .art_series import Claim

LEVELS = 3   # none, one, several (D25's negation, limitation, reality)


def level(n: int) -> int:
    return min(n, 2)


def doubling(n: int) -> int:
    """0, 1, 2, 3-4, 5-8, 9-16, 17+: size graded finely enough that a
    feature cannot stand in for it."""
    return 0 if n == 0 else min(6, (n - 1).bit_length() + 1)


@dataclass(frozen=True)
class Record:
    """One case in one year: its own past, its features and next year's outcome."""
    year: int
    own: tuple
    features: dict
    outcome: int


@dataclass
class Judgement:
    gain: float = 0.0
    cases: int = 0
    by_year: dict = field(default_factory=dict)


def _log_p(counts: list[int], y: int) -> float:
    return math.log((counts[y] + 1) / (sum(counts) + LEVELS))


def judge(records: Iterable[Record], feature: str) -> Judgement:
    """FEATURE added to each case's own past, against the own past alone. The
    first year is only learned; every later year is scored, then learned."""
    by_year: dict[int, list[Record]] = defaultdict(list)
    for r in records:
        by_year[r.year].append(r)
    own: dict = defaultdict(lambda: [0] * LEVELS)
    both: dict = defaultdict(lambda: [0] * LEVELS)
    out = Judgement()
    for i, year in enumerate(sorted(by_year)):
        rows = by_year[year]
        if i > 0:
            gain = sum(_log_p(both[(r.own, r.features[feature])], r.outcome) - _log_p(own[r.own], r.outcome)
                       for r in rows)
            out.gain += gain
            out.cases += len(rows)
            out.by_year[year] = gain / len(rows)
        for r in rows:
            own[r.own][r.outcome] += 1
            both[(r.own, r.features[feature])][r.outcome] += 1
    return out


def dealt(records: list[Record], feature: str, rng: random.Random) -> list[Record]:
    """The control: FEATURE's values dealt at random among the same year's
    cases, keeping how common each value is and breaking its tie to the case."""
    by_year: dict[int, list[int]] = defaultdict(list)
    for i, r in enumerate(records):
        by_year[r.year].append(i)
    out = list(records)
    for idx in by_year.values():
        values = [records[i].features[feature] for i in idx]
        rng.shuffle(values)
        for i, v in zip(idx, values):
            out[i] = replace(records[i], features={**records[i].features, feature: v})
    return out


DORMANT_MONTHS = 24   # as synthesis.DORMANT_MONTHS


def _months(month: str) -> int:
    y, m = map(int, month.split("-"))
    return y * 12 + m - 1


def _age(years: int) -> int:
    return 0 if years == 0 else 1 if years <= 3 else 2


def concept_years(claims: Iterable[Claim], founded: dict[int, str], last_year: int, fine: bool = False) -> list[Record]:
    """Each concept from its founding year while alive at the year's end (not
    DORMANT_MONTHS unasserted: known at the time), up to LAST_YEAR - 1, each
    record predicting the next year's writers. FINE grades the own past as
    this year's writers and the writers so far in doubling bins, with age."""
    cells: dict[tuple[int, int], dict] = {}
    asserted: dict[int, list[int]] = defaultdict(list)
    for c in claims:
        cell = cells.setdefault((c.concept, int(c.month[:4])),
                                {"writers": set(), "approval": 0, "disapproval": 0, "papers": set(), "modal": False})
        cell["writers"].add(c.writer)
        cell["papers"].add(c.paper)
        if c.force == "judges" and c.stance in ("approval", "disapproval"):
            cell[c.stance] += 1
        if c.force in ("predicts", "doubts"):
            cell["modal"] = True
        asserted[c.concept].append(_months(c.month))
    empty = {"writers": (), "approval": 0, "disapproval": 0, "papers": (), "modal": False}
    out = []
    for k, start in founded.items():
        months = sorted(asserted.get(k, ()))
        first = int(start[:4])
        so_far: set = set()
        for y in range(first, last_year):
            end = y * 12 + 11
            last = max([_months(start)] + [m for m in months if m <= end])
            if end - last >= DORMANT_MONTHS:
                break
            cell = cells.get((k, y), empty)
            so_far |= set(cell["writers"])
            sides = (cell["approval"] > 0) + (cell["disapproval"] > 0)
            out.append(Record(
                year=y,
                own=((doubling(len(cell["writers"])), doubling(len(so_far)), _age(y - first)) if fine
                     else (level(len(cell["writers"])), _age(y - first))),
                features={"contested": sides, "both_papers": int(len(cell["papers"]) > 1), "modality": int(cell["modal"])},
                outcome=level(len(cells.get((k, y + 1), empty)["writers"])),
            ))
    return out
