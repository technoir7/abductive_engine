"""A scheme (DESIGN §§5–6): a vocabulary of concepts and links from concepts
to series. Each series' change is predicted by its own persistence, shifted
by the states its linked concepts were in last week."""
import random
from datetime import date, timedelta

import pytest

from abductive.baselines import Persistence
from abductive.concepts import Concept, Form, Reproduction
from abductive.scheme import Scheme
from abductive.weeks import Change, Week

D0 = date(2000, 1, 7)
KINDS = {"X": Change.DIFFERENCE, "Y": Change.DIFFERENCE}
X_UP = Concept(Form(("X",), Reproduction.LEVEL, None, (0.0,)), occasion="test")
Y_UP = Concept(Form(("Y",), Reproduction.LEVEL, None, (0.0,)), occasion="test")


def driven(n, seed=0, effect=1.0):
    """X's level is +1 or -1 at random; Y's change follows X's level a week later."""
    rng, out, x_before = random.Random(seed), [], 0.0
    for i in range(n):
        x = rng.choice((-1.0, 1.0))
        y = effect * x_before + rng.gauss(0, 0.3)
        out.append(Week(D0 + timedelta(weeks=i), {"Y": y, "X": rng.gauss(0, 1)}, {"X": x, "Y": y}))
        x_before = x
    return out


def total(scheme, weeks, skip=50):
    """Learns from every week; counts the score of those after the first SKIP."""
    out = 0.0
    for i, w in enumerate(weeks):
        score = sum(scheme.score_and_learn(w).values())
        if i >= skip:
            out += score
    return out


def test_with_no_links_a_scheme_is_persistence():
    weeks = driven(200)
    a, b = Scheme((), frozenset(), KINDS), Persistence()
    for w in weeks:
        assert a.score_and_learn(w) == pytest.approx(b.score_and_learn(w))


def test_a_link_from_a_concept_that_bears_on_a_series_pays():
    weeks = driven(500)
    linked = Scheme((X_UP,), frozenset({(X_UP, "Y")}), KINDS)
    assert total(linked, weeks) > total(Scheme((), frozenset(), KINDS), weeks) + 200


def test_a_link_from_a_concept_that_does_not_costs_little():
    weeks = driven(500, effect=0.0)
    linked = Scheme((X_UP,), frozenset({(X_UP, "Y")}), KINDS)
    assert total(linked, weeks) > total(Scheme((), frozenset(), KINDS), weeks) - 15


def test_a_concept_predicts_from_last_weeks_state_not_this_weeks():
    # Y_UP this week is read from Y's own change this week; were it used, Y would be foretold.
    rng = random.Random(3)
    weeks = []
    for i in range(400):
        y = rng.choice((-1.0, 1.0)) + rng.gauss(0, 0.1)
        weeks.append(Week(D0 + timedelta(weeks=i), {"Y": y}, {"Y": y}))
    own = Scheme((Y_UP,), frozenset({(Y_UP, "Y")}), KINDS)
    assert total(own, weeks) < total(Scheme((), frozenset(), KINDS), weeks) + 10


def test_an_unknown_parent_is_averaged_over_not_assumed():
    weeks = driven(300)
    linked = Scheme((X_UP,), frozenset({(X_UP, "Y")}), KINDS)
    for w in weeks:
        linked.score_and_learn(w)
    linked.score_and_learn(Week(D0, {"Y": 1.0}, {}))                       # X unknown this week
    mixed = linked.score_and_learn(Week(D0, {"Y": 1.0}, {"X": 1.0}))["Y"]  # so Y is predicted not knowing it
    sharp = linked.score_and_learn(Week(D0, {"Y": 1.0}, {"X": 1.0}))["Y"]  # X was up: Y foretold
    assert mixed < sharp - 0.5   # not scored as if certain of X


def test_a_link_must_come_from_the_schemes_own_vocabulary():
    with pytest.raises(ValueError):
        Scheme((), frozenset({(X_UP, "Y")}), KINDS)


def test_a_link_that_bears_comes_to_be_believed():
    linked = Scheme((X_UP,), frozenset({(X_UP, "Y")}), KINDS)
    for w in driven(300):
        linked.score_and_learn(w)
    assert linked.existence((X_UP, "Y")) > 0.99


def test_a_link_that_does_not_bear_is_doubted():
    linked = Scheme((X_UP,), frozenset({(X_UP, "Y")}), KINDS)
    for w in driven(300, effect=0.0):
        linked.score_and_learn(w)
    assert linked.existence((X_UP, "Y")) < 0.5


def test_a_link_that_stops_bearing_loses_belief():
    linked = Scheme((X_UP,), frozenset({(X_UP, "Y")}), KINDS)
    weeks = driven(300) + driven(300, seed=1, effect=0.0)
    for w in weeks[:300]:
        linked.score_and_learn(w)
    assert linked.existence((X_UP, "Y")) > 0.99
    for w in weeks[300:]:
        linked.score_and_learn(w)
    assert linked.existence((X_UP, "Y")) < 0.5
