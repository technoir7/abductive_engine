"""
Prequential scoring (DESIGN §6): each week, before seeing it, a scheme gives
a distribution for each observed change, and is scored by the log density it
gave the change. Then it learns from the week. A score so earned is out of
sample every week, so a scheme pays for the parameters it has to learn and
needs no separate charge for complexity (no BIC: POE's replay 10).
"""
from __future__ import annotations

import math
from datetime import date
from typing import Protocol, Sequence

from .weeks import Week


class Scheme(Protocol):
    def predict(self, series: str) -> tuple[float, float]:
        """Mean and variance of the series' next change."""

    def score_and_learn(self, week: Week) -> dict[str, float]:
        """Log density of each observed change, given before learning from it."""


def gaussian_log_density(x: float, mean: float, var: float) -> float:
    return -0.5 * (math.log(2 * math.pi * var) + (x - mean) ** 2 / var)


def run(scheme: Scheme, weeks: Sequence[Week], score_from: date) -> list[float]:
    """Each week's total log score from SCORE_FROM on. Earlier weeks are
    learned from but not counted: every scheme starts with the same warm-up."""
    out = []
    for week in weeks:
        scores = scheme.score_and_learn(week)
        if week.friday >= score_from:
            out.append(sum(scores.values()))
    return out
