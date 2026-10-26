"""
The baselines every scheme is scored against (DESIGN §8).

Independence: each series' change is Gaussian with the mean and variance of
its past changes, ignoring order.

Persistence: each change depends on that series' own last change (a
regression on it, fitted to the past), and its spread is an exponentially
weighted variance of recent errors, so calm and wild stretches are already
allowed for. This is the baseline POE could not beat: a formed concept must
explain something beyond it, not merely notice that volatility comes and
goes.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .scoring import gaussian_log_density
from .weeks import Week

VAGUE = (0.0, 1.0)   # before anything is known; only ever seen in the warm-up
HALF_LIFE = 13        # observations: a quarter of a weekly series, about a year of a monthly one
_ALPHA = 1 - 0.5 ** (1 / HALF_LIFE)
_FLOOR = 1e-12        # a variance is never exactly zero


@dataclass
class _Moments:
    n: int = 0
    mean: float = 0.0
    m2: float = 0.0

    def add(self, x: float) -> None:
        self.n += 1
        d = x - self.mean
        self.mean += d / self.n
        self.m2 += d * (x - self.mean)

    @property
    def var(self) -> float:
        return max(self.m2 / (self.n - 1), _FLOOR)


class Independence:
    def __init__(self) -> None:
        self._m: dict[str, _Moments] = {}

    def predict(self, series: str) -> tuple[float, float]:
        m = self._m.get(series)
        return VAGUE if m is None or m.n < 2 else (m.mean, m.var)

    def score_and_learn(self, week: Week) -> dict[str, float]:
        scores = {}
        for s, x in week.changes.items():
            scores[s] = gaussian_log_density(x, *self.predict(s))
            self._m.setdefault(s, _Moments()).add(x)
        return scores


@dataclass
class SeriesPersistence:
    """One series' persistence: its change on its last change, with an intercept,
    by least squares on all past pairs, and an exponentially weighted variance
    of its errors. Shared by every scheme as the base it must add to."""
    n: int = 0
    sx: float = 0.0
    sy: float = 0.0
    sxx: float = 0.0
    sxy: float = 0.0
    last: float | None = None
    error_var: float | None = None
    errors: list[float] = field(default_factory=list)

    def coefficients(self) -> tuple[float, float]:
        if self.n < 3:
            return (self.sy / self.n if self.n else 0.0), 0.0
        cov = self.sxy - self.sx * self.sy / self.n
        var = self.sxx - self.sx ** 2 / self.n
        slope = cov / var if var > _FLOOR else 0.0
        return (self.sy - slope * self.sx) / self.n, slope

    def mean(self) -> float:
        a, b = self.coefficients()
        return a + b * (self.last if self.last is not None else 0.0)

    def add(self, y: float) -> None:
        error = y - self.mean()
        if self.error_var is None:
            self.errors.append(error * error)
            if len(self.errors) >= 5:   # start the weighted variance from a plain one
                self.error_var = sum(self.errors) / len(self.errors)
        else:
            self.error_var += _ALPHA * (error * error - self.error_var)
        if self.last is not None:
            x = self.last
            self.n += 1
            self.sx, self.sy, self.sxx, self.sxy = self.sx + x, self.sy + y, self.sxx + x * x, self.sxy + x * y
        self.last = y

    def predict(self) -> tuple[float, float] | None:
        """Mean and variance of the next change, or None before the error variance is known."""
        return None if self.error_var is None else (self.mean(), max(self.error_var, _FLOOR))


class Persistence:
    def __init__(self) -> None:
        self._r: dict[str, SeriesPersistence] = {}

    def predict(self, series: str) -> tuple[float, float]:
        r = self._r.get(series)
        return (r.predict() if r is not None else None) or VAGUE

    def score_and_learn(self, week: Week) -> dict[str, float]:
        scores = {}
        for s, x in week.changes.items():
            scores[s] = gaussian_log_density(x, *self.predict(s))
            self._r.setdefault(s, SeriesPersistence()).add(x)
        return scores
