"""The weekly observations (DESIGN §3): each Friday, each series' change
since its previous published value, scored only in weeks it publishes."""
import math
from datetime import date, timedelta

import pytest

from abductive.observations import Row
from abductive.weeks import Change, weeks

FRI = date(2024, 3, 1)  # a Friday


def daily(series, start, values):
    return [Row(series, start + timedelta(days=i), v, start + timedelta(days=i + 1)) for i, v in enumerate(values)]


def test_a_daily_series_changes_from_last_fridays_latest_to_this_fridays():
    rows = daily("VIXCLS", FRI - timedelta(days=10), [10, 11, 12, 13, 14, 15, 16, 17, 18, 19])
    week = weeks(rows, [FRI - timedelta(days=7), FRI], {"VIXCLS": Change.LOG})[1]
    # Public by the earlier Friday: values measured up to 2 days before it (12);
    # by this Friday, up to the Thursday (19).
    assert week.changes["VIXCLS"] == pytest.approx(math.log(19) - math.log(12))


def test_a_rate_changes_by_its_difference():
    rows = daily("T10Y2Y", FRI - timedelta(days=10), [0.5] * 3 + [0.2] * 7)
    week = weeks(rows, [FRI - timedelta(days=7), FRI], {"T10Y2Y": Change.DIFFERENCE})[1]
    assert week.changes["T10Y2Y"] == pytest.approx(-0.3)


def test_a_series_with_nothing_new_is_not_observed_that_week():
    rows = [Row("UNRATE", date(2024, 1, 1), 3.7, date(2024, 2, 2)),
            Row("UNRATE", date(2024, 2, 1), 3.9, date(2024, 3, 8))]
    w = weeks(rows, [FRI - timedelta(days=7), FRI, FRI + timedelta(days=7)], {"UNRATE": Change.DIFFERENCE})
    assert "UNRATE" not in w[1].changes
    assert w[2].changes["UNRATE"] == pytest.approx(0.2)


def test_the_change_is_against_the_previous_value_as_revised_by_now():
    rows = [Row("CPIAUCSL", date(2024, 1, 1), 100.0, date(2024, 2, 16)),
            Row("CPIAUCSL", date(2024, 1, 1), 101.0, date(2024, 3, 14)),   # revised with...
            Row("CPIAUCSL", date(2024, 2, 1), 102.0, date(2024, 3, 14))]   # ...February's release
    w = weeks(rows, [date(2024, 3, 8), date(2024, 3, 15)], {"CPIAUCSL": Change.LOG})
    assert w[1].changes["CPIAUCSL"] == pytest.approx(math.log(102) - math.log(101))


def test_the_first_week_has_nothing_to_change_from():
    rows = daily("VIXCLS", FRI - timedelta(days=10), list(range(10, 20)))
    assert weeks(rows, [FRI], {"VIXCLS": Change.LOG})[0].changes == {}


def test_nothing_published_after_a_friday_is_seen_that_week():
    rows = daily("VIXCLS", FRI - timedelta(days=10), list(range(10, 20)))
    rows.append(Row("VIXCLS", FRI, 99.0, FRI + timedelta(days=1)))
    week = weeks(rows, [FRI - timedelta(days=7), FRI], {"VIXCLS": Change.LOG})[1]
    assert week.changes["VIXCLS"] == pytest.approx(math.log(19) - math.log(12))


def test_series_not_asked_for_are_ignored():
    rows = daily("VIXCLS", FRI - timedelta(days=10), list(range(10, 20)))
    assert weeks(rows, [FRI - timedelta(days=7), FRI], {})[1].changes == {}


def test_each_week_carries_every_series_latest_known_value():
    rows = [Row("UNRATE", date(2024, 1, 1), 3.7, date(2024, 2, 2)),
            Row("UNRATE", date(2024, 1, 1), 3.8, date(2024, 2, 27)),   # revised, nothing new
            Row("UNRATE", date(2024, 2, 1), 3.9, date(2024, 3, 8))]
    w = weeks(rows, [date(2024, 2, 23), FRI, FRI + timedelta(days=7)], {"UNRATE": Change.DIFFERENCE})
    assert [x.levels for x in w] == [{"UNRATE": 3.7}, {"UNRATE": 3.8}, {"UNRATE": 3.9}]
