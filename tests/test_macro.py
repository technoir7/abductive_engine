"""Macro's weekly observations from POE's export, when it is present."""
from collections import Counter
from pathlib import Path

import pytest

from abductive import macro
from abductive.observations import read_csv
from abductive.weeks import weeks

EXPORT = Path(__file__).parent.parent / "data" / "observations.csv"


def test_the_replay_runs_friday_to_friday():
    f = macro.fridays()
    assert f[0].isoformat() == "2003-04-04" and f[-1].isoformat() == "2026-10-16"
    assert len(f) == 1229


@pytest.mark.skipif(not EXPORT.exists(), reason="POE's export not present")
def test_each_series_is_observed_as_often_as_it_publishes():
    w = weeks(read_csv(EXPORT), macro.fridays(), macro.SERIES)
    seen = Counter(s for week in w for s in week.changes)
    weeks_n = len(w) - 1
    for daily in ("T10Y2Y", "BAA10Y", "VIXCLS", "DEXUSEU", "NASDAQCOM", "WALCL"):
        assert seen[daily] >= 0.97 * weeks_n, daily
    for monthly in ("CPIAUCSL", "UNRATE"):
        assert 0.2 * weeks_n <= seen[monthly] <= 0.25 * weeks_n, monthly
