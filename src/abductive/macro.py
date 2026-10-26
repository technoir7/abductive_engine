"""
Macro: the eight FRED series POE's macro domain reads (DESIGN §3), and the
weeks of POE's replay 10 (DESIGN §9).

The credit spread is Moody's Baa yield less the 10-year Treasury (BAA10Y),
as in POE's replays: FRED serves the ICE BofA high-yield spread POE uses
live only for its last three years.
"""
from __future__ import annotations

from datetime import date, timedelta

from .weeks import Change

SERIES: dict[str, Change] = {
    "T10Y2Y": Change.DIFFERENCE,     # yield curve, percentage points
    "CPIAUCSL": Change.LOG,          # consumer prices
    "WALCL": Change.LOG,             # the Fed's balance sheet
    "BAA10Y": Change.DIFFERENCE,     # credit spread, percentage points
    "VIXCLS": Change.LOG,            # equity volatility
    "DEXUSEU": Change.LOG,           # dollars per euro
    "UNRATE": Change.DIFFERENCE,     # unemployment, percent
    "NASDAQCOM": Change.LOG,         # equities
}

FIRST, LAST = date(2003, 4, 4), date(2026, 10, 16)


def fridays(first: date = FIRST, last: date = LAST) -> list[date]:
    assert first.weekday() == 4, first
    return [first + timedelta(weeks=i) for i in range((last - first).days // 7 + 1)]
