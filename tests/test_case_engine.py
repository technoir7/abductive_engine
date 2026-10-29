"""The engine on cases (ART-PLAN §9): every set of mechanisms kept as a
rival scheme, a leader that changes only when a rival is decisively ahead."""
from __future__ import annotations

import random

from abductive.case_engine import CaseEngine
from abductive.cases import Record


def _year(y, n, rng, matters):
    rows = []
    for _ in range(n):
        own, f, g = rng.randrange(4), rng.randrange(2), rng.randrange(2)
        outcome = 2 * f if matters else rng.choice((0, 0, 1, 2))
        rows.append(Record(y, (own,), {"f": f, "g": g}, outcome))
    return rows


def _run(engine, years, matters_from, n=300, seed=0):
    rng, out = random.Random(seed), {}
    for y in years:
        out[y] = engine.step(y, _year(y, n, rng, y >= matters_from))
    return out


def test_every_set_of_mechanisms_is_a_rival():
    engine = CaseEngine(("f", "g"))
    assert set(engine.schemes) == {(), ("f",), ("g",), ("f", "g")}
    assert engine.leader == ()


def test_noise_never_takes_the_lead():
    engine = CaseEngine(("f", "g"))
    _run(engine, range(2000, 2015), matters_from=9999)
    assert engine.leader == () and engine.shifts == []


def test_a_mechanism_that_starts_to_matter_takes_the_lead_and_the_change_is_recorded():
    engine = CaseEngine(("f", "g"))
    scores = _run(engine, range(2000, 2015), matters_from=2006)
    assert engine.leader == ("f",)
    # Learned from 2006's cases, it predicts better from 2007: the earliest it could lead.
    assert [(s.year, s.to) for s in engine.shifts] == [(2007, ("f",))]
    # The engine's score for a year is its leader's before the year was seen.
    engine_2006, own_2006 = scores[2006]
    assert engine_2006 == own_2006
    engine_late, own_late = scores[2014]
    assert engine_late > own_late + 100


def test_a_scheme_predicts_a_case_from_what_it_has_learned():
    from abductive.case_engine import CaseScheme
    scheme = CaseScheme(("f",))
    scheme.learn([Record(0, (0,), {"f": 1}, 2)] * 20 + [Record(0, (0,), {"f": 0}, 0)] * 20)
    p = scheme.predict(Record(1, (0,), {"f": 1}, None))
    assert abs(sum(p) - 1) < 1e-9 and p[2] > 0.8
