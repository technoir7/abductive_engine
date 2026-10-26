"""Each concept's degrees by quarter, and the random control (ART-PLAN §4)."""
import random

from abductive.art_series import Claim, degrees, quarter, shuffled_concepts


def test_months_fall_in_quarters():
    assert [quarter("2004-01"), quarter("2004-03"), quarter("2004-04"), quarter("2005-12")] == [16, 16, 17, 23]


def test_a_concepts_degrees_count_writers_and_the_balance_of_judgement():
    claims = [Claim(0, "2004-01", "Jones", "judges", "approval"),
              Claim(0, "2004-02", "Jones", "judges", "approval"),     # same writer, same quarter: one writer
              Claim(0, "2004-03", "Cumming", "judges", "disapproval"),
              Claim(0, "2004-05", "Searle", "reports", "neither"),
              Claim(1, "2004-01", "Searle", "reports", "neither")]
    got = degrees(claims)
    assert got[0][16] == {"writers": 2, "approval": 2, "disapproval": 1}
    assert got[0][17] == {"writers": 1, "approval": 0, "disapproval": 0}
    assert set(got) == {0, 1}


def test_the_control_keeps_each_concepts_size_and_each_claims_place_in_time():
    claims = [Claim(c, f"2004-0{1 + i % 9}", f"w{i}", "reports", "neither") for i, c in enumerate([0] * 5 + [1] * 3 + [2] * 2)]
    out = shuffled_concepts(claims, random.Random(0))
    assert sorted(c.concept for c in out) == sorted(c.concept for c in claims)
    assert [(c.month, c.writer) for c in out] == [(c.month, c.writer) for c in claims]
    assert [c.concept for c in out] != [c.concept for c in claims]


def test_series_are_concepts_held_by_enough_writers_over_enough_quarters():
    from abductive.art_series import select
    claims = [Claim(0, f"{2000 + q // 4}-{(q % 4) * 3 + 1:02d}", f"w{q % 5}", "reports", "neither") for q in range(8)]
    claims += [Claim(1, "2004-01", f"w{i}", "reports", "neither") for i in range(9)]       # many writers, one quarter
    assert select(claims, min_writers=5, min_quarters=8) == [0]


def test_quarters_become_periods_with_every_series_observed():
    from datetime import date

    from abductive.art_series import periods
    deg = {0: {16: {"writers": 2, "approval": 0, "disapproval": 0}, 18: {"writers": 5, "approval": 0, "disapproval": 0}}}
    got = periods(deg, [0], first=16, last=18)
    assert [p.friday for p in got] == [date(2004, 6, 30), date(2004, 9, 30)]
    assert [p.changes for p in got] == [{"c0": -2.0}, {"c0": 5.0}]
    assert got[-1].levels == {"c0": 5.0}


def test_a_concept_is_observed_only_from_its_founding_until_it_goes_dormant():
    from abductive.art_series import periods
    deg = {0: {10: {"writers": 2, "approval": 0, "disapproval": 0}, 12: {"writers": 1, "approval": 0, "disapproval": 0}}}
    got = {p.friday.year * 4 + (p.friday.month - 1) // 3 - 8000: p for p in periods(deg, [0], first=0, last=30)}
    assert "c0" not in got[9].changes                      # before it was founded
    assert got[10].changes["c0"] == 2.0 and got[11].changes["c0"] == -2.0
    assert "c0" in got[20].changes                         # dormant only after 8 quarters unasserted
    assert "c0" not in got[21].changes and "c0" not in got[21].levels
