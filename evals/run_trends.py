"""ART-PLAN §10.7 and checks: the case engine on trends, by quarter.

    uv run python -m evals.run_trends

Reads ROOT/trends/claims.jsonl (evals/build_trends.py). Runs the engine on
the trends, then on five random groupings (each year's claims dealt among
the trends, sizes kept) and on five deals of the leader's features among
each quarter's trends. Writes ROOT/trends/engine.json: leader, shifts,
each scheme's gain, and the open quarter's forecasts.
"""
from __future__ import annotations

import json
import random
from collections import defaultdict
from dataclasses import replace
from pathlib import Path

from abductive.art_series import Claim, quarter
from abductive.case_engine import CaseEngine
from abductive.cases import dealt, trend_quarters

ROOT = Path.home() / "Documents" / "art-press-texts"
POOL = ("contested", "both_papers", "modality")
OPEN = quarter("2026-09")
HALF_LIFE_QUARTERS = 20
DEALS = 5


def label(q: int) -> str:
    return f"{2000 + q // 4} Q{q % 4 + 1}"


def load(root: Path):
    claims, start = [], {}
    for line in (root / "trends" / "claims.jsonl").read_text().splitlines():
        r = json.loads(line)
        if r["start"] is None:
            continue
        claims.append(Claim(r["trend"], r["month"], r["writer"], r["force"], r["stance"], r["paper"]))
        start[r["trend"]] = quarter(f"{r['start']}-01")
    return claims, start


def regrouped(claims: list[Claim], seed: int) -> list[Claim]:
    """Each year's claims dealt among that year's trends at random, each
    trend keeping its number of claims that year."""
    rng = random.Random(seed)
    by_year = defaultdict(list)
    for i, c in enumerate(claims):
        by_year[c.month[:4]].append(i)
    out = list(claims)
    for idx in by_year.values():
        labels = [claims[i].concept for i in idx]
        rng.shuffle(labels)
        for i, k in zip(idx, labels):
            out[i] = replace(claims[i], concept=k)
    return out


def run(records):
    closed = defaultdict(list)
    for r in records:
        if r.outcome is not None:
            closed[r.year].append(r)
    engine = CaseEngine(POOL, half_life=HALF_LIFE_QUARTERS)
    gains = {s: 0.0 for s in engine.schemes if s}
    total, by_year = 0.0, defaultdict(float)
    for i, q in enumerate(sorted(closed)):
        scores = {s: scheme.score(closed[q]) for s, scheme in engine.schemes.items()}
        e, o = engine.step(q, closed[q])
        if i > 0:
            total += e - o
            by_year[2000 + q // 4] += e - o
            for s in gains:
                gains[s] += scores[s] - o
    return engine, total, gains, by_year


def main() -> None:
    claims, start = load(ROOT)
    records = trend_quarters(claims, start, OPEN)
    print(f"{len(start)} trends, {sum(r.outcome is not None for r in records)} trend-quarters judged")
    engine, total, gains, by_year = run(records)
    print(f"engine - own past: {total:+.1f} nats; leader {engine.leader or '(own past)'}")
    print("shifts:", [(label(s.year), s.frm, s.to) for s in engine.shifts])
    print("by year:", {y: round(g, 1) for y, g in sorted(by_year.items())})
    for s, g in sorted(gains.items(), key=lambda kv: -kv[1]):
        print(f"  {' + '.join(s):40} {g:+.1f}")

    print("random groupings (engine - own past):",
          [round(run(trend_quarters(regrouped(claims, d), start, OPEN))[1], 1) for d in range(DEALS)], flush=True)
    if engine.leader:
        deals = []
        for d in range(DEALS):
            rng, moved = random.Random(d), records
            for f in engine.leader:
                moved = dealt(moved, f, rng)
            deals.append(round(run(moved)[1], 1))
        print("leader's features dealt (engine - own past):", deals)

    own = engine.schemes[()]
    lead = engine.schemes[engine.leader]
    forecasts = [{"trend": r.case, "own": r.own, "features": r.features,
                  "own_past": own.predict(r), "with_leader": lead.predict(r)}
                 for r in records if r.outcome is None]
    (ROOT / "trends" / "engine.json").write_text(json.dumps({
        "leader": engine.leader, "shifts": [(s.year, s.frm, s.to) for s in engine.shifts], "total": total,
        "gains": {" + ".join(s): g for s, g in gains.items()}, "by_year": by_year,
        "forecast_quarter": label(OPEN + 1), "forecasts": forecasts}))


if __name__ == "__main__":
    main()
