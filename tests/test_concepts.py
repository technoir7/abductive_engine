"""Defined concepts under the fixed table of forms (DESIGN §4,
EPISTEMOLOGY §5): a rule assigning each week a state, from one series,
several, or all, held over a window, in two or three ordered degrees."""
import math
from datetime import date, timedelta

import pytest

from abductive.concepts import Concept, Form, Quantity, Reproduction, states
from abductive.weeks import Change, Week

D0 = date(2000, 1, 7)
KINDS = {"A": Change.LOG, "B": Change.DIFFERENCE, "C": Change.DIFFERENCE}


def levels(**series):
    n = len(next(iter(series.values())))
    return [Week(D0 + timedelta(weeks=i), {}, {s: v[i] for s, v in series.items()}) for i in range(n)]


def concept(*series, reproduction=Reproduction.CHANGE, window=4, cuts=(0.0,)):
    return Concept(Form(tuple(series), reproduction, window, cuts), occasion="test")


def test_a_change_over_k_weeks_in_two_degrees():
    w = levels(B=[0, 1, 2, 3, 4, 3, 2, 1, 0])
    assert states(concept("B"), w, KINDS) == [None] * 4 + [1, 1, 0, 0, 0]


def test_a_positive_series_changes_by_its_log():
    w = levels(A=[100, 100, 100, 100, 110, 99])
    got = states(concept("A", cuts=(math.log(1.05),)), w, KINDS)
    assert got[4:] == [1, 0]   # up 10% over 4 weeks; then down 1%


def test_a_level_against_its_trailing_weeks_in_three_degrees():
    base = [1.0, -1.0] * 2
    w = levels(B=base + [0.0, 5.0, -5.0])
    c = concept("B", reproduction=Reproduction.ZSCORE, window=4, cuts=(-1.0, 1.0))
    assert states(c, w, KINDS)[4:] == [1, 2, 0]


def test_a_plain_level_needs_no_window():
    w = levels(B=[-2.0, 0.5, 3.0])
    c = concept("B", reproduction=Reproduction.LEVEL, window=None, cuts=(0.0, 1.0))
    assert states(c, w, KINDS) == [0, 1, 2]


def test_several_series_are_taken_together_by_their_mean_z_score():
    w = levels(B=[1.0, -1.0, 1.0, -1.0, 3.0], C=[1.0, -1.0, 1.0, -1.0, -3.0])
    c = concept("B", "C", reproduction=Reproduction.ZSCORE, window=4, cuts=(0.5,))
    assert states(c, w, KINDS)[4] == 0   # one far above usual, one far below: together, usual


def test_quantity_follows_from_the_series():
    assert concept("A").form.quantity is Quantity.UNITY
    assert concept("A", "B", reproduction=Reproduction.ZSCORE).form.quantity is Quantity.PLURALITY
    assert Form(("A", "B", "C"), Reproduction.ZSCORE, 13, (0.0,)).quantity_in(KINDS) is Quantity.TOTALITY


def test_a_week_the_series_is_unknown_has_no_state():
    w = [Week(D0, {}, {}), *levels(B=[0.0, 1.0])]
    assert states(concept("B", reproduction=Reproduction.LEVEL, window=None), w, KINDS) == [None, 0, 1]


@pytest.mark.parametrize("form", [
    lambda: Form(("A",), Reproduction.CHANGE, 5, (0.0,)),                  # window not in the table
    lambda: Form(("A",), Reproduction.CHANGE, 4, ()),                      # no degrees
    lambda: Form(("A",), Reproduction.CHANGE, 4, (1.0, 0.0)),              # degrees out of order
    lambda: Form(("A",), Reproduction.CHANGE, 4, (0.0, 1.0, 2.0)),         # four degrees
    lambda: Form(("A", "B"), Reproduction.CHANGE, 4, (0.0,)),              # unlike units added together
    lambda: Form(("A",), Reproduction.LEVEL, 4, (0.0,)),                   # a level has no window
])
def test_a_form_outside_the_table_cannot_be_made(form):
    with pytest.raises(ValueError):
        form()


def test_a_concept_keeps_its_pedigree():
    c = Concept(Form(("A",), Reproduction.ZSCORE, 52, (1.2,)), occasion="anomaly in VIXCLS, 2008-09-19")
    assert c.pedigree() == "A, z-score over 52 weeks, cut at 1.2 (anomaly in VIXCLS, 2008-09-19)"
