"""
The engine on cases (ART-PLAN §9). Every set of mechanisms from a small
pool is a rival scheme; each predicts every case's outcome from its own
past and its mechanisms (cases.py's backoff tables), before the year is
seen. Evidence between schemes is their decayed difference in score; the
leader changes only when a rival is ahead by SHIFT_NATS, and each change
is recorded as a shift in what drives the cases.
"""
from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import dataclass
from itertools import combinations

from .cases import LEVELS, Record, _key, _log_p_backoff

HALF_LIFE_YEARS = 5
SHIFT_NATS = 3.0          # Jeffreys' "strong"


class CaseScheme:
    def __init__(self, features: tuple[str, ...]):
        self.features = features
        self._own: dict = defaultdict(lambda: [0] * LEVELS)
        self._cells: dict = defaultdict(lambda: [0] * LEVELS)

    def score(self, rows: list[Record]) -> float:
        return sum(_log_p_backoff(self._cells[_key(r, self.features)], r.outcome, self._own[r.own]) for r in rows)

    def predict(self, r: Record) -> list[float]:
        """The chance of each outcome for R, from what has been learned."""
        cell, base = self._cells[_key(r, self.features)], self._own[r.own]
        return [math.exp(_log_p_backoff(cell, y, base)) for y in range(LEVELS)]

    def learn(self, rows: list[Record]) -> None:
        for r in rows:
            self._own[r.own][r.outcome] += 1
            self._cells[_key(r, self.features)][r.outcome] += 1


@dataclass(frozen=True)
class Shift:
    year: int
    frm: tuple
    to: tuple


class CaseEngine:
    def __init__(self, pool: tuple[str, ...], half_life: float = HALF_LIFE_YEARS):
        """HALF_LIFE is in steps: years, or 20 for quarters (ART-PLAN §10.7)."""
        self._decay = 0.5 ** (1 / half_life)
        sets = [c for k in range(len(pool) + 1) for c in combinations(pool, k)]
        self.schemes = {s: CaseScheme(s) for s in sets}
        self.leader: tuple = ()
        self.shifts: list[Shift] = []
        self._standing = {s: 0.0 for s in sets}   # decayed total score

    def step(self, year: int, rows: list[Record]) -> tuple[float, float]:
        """Score and learn one year. Returns the engine's score (its leader's,
        chosen before the year was seen) and own past's."""
        scores = {s: scheme.score(rows) for s, scheme in self.schemes.items()}
        result = (scores[self.leader], scores[()])
        for s, scheme in self.schemes.items():
            self._standing[s] = self._decay * self._standing[s] + scores[s]
            scheme.learn(rows)
        best = max(self._standing, key=self._standing.get)
        if best != self.leader and self._standing[best] - self._standing[self.leader] > SHIFT_NATS:
            self.shifts.append(Shift(year, self.leader, best))
            self.leader = best
        return result
