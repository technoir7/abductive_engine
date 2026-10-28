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

Each link also carries the probability that it exists (level 2), from the
evidence for it: how much better its series was predicted with it than by a
shadow of the same model without it, week by week out of sample, recent
weeks counting more (DESIGN §5: prequential, not BIC). Even odds before any
evidence.

A scheme proposes the link the evidence most supports (DESIGN §7): among
links from its concepts it lacks, the one whose states last week would best
have explained its recent surprises in a series, if that explains more than
the link's extra parameters could by chance. The past suggests; only what
follows confirms, since a variant is scored only from its birth. It learns
its parameters from the past, as every scheme does.
"""
from __future__ import annotations

import math
from collections import deque
from dataclasses import dataclass
from itertools import product
from typing import Iterable, Mapping, Optional, Sequence

from .baselines import VAGUE, SeriesPersistence
from .concepts import Concept, degrees, state_at
from .scoring import gaussian_log_density
from .weeks import Change, Week

Link = tuple[Concept, str]   # a concept bears on a series
SHRINK = 10.0                # pseudo-observations of "no shift" for each combination of states
HALF_LIFE_WEEKS = 52         # how fast old evidence for a link fades
RECENT = 104                 # weeks of surprises a proposal is drawn from
MIN_CASES = 30
_DECAY = 0.5 ** (1 / HALF_LIFE_WEEKS)


@dataclass
class _Shift:
    """The base's errors under one combination of parent states, in units of
    the base's own spread: their mean and variance, shrunk towards 0 and 1."""
    n: float = 0.0
    total: float = 0.0
    squares: float = 0.0

    def add(self, z: float) -> None:
        self.n, self.total, self.squares = self.n + 1, self.total + z, self.squares + z * z

    def mean_and_scale(self) -> tuple[float, float]:
        mean = self.total / (self.n + SHRINK)
        return mean, max((self.squares + SHRINK) / (self.n + SHRINK) - mean * mean, 1e-6)


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
        sd = math.sqrt(var)
        for c, w in zip(combos, weights):
            shift, scale = self.shifts.get(c, _Shift()).mean_and_scale()
            out.append((w / total, mean + shift * sd, var * scale))
        return out

    def moments(self, config: tuple[Optional[int], ...]) -> tuple[float, float]:
        parts = self._components(config)
        mean = sum(w * m for w, m, _ in parts)
        return mean, sum(w * (v + m * m) for w, m, v in parts) - mean * mean

    def log_density(self, y: float, config: tuple[Optional[int], ...]) -> float:
        terms = [math.log(w) + gaussian_log_density(y, m, v) for w, m, v in self._components(config)]
        top = max(terms)
        return top + math.log(sum(math.exp(t - top) for t in terms))

    def learn(self, y: float, config: tuple[Optional[int], ...]) -> None:
        base = self.base.predict()
        if base is not None and self.parents and None not in config:
            mean, var = base
            self.shifts.setdefault(config, _Shift()).add((y - mean) / math.sqrt(var))   # type: ignore[arg-type]
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
        self._without: dict[Link, _SeriesModel] = {}   # each link's shadow: its series' model less it
        self._evidence: dict[Link, float] = {link: 0.0 for link in self.links}
        self._states: dict[Concept, list[Optional[int]]] = {c: [] for c in self.vocabulary}
        self._surprises: dict[str, deque[tuple[int, float]]] = {}   # (week index, standardized error)

    def parents(self, series: str) -> tuple[Concept, ...]:
        return tuple(sorted((c for c, s in self.links if s == series), key=self.vocabulary.index))

    def _shadow(self, link: Link, model: _SeriesModel) -> _SeriesModel:
        if link not in self._without:
            self._without[link] = _SeriesModel([p for p in model.parents if p != link[0]])
        return self._without[link]

    def _model(self, series: str) -> _SeriesModel:
        if series not in self._models:
            self._models[series] = _SeriesModel(self.parents(series))
        return self._models[series]

    def existence(self, link: Link) -> float:
        """The probability that LINK exists, given the evidence so far."""
        e = self._evidence[link]
        # Written per sign so exp() never sees a large positive argument.
        if e >= 0:
            return 1.0 / (1.0 + math.exp(-e))
        return math.exp(e) / (1.0 + math.exp(e))

    def score_and_learn(self, week: Week) -> dict[str, float]:
        """Each observed change's log density, from last week's concept states,
        given before learning from it."""
        scores = {}
        for s, y in week.changes.items():
            model = self._model(s)
            config = tuple(self._last[c] for c in model.parents)
            scores[s] = model.log_density(y, config)
            mean, var = model.moments(config)
            self._surprises.setdefault(s, deque(maxlen=RECENT)).append((len(self._weeks), (y - mean) / math.sqrt(var)))
            for c in model.parents:
                shadow = self._shadow((c, s), model)
                shadow_config = tuple(self._last[p] for p in shadow.parents)
                gain = scores[s] - shadow.log_density(y, shadow_config)
                self._evidence[(c, s)] = _DECAY * self._evidence[(c, s)] + gain
                shadow.learn(y, shadow_config)
            model.learn(y, config)
        self._weeks.append(week)
        i = len(self._weeks) - 1
        self._last = {c: state_at(c, self._weeks, i, self.kinds) for c in self.vocabulary}
        for c, state in self._last.items():
            self._states[c].append(state)
        return scores

    def proposal(self) -> Optional[Link]:
        """The link this scheme lacks that its recent surprises most support
        beyond chance, or None."""
        best, best_gain = None, 0.0
        for s, recent in sorted(self._surprises.items()):
            for c in self.vocabulary:
                if (c, s) in self.links:
                    continue
                cases = [(self._states[c][i - 1], z) for i, z in recent if i >= 1 and self._states[c][i - 1] is not None]
                gain = _explained(cases, degrees(c))
                if gain is not None and gain > best_gain:
                    best, best_gain = (c, s), gain
        return best

    def variant(self, add: Optional[Link] = None, remove: Optional[Link] = None) -> "Scheme":
        """This scheme with one link added or removed, its parameters learned
        from every week this one has seen."""
        links = (self.links | {add} if add else self.links) - ({remove} if remove else set())
        out = Scheme(self.vocabulary, frozenset(links), self.kinds)
        for week in self._weeks:
            out.score_and_learn(week)
        return out


def _explained(cases: list[tuple[int, float]], k: int) -> Optional[float]:
    """Log-likelihood gained by giving each state its own mean and spread for
    the surprises, less the chance penalty (½ ln n for each of the 2(k-1)
    extra parameters); None with too few cases to judge."""
    n = len(cases)
    if n < MIN_CASES:
        return None
    groups: dict[int, list[float]] = {}
    for state, z in cases:
        groups.setdefault(state, []).append(z)
    if len(groups) < 2 or any(len(g) < 3 for g in groups.values()):
        return None

    def fit(zs: list[float]) -> float:
        m = sum(zs) / len(zs)
        v = max(sum((z - m) ** 2 for z in zs) / len(zs), 1e-9)
        return -0.5 * len(zs) * (math.log(2 * math.pi * v) + 1)

    gain = sum(fit(g) for g in groups.values()) - fit([z for _, z in cases])
    return gain - (len(groups) - 1) * math.log(n)
