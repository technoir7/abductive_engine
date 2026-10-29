"""Cases and mechanisms (ART-PLAN §8): one hypothesis judged across many
cases, each year predicted from earlier years only."""
from __future__ import annotations

import random

from abductive.art_series import Claim
from abductive.cases import Record, concept_years, dealt, doubling, forecast, judge, level


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


def test_a_forecast_uses_only_earlier_years_and_names_its_case():
    records = _records(range(2000, 2005), 200, lambda f, rng: 2 * f)
    target = [Record(2005, (0,), {"f": 1, "noise": 0}, 0, case="x")]
    [(case, p_own, p_with)] = forecast(records + target, "f", 2005)
    assert case == "x"
    assert abs(sum(p_own) - 1) < 1e-9 and abs(sum(p_with) - 1) < 1e-9
    assert p_with[2] > 0.95 and 0.3 < p_own[2] < 0.7     # learned from 2000-2004 only


def test_each_concept_year_names_its_concept():
    rows = concept_years([_claim(7, "2004-11", "A")], founded={7: "2004-11"}, last_year=2006)
    assert {r.case for r in rows} == {7}


def test_with_backoff_noise_costs_little_and_a_settling_feature_still_pays():
    # Many small own-past cells, as with finely graded size: splitting them costs.
    rng, records = random.Random(0), []
    for y in range(2000, 2010):
        for _ in range(300):
            own = rng.randrange(60)
            records.append(Record(y, (own,), {"noise": rng.randrange(3)}, own % 3))
    uniform, backed = judge(records, "noise").gain, judge(records, "noise", backoff=True).gain
    assert uniform < -50 and uniform / 3 < backed <= 0   # noise never pays
    settled = _records(range(2000, 2010), 200, lambda f, rng: 2 * f)
    assert judge(settled, "f", backoff=True).gain > 500


def test_features_can_be_judged_together():
    records = _records(range(2000, 2010), 200, lambda f, rng: 2 * f)
    assert judge(records, ("f", "noise"), backoff=True).gain > 500


def test_a_concept_is_named_by_what_its_claims_are_most_often_about():
    from abductive.cases import concept_labels
    claims = [Claim(1, "2005-01", "A", "reports", "neither", "nyt", about="Guernica"),
              Claim(1, "2005-02", "B", "reports", "neither", "nyt", about="Picasso's Guernica"),
              Claim(1, "2005-03", "C", "reports", "neither", "nyt", about="Picasso's Guernica"),
              Claim(2, "2005-03", "C", "reports", "neither", "nyt", about="graffiti")]
    assert concept_labels(claims) == {1: "Picasso's Guernica", 2: "graffiti"}


def test_a_trends_quarter_reads_its_writers_and_grades_features_against_that_quarters_trends():
    from abductive.cases import trend_quarters
    claims = [
        _claim(1, "2000-01", "A", force="judges", stance="approval"),
        _claim(1, "2000-02", "B", paper="nyt", force="judges", stance="disapproval"),
        _claim(1, "2000-03", "C", force="judges", stance="approval"),
        *[_claim(1, "2000-04", w) for w in "ABCD"],
        _claim(2, "2000-01", "A", force="judges", stance="approval"),
        _claim(2, "2000-02", "B", force="predicts", stance="disapproval"),
        _claim(2, "2000-03", "B", force="judges", stance="disapproval"),
    ]
    rows = {(r.case, r.year): r for r in trend_quarters(claims, {1: 0, 2: 0}, open_quarter=2)}
    one, two = rows[(1, 0)], rows[(2, 0)]
    assert one.own == (3, 0, 0)                  # three writers; none before; first year
    assert one.outcome == 1                      # four next quarter: the same doubling bin
    assert one.features == {"contested": 1, "both_papers": 1, "modality": 0}
    assert two.features == {"contested": 2, "both_papers": 0, "modality": 1}   # the only one with modality: at the median
    assert two.outcome == 0                      # nobody next quarter
    assert rows[(1, 1)].own == (3, 3, 0)         # four writers; three before
    assert rows[(1, 2)].outcome is None          # the open quarter


def test_a_trend_eight_quarters_unasserted_is_no_longer_a_case():
    from abductive.cases import trend_quarters
    claims = [_claim(1, "2000-01", "A")]
    assert [r.year for r in trend_quarters(claims, {1: 0}, open_quarter=20)] == list(range(8))


def test_trends_can_step_by_years_ending_in_september():
    from abductive.cases import trend_quarters, year_to_september
    assert [year_to_september(m) for m in ("2000-09", "2000-10", "2001-09")] == [0, 1, 1]
    claims = [_claim(1, "2000-10", "A"), _claim(1, "2001-03", "B"), _claim(1, "2001-11", "C")]
    rows = {r.year: r for r in trend_quarters(claims, {1: 1}, open_quarter=2, per_year=1)}
    assert rows[1].own == (2, 0, 0)              # two writers in the year to September 2001
    assert rows[1].outcome == 0                  # one the year after: a bin lower
    assert rows[2].own == (1, 2, 1) and rows[2].outcome is None


def test_a_big_trend_can_still_rise():
    from abductive.cases import trend_quarters
    claims = [_claim(1, "2000-01", f"w{i}") for i in range(20)] + [_claim(1, "2000-04", f"w{i}") for i in range(40)]
    r = next(r for r in trend_quarters(claims, {1: 0}, open_quarter=1) if r.year == 0)
    assert r.own[0] == 6 and r.outcome == 2       # 20 writers, then 40: a bin up
    assert doubling(400, None) == 10 and doubling(400) == 6
