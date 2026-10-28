"""Cases and mechanisms (ART-PLAN §8): one hypothesis judged across many
cases, each year predicted from earlier years only."""
from __future__ import annotations

import random

from abductive.art_series import Claim
from abductive.cases import Record, concept_years, dealt, doubling, judge, level


def test_levels_are_none_one_several():
    assert [level(n) for n in (0, 1, 2, 7)] == [0, 1, 2, 2]


def _records(years, n, rule, seed=0):
    rng, out = random.Random(seed), []
    for y in years:
        for _ in range(n):
            f = rng.randrange(2)
            out.append(Record(y, (0,), {"f": f, "noise": rng.randrange(2)}, rule(f, rng)))
    return out


def test_a_feature_that_settles_the_outcome_pays_and_noise_does_not():
    records = _records(range(2000, 2010), 200, lambda f, rng: 2 * f)
    assert judge(records, "f").gain > 500
    assert judge(records, "noise").gain < 5


def test_the_first_year_is_learned_not_scored():
    records = _records(range(2000, 2003), 50, lambda f, rng: f)
    result = judge(records, "f")
    assert sorted(result.by_year) == [2001, 2002]
    assert result.cases == 100


def test_no_year_is_scored_with_anything_learned_from_later_years():
    early = _records(range(2000, 2005), 200, lambda f, rng: f)
    later = _records([2005, 2006], 200, lambda f, rng: 2 * (1 - f), seed=1)
    alone, together = judge(early, "f").by_year, judge(early + later, "f").by_year
    assert {y: g for y, g in together.items() if y < 2005} == alone


def test_dealing_keeps_each_years_values_and_moves_them_between_cases():
    records = _records(range(2000, 2003), 100, lambda f, rng: f)
    moved = dealt(records, "f", random.Random(0))
    for y in range(2000, 2003):
        assert sorted(r.features["f"] for r in records if r.year == y) == \
               sorted(r.features["f"] for r in moved if r.year == y)
    assert [r.features["f"] for r in moved] != [r.features["f"] for r in records]
    assert [r.outcome for r in moved] == [r.outcome for r in records]


def _claim(concept, month, writer, paper="guardian", force="reports", stance="neither"):
    return Claim(concept, month, writer, force, stance, paper)


def test_a_concepts_year_reads_its_writers_quality_papers_and_modality():
    claims = [
        _claim(1, "2005-02", "A", force="judges", stance="approval"),
        _claim(1, "2005-06", "B", paper="nyt", force="judges", stance="disapproval"),
        _claim(1, "2005-07", "B", force="predicts"),
        _claim(1, "2006-03", "C"),
    ]
    rows = {r.year: r for r in concept_years(claims, founded={1: "2004-11"}, last_year=2006)}
    r = rows[2005]
    assert r.own == (2, 1)                       # several writers; aged 1 year
    assert r.features == {"contested": 2, "both_papers": 1, "modality": 1}
    assert r.outcome == 1                        # one writer in 2006
    assert rows[2004].own == (0, 0) and rows[2004].features["contested"] == 0


def test_a_concept_two_years_unasserted_is_no_longer_a_case():
    claims = [_claim(1, "2001-01", "A"), _claim(1, "2005-01", "B")]
    years = [r.year for r in concept_years(claims, founded={1: "2001-01"}, last_year=2006)]
    # Unasserted through 2002 and 2003: dead by the end of 2003 by the synthesis rule.
    assert years == [2001, 2002]


def test_doubling_bins():
    assert [doubling(n) for n in (0, 1, 2, 3, 4, 5, 8, 9, 16, 17, 400)] == [0, 1, 2, 3, 3, 4, 4, 5, 5, 6, 6]


def test_the_fine_own_past_reads_this_years_writers_and_the_writers_so_far():
    claims = [_claim(1, "2004-11", "A"), _claim(1, "2005-02", "B"), _claim(1, "2005-06", "C"),
              _claim(1, "2005-07", "D"), _claim(1, "2006-03", "A")]
    rows = {r.year: r for r in concept_years(claims, founded={1: "2004-11"}, last_year=2006, fine=True)}
    assert rows[2004].own == (1, 1, 0)
    assert rows[2005].own == (3, 3, 1)           # 3 writers this year (3-4), 4 so far (3-4), aged 1
