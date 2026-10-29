"""Each trend's list status in every year to September (ART-PLAN §12.3):
new, growing, fading, argued over, by §11's rules applied to every year
and to all trends (the theme filter needs names, which only 2026's
candidates have). POE's evals/success_records.py labels each artist's
claims with them.

    uv run python -m evals.export_trend_status OUT.jsonl"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from abductive.trend_lists import BEFORE, candidates, year_stats
from evals.export_trends import ROOT, _claims, _rows, _trends

FIRST = 2000 + BEFORE      # the first year with three before it
LAST = 2026


def main() -> None:
    stats = year_stats(_claims(_rows(ROOT)))
    starts = {k: t["start"] for k, t in _trends(ROOT).items()}
    n = 0
    with open(sys.argv[1], "w") as f:
        for year in range(FIRST, LAST + 1):
            lists = candidates(stats, starts, year)
            on = {t for ts in lists.values() for t in ts}
            for t in sorted(on):
                f.write(json.dumps({"trend": t, "year": year, **{k: t in ts for k, ts in lists.items()}}) + "\n")
                n += 1
    print(f"{n} trend-years on a list, {FIRST}-{LAST} -> {sys.argv[1]}")


if __name__ == "__main__":
    main()
