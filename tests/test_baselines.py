"""Prequential scoring and the baselines (DESIGN §§6, 8): each week a scheme
gives its distribution for the week's changes before seeing them, and is
scored by the log-probability it gave them."""
import math
import random
from datetime import date, timedelta

import pytest

from abductive.baselines import Independence, Persistence
from abductive.scoring import run
from abductive.weeks import Week

D0 = date(2000, 1, 7)


def series_weeks(values, name="X"):
    return [Week(D0 + timedelta(weeks=i), {name: v}) for i, v in enumerate(values)]


def ar1(n, b, seed=0, sd=1.0):
    rng, y, out = random.Random(seed), 0.0, []
    for _ in range(n):
        y = b * y + rng.gauss(0, sd)
        out.append(y)
    return out


def test_a_week_is_scored_before_it_is_learned_from():
    scheme = Independence()
    for w in series_weeks([0.1, -0.1, 0.2, -0.2, 0.0] * 10):
        scheme.score_and_learn(w)
    calm = scheme.score_and_learn(Week(D0, {"X": 0.0}))["X"]
    outlier = scheme.score_and_learn(Week(D0, {"X": 50.0}))["X"]
    assert outlier < calm - 100   # had it learned from the outlier first, it would not be so surprised


def test_independence_predicts_the_past_mean_and_spread():
    scheme = Independence()
    values = [1.0, 3.0] * 50
    for w in series_weeks(values):
        scheme.score_and_learn(w)
    mean, var = scheme.predict("X")
    assert mean == pytest.approx(2.0) and var == pytest.approx(1.0, rel=0.05)


def test_persistence_beats_independence_where_changes_persist():
    weeks = series_weeks(ar1(600, 0.8))
    ind, per = run(Independence(), weeks, score_from=weeks[100].friday), run(Persistence(), weeks, score_from=weeks[100].friday)
    assert sum(per) > sum(ind) + 50


def test_persistence_does_no_worse_where_nothing_persists():
    weeks = series_weeks(ar1(600, 0.0, seed=1))
    ind, per = run(Independence(), weeks, score_from=weeks[100].friday), run(Persistence(), weeks, score_from=weeks[100].friday)
    assert sum(per) > sum(ind) - 10


def test_persistences_spread_follows_recent_volatility():
    scheme = Persistence()
    for w in series_weeks(ar1(200, 0.0, sd=0.1) + ar1(30, 0.0, seed=2, sd=2.0)):
        scheme.score_and_learn(w)
    _, var = scheme.predict("X")
    assert var > 1.0   # the calm stretch's 0.01 is forgotten within weeks


def test_a_series_not_observed_is_neither_scored_nor_learned():
    scheme = Persistence()
    for w in series_weeks([0.5, -0.2, 0.3] * 10):
        scheme.score_and_learn(w)
    before = scheme.predict("X")
    assert scheme.score_and_learn(Week(D0, {})) == {}
    assert scheme.predict("X") == before


def test_only_weeks_from_the_start_of_scoring_are_counted_but_all_are_learned():
    weeks = series_weeks(ar1(50, 0.5))
    scores = run(Persistence(), weeks, score_from=weeks[10].friday)
    assert len(scores) == 40
    assert all(math.isfinite(s) for s in scores)
