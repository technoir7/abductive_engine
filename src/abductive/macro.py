"""
Macro: the eight FRED series POE's macro domain reads (DESIGN §3), and the
weeks of POE's replay 10 (DESIGN §9).

The credit spread is Moody's Baa yield less the 10-year Treasury (BAA10Y),
as in POE's replays: FRED serves the ICE BofA high-yield spread POE uses
live only for its last three years.
"""
from __future__ import annotations

import math
from datetime import date, timedelta

from .concepts import Concept, Form, Reproduction
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


def _poe(series: str, reproduction: Reproduction, window, cuts) -> Concept:
    return Concept(Form((series,), reproduction, window, cuts), occasion="POE's hand-written vocabulary")


def poe_vocabulary() -> tuple[Concept, ...]:
    """POE's eight macro signals, each as the nearest concept the table can
    form, in POE's three levels (its D25: ±0.5 of each signal's unit). Three
    are approximations, since POE's rules use forms the table lacks:
    VolatilityShock (median and spread over 90 days; here a z-score over 13
    weeks), EquityRiskOn (unemployment against its 12-month mean; here its
    change over 26 weeks) and AIRiskOn (a 13-week return against the past
    year's; here the 13-week change, cut at ±4%)."""
    ln = math.log
    return (
        _poe("T10Y2Y", Reproduction.LEVEL, None, (-0.15, 0.15)),                 # YieldCurveInverted
        _poe("CPIAUCSL", Reproduction.CHANGE, 52, (ln(1.03125), ln(1.03875))),   # InflationShock
        _poe("WALCL", Reproduction.CHANGE, 13, (ln(0.999), ln(1.001))),          # LiquidityStress
        _poe("BAA10Y", Reproduction.ZSCORE, 52, (-0.5, 0.5)),                    # CreditSpreadStress
        _poe("VIXCLS", Reproduction.ZSCORE, 13, (-0.5, 0.5)),                    # VolatilityShock
        _poe("DEXUSEU", Reproduction.ZSCORE, 52, (-0.5, 0.5)),                   # DollarStrength
        _poe("UNRATE", Reproduction.CHANGE, 26, (-0.15, 0.15)),                  # EquityRiskOn
        _poe("NASDAQCOM", Reproduction.CHANGE, 13, (ln(0.96), ln(1.04))),        # AIRiskOn
    )
