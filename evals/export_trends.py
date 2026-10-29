"""Trends for POE's art domain (ART-PLAN §11): the trends as cases by years
to September (Test 10b), for POE's case engine to judge, and this year's
lists (new, growing, fading, argued over) with what POE shows of each.
POE's evals/trend_snapshot.py turns the file into the domain's snapshots.

Names come from evals/name_trends.py and their fit from
evals/check_trend_names.py, which must have judged every candidate first.

    uv run python -m evals.export_trends OUT.json"""
from __future__ import annotations

import json
import random
import sys
from collections import defaultdict
from dataclasses import asdict
from pathlib import Path

from abductive.art_series import Claim
from abductive.cases import trend_quarters, year_to_september
from abductive.trend_lists import BEFORE, LEAST_WRITERS, candidates, shown, year_stats

ROOT = Path.home() / "Documents" / "art-press-texts"
NOW = 2026               # the year to September 2026
POOL = ("contested", "both_papers", "modality")
SAMPLE = 3
FIRST_SHOWN = 2010       # shares shown from here


def _rows(root: Path) -> list[dict]:
    return [r for r in map(json.loads, (root / "trends" / "claims.jsonl").read_text().splitlines())
            if r["start"] is not None]


def _claims(rows: list[dict]) -> list[Claim]:
    return [Claim(r["trend"], r["month"], r["writer"], r["force"], r["stance"], r["paper"]) for r in rows]


def _trends(root: Path) -> dict[int, dict]:
    return {t["id"]: t for t in map(json.loads, (root / "trends" / "trends.jsonl").read_text().splitlines())}


def candidate_lists(root: Path = ROOT) -> dict[str, list[int]]:
    starts = {k: t["start"] for k, t in _trends(root).items()}
    return candidates(year_stats(_claims(_rows(root))), starts, NOW)


def _claim_text(root: Path, picks: list[dict]) -> list[str]:
    """The claims' wording (the reader's paraphrase, not the article), read
    from the grounded month files."""
    out = []
    for r in picks:
        path = root / "grounded" / r["paper"] / f"{r['month']}.jsonl"
        row = next(x for x in map(json.loads, path.read_text().splitlines()) if x["id"] == r["article"])
        a = row["assertions"][r["i"]]
        out.append(f"{a['about']}: {a['asserts']}")
    return out


def main() -> None:
    rows = _rows(ROOT)
    claims = _claims(rows)
    trends = _trends(ROOT)
    names = {int(k): v for k, v in json.loads((ROOT / "trends" / "names.json").read_text()).items()}
    stats = year_stats(claims)

    def label(k: int) -> str:
        return names[k]["name"] if k in names else " · ".join(trends[k]["words"][:3])

    start = {k: year_to_september(f"{t['start']}-01") for k, t in trends.items()}
    records = trend_quarters(claims, start, year_to_september(f"{NOW}-09"), per_year=1)
    case_rows = []
    for r in records:
        row = asdict(r)
        row["year"], row["case"] = 2000 + r.year, str(r.case)
        case_rows.append(row)
    labels = {str(r.case): label(r.case) for r in records if r.outcome is None}

    fit = {int(k): v for k, v in json.loads((ROOT / "trends" / "fit.json").read_text()).items()}
    broad = {k for k in trends if stats.n(k, NOW) >= LEAST_WRITERS}
    lists = shown(candidate_lists(ROOT), {k: v["kind"] for k, v in names.items()}, fit,
                  {k: v["name"] for k, v in names.items()}, broad)
    picked = sorted({k for ks in lists.values() for k in ks})
    this_year = defaultdict(list)
    for r in rows:
        if r["trend"] in picked and 2000 + year_to_september(r["month"]) == NOW:
            this_year[r["trend"]].append(r)
    rng = random.Random(0)
    years = list(range(FIRST_SHOWN, NOW + 1))
    shown_trends = {}
    for k in picked:
        cell = stats.cells[(k, NOW)] if (k, NOW) in stats.cells else None
        shown_trends[str(k)] = {
            "name": names[k]["name"], "start": trends[k]["start"], "words": trends[k]["words"][:6],
            "writers": [stats.n(k, y) for y in years],
            "papers": sorted(cell.papers) if cell else [],
            "verdicts": [cell.approval, cell.disapproval] if cell else [0, 0],
            "sample": _claim_text(ROOT, rng.sample(this_year[k], min(SAMPLE, len(this_year[k])))),
        }
    out = {
        "cases": {"pool": POOL, "records": case_rows, "labels": labels},
        "lists": {"year": NOW, "before": BEFORE, "years": years,
                  "all_writers": [len(stats.writers.get(y, ())) for y in years],
                  "lists": {k: [str(t) for t in ts] for k, ts in lists.items()}, "trends": shown_trends},
    }
    Path(sys.argv[1]).write_text(json.dumps(out, ensure_ascii=False))
    print(f"{len(case_rows)} trend-years, {len(labels)} open; lists "
          + ", ".join(f"{k} {len(v)}" for k, v in lists.items()) + f" -> {sys.argv[1]}")


if __name__ == "__main__":
    main()
