"""
A scheme: one vocabulary, its links, and their parameters (DESIGN §§5–6).

Each series' change is predicted from its own persistence (the base every
scheme shares, so a scheme with no links is the persistence baseline) and,
for each link into it, the state its concept was in last week. Each
combination of parent states learns how far it shifts the base's mean, and
how far it widens or narrows its spread, shrunk towards no shift until the
evidence for it accumulates.

Links run from last week's states only. A link within the same week would
need the week's observations ordered so that no concept predicts an
observation it is read from; that waits until these links are tested.

A parent whose state is unknown is averaged over the states it has been
seen in, not assumed (DESIGN §6: nothing is scored as certain for free).
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from itertools import product
from typing import Iterable, Mapping, Optional, Sequence

from .baselines import VAGUE, SeriesPersistence
from .concepts import Concept, degrees, state_at
from .scoring import gaussian_log_density
from .weeks import Change, Week

Link = tuple[Concept, str]   # a concept bears on a series
SHRINK = 10.0                # pseudo-observations of "no shift" for each combination of states


@dataclass
class _Shift:
    n: float = 0.0
    residuals: float = 0.0
    ratios: float = 0.0   # squared residual over the base's variance

    def mean_and_scale(self) -> tuple[float, float]:
        return self.residuals / (self.n + SHRINK), (self.ratios + SHRINK) / (self.n + SHRINK)


class _SeriesModel:
    def __init__(self, parents: Sequence[Concept]) -> None:
        self.parents = tuple(parents)
        self.base = SeriesPersistence()
        self.shifts: dict[tuple[int, ...], _Shift] = {}

    def _components(self, config: tuple[Optional[int], ...]) -> list[tuple[float, float, float]]:
        """(weight, mean, variance) for each combination of parent states consistent with CONFIG."""
        base = self.base.predict()
        if base is None:
            return [(1.0, *VAGUE)]
        mean, var = base
        if not self.parents:
            return [(1.0, mean, var)]
        choices = [range(degrees(p)) if s is None else (s,) for p, s in zip(self.parents, config)]
        combos = list(product(*choices))
        weights = [self.shifts.get(c, _Shift()).n + 1.0 for c in combos]
        total = sum(weights)
        out = []
        for c, w in zip(combos, weights):
            shift, scale = self.shifts.get(c, _Shift()).mean_and_scale()
            out.append((w / total, mean + shift, var * scale))
        return out

    def log_density(self, y: float, config: tuple[Optional[int], ...]) -> float:
        terms = [math.log(w) + gaussian_log_density(y, m, v) for w, m, v in self._components(config)]
        top = max(terms)
        return top + math.log(sum(math.exp(t - top) for t in terms))

    def learn(self, y: float, config: tuple[Optional[int], ...]) -> None:
        base = self.base.predict()
        if base is not None and self.parents and None not in config:
            mean, var = base
            r = y - mean
            s = self.shifts.setdefault(config, _Shift())   # type: ignore[arg-type]
            s.n, s.residuals, s.ratios = s.n + 1, s.residuals + r, s.ratios + r * r / var
        self.base.add(y)


class Scheme:
    def __init__(self, vocabulary: Iterable[Concept], links: frozenset[Link], kinds: Mapping[str, Change]) -> None:
        self.vocabulary = tuple(vocabulary)
        self.links = frozenset(links)
        unknown = {c for c, _ in self.links} - set(self.vocabulary)
        if unknown:
            raise ValueError(f"links from concepts outside the vocabulary: {unknown}")
        self.kinds = dict(kinds)
        self._weeks: list[Week] = []
        self._models: dict[str, _SeriesModel] = {}
        self._last: dict[Concept, Optional[int]] = {c: None for c in self.vocabulary}

    def parents(self, series: str) -> tuple[Concept, ...]:
        return tuple(sorted((c for c, s in self.links if s == series), key=self.vocabulary.index))

    def _model(self, series: str) -> _SeriesModel:
        if series not in self._models:
            self._models[series] = _SeriesModel(self.parents(series))
        return self._models[series]

    def score_and_learn(self, week: Week) -> dict[str, float]:
        """Each observed change's log density, from last week's concept states,
        given before learning from it."""
        scores = {}
        for s, y in week.changes.items():
            model = self._model(s)
            config = tuple(self._last[c] for c in model.parents)
            scores[s] = model.log_density(y, config)
            model.learn(y, config)
        self._weeks.append(week)
        i = len(self._weeks) - 1
        self._last = {c: state_at(c, self._weeks, i, self.kinds) for c in self.vocabulary}
        return scores
