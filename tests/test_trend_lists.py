"""Trends shown in POE (ART-PLAN §11): which trends this year are new,
growing, fading or argued over."""
from __future__ import annotations

from abductive.art_series import Claim
from abductive.trend_lists import candidates, shown, year_stats


def _claims(trend, year, writers, paper="guardian", force="asserts", stance="neutral"):
    # Months in March, so the year to September is the calendar year.
    return [Claim(trend, f"{year}-03", f"w{trend}-{stance}-{i}", force, stance, paper) for i in range(writers)]


def _filler(year, writers):
    # Other trends' writers, so shares are small and comparable across years.
    return _claims(999, year, writers)


def test_a_years_stats_count_writers_papers_and_verdicts_per_trend():
    claims = [Claim(1, "2026-03", "a", "judges", "approval", "guardian"),
              Claim(1, "2026-04", "b", "judges", "approval", "guardian"),
              Claim(1, "2026-05", "c", "judges", "disapproval", "nyt"),
              Claim(1, "2025-10", "d", "asserts", "neutral", "nyt"),      # October opens the year to September 2026
              Claim(2, "2026-03", "e", "asserts", "neutral", "nyt")]
    stats = year_stats(claims)
    cell = stats.cells[(1, 2026)]
    assert cell.writers == {"a", "b", "c", "d"} and cell.papers == {"guardian", "nyt"}
    assert (cell.approval, cell.disapproval) == (2, 1)
    assert stats.writers[2026] == {"a", "b", "c", "d", "e"}


def test_new_means_first_broad_in_2021_or_later_and_ranked_by_writers():
    claims = _claims(1, 2026, 20) + _claims(2, 2026, 30) + _claims(3, 2026, 40) + _filler(2026, 100)
    lists = candidates(year_stats(claims), {1: 2021, 2: 2024, 3: 2019}, now=2026)
    assert lists["new"] == [2, 1]


def test_trends_under_twelve_writers_this_year_are_left_out():
    claims = _claims(1, 2026, 11) + _filler(2026, 100)
    assert candidates(year_stats(claims), {1: 2025}, now=2026)["new"] == []


def test_growing_is_one_and_a_half_times_the_average_share_of_the_three_years_before():
    claims = _filler(2023, 1000) + _filler(2024, 1000) + _filler(2025, 1000) + _filler(2026, 1000)
    claims += _claims(1, 2023, 10) + _claims(1, 2024, 10) + _claims(1, 2025, 10) + _claims(1, 2026, 16)   # ×1.6
    claims += _claims(2, 2023, 10) + _claims(2, 2024, 10) + _claims(2, 2025, 10) + _claims(2, 2026, 14)   # ×1.4
    claims += _claims(3, 2026, 12)                                                                         # new: grows
    lists = candidates(year_stats(claims), {1: 2010, 2: 2010, 3: 2026}, now=2026)
    assert lists["growing"] == [3, 1]


def test_fading_is_half_its_best_share_of_the_three_years_before_when_that_year_was_broad():
    claims = _filler(2024, 100) + _filler(2025, 100) + _filler(2026, 100)
    claims += _claims(1, 2024, 30) + _claims(1, 2026, 14)      # 30 -> 14 of about the same total: fading
    claims += _claims(2, 2025, 11) + _claims(2, 2026, 1)       # best year had 11 writers: never broad
    claims += _claims(3, 2025, 20) + _claims(3, 2026, 15)      # not halved
    lists = candidates(year_stats(claims), {1: 2010, 2: 2010, 3: 2010}, now=2026)
    assert lists["fading"] == [1]


def test_a_trend_that_fell_silent_this_year_can_still_be_fading():
    claims = _filler(2025, 100) + _filler(2026, 100) + _claims(1, 2025, 20)
    assert candidates(year_stats(claims), {1: 2010}, now=2026)["fading"] == [1]


def test_argued_over_needs_ten_verdicts_and_ranks_by_the_minority_sides_share():
    claims = _filler(2026, 100)
    claims += _claims(1, 2026, 6, force="judges", stance="approval") + _claims(1, 2026, 6, force="judges", stance="disapproval")
    claims += _claims(2, 2026, 9, force="judges", stance="approval") + _claims(2, 2026, 3, force="judges", stance="disapproval")
    claims += _claims(3, 2026, 4, force="judges", stance="approval") + _claims(3, 2026, 4, force="judges", stance="disapproval") \
        + _claims(3, 2026, 8)                                   # 8 verdicts: too few
    lists = candidates(year_stats(claims), {1: 2010, 2: 2010, 3: 2010}, now=2026)
    assert lists["argued"] == [1, 2]


def test_shown_keeps_every_theme_whose_name_fits_this_years_claims():
    lists = {"new": list(range(20)), "growing": [3, 4], "fading": [], "argued": [5]}
    kinds = {k: "theme" for k in range(20)} | {4: "general", 5: "none"}
    fit = {k: 1.0 for k in range(20)} | {6: 0.4, 7: 0.5}
    out = shown(lists, kinds, fit, {k: str(k) for k in range(20)}, broad=set())
    assert out["new"] == [0, 1, 2, 3] + list(range(7, 20))       # 6 fits too few of its claims
    assert out["growing"] == [3] and out["argued"] == []


def test_a_theme_never_checked_against_its_claims_is_an_error():
    import pytest
    with pytest.raises(KeyError):
        shown({"new": [1], "growing": [], "fading": [], "argued": []}, {1: "theme"}, {}, {1: "a"}, broad=set())


def test_a_name_shows_once_and_a_fading_trend_carried_on_under_another_number_leaves_fading():
    lists = {"new": [1, 2, 3], "growing": [], "fading": [4, 5], "argued": []}
    kinds = {k: "theme" for k in range(1, 6)}
    fit = {k: 1.0 for k in range(1, 6)}
    names = {1: "food and art", 2: "food and art", 3: "punk", 4: "food and art", 5: "NFTs"}
    out = shown(lists, kinds, fit, names, broad={1, 2, 3})
    assert out["new"] == [1, 3] and out["fading"] == [5]
