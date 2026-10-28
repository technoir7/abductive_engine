"""Test 3 of ART-PLAN §8: concepts alive at the end of 2025 forecast for
2026 (January-September, all that exists) from 2000-2024 only.

    uv run python -m evals.forecast_2026"""
from __future__ import annotations

import json
import math
import random
from collections import Counter
from pathlib import Path

from abductive.art_series import load_claims
from abductive.cases import concept_years, dealt, forecast, judge

ROOT = Path.home() / "Documents" / "art-press-texts"
YEAR = 2025          # the state year; its outcome is 2026


def _labels(ids: set[int]) -> dict[int, tuple[int, str]]:
    """Each concept's size and the 'about' of its most common subject."""
    members = {}
    for line in (ROOT / "concepts" / "concepts.jsonl").read_text().splitlines():
        row = json.loads(line)
        if row["id"] in ids:
            members[row["id"]] = {(p, a, i) for p, a, i in row["members"]}
    abouts = {k: Counter() for k in ids}
    wanted = {(p, a) for m in members.values() for p, a, _ in m}
    for path in sorted((ROOT / "grounded").glob("*/*.jsonl")):
        for line in path.read_text().splitlines():
            row = json.loads(line)
            if (path.parent.name, row["id"]) not in wanted:
                continue
            for i, s in enumerate(row["assertions"]):
                for k, m in members.items():
                    if (path.parent.name, row["id"], i) in m:
                        abouts[k][s["about"]] += 1
    return {k: (len(members[k]), abouts[k].most_common(1)[0][0] if abouts[k] else "?") for k in ids}


def main() -> None:
    founded = {json.loads(l)["id"]: json.loads(l)["founded"] for l in (ROOT / "concepts" / "concepts.jsonl").read_text().splitlines()}
    records = concept_years(load_claims(ROOT), founded, last_year=2026, fine=True)
    n = sum(r.year == YEAR for r in records)
    real = judge(records, "contested").by_year[YEAR] * n
    deals = [judge(dealt(records, "contested", random.Random(s)), "contested").by_year[YEAR] * n for s in range(20)]
    print(f"{n} concepts alive at the end of 2025; contested's gain on 2026: {real:.1f} nats; "
          f"deals max {max(deals):.1f} mean {sum(deals) / 20:.1f}")
    rows = forecast(records, "contested", YEAR)
    outcome = {r.case: r.outcome for r in records if r.year == YEAR}
    log_own = sum(math.log(po[outcome[c]]) for c, po, _ in rows)
    log_with = sum(math.log(pw[outcome[c]]) for c, _, pw in rows)
    print(f"log score: own past {log_own:.1f}, with contested {log_with:.1f}")
    top = sorted(rows, key=lambda t: -t[2][2])[:15]
    labels = _labels({c for c, _, _ in top})
    print("Most likely to be taken up by several writers in 2026 (chance; outcome Jan-Sep 2026):")
    for c, _, pw in top:
        size, about = labels[c]
        print(f"  {pw[2]:.0%}  c{c} ({size} claims) {about[:70]!r}: {['none', 'one', 'several'][outcome[c]]}")
    hit = Counter((pw[2] > 0.5, outcome[c] == 2) for c, _, pw in rows)
    print(f"forecast several (>50%): {hit[(True, True)]} came true, {hit[(True, False)]} did not; "
          f"not forecast but several: {hit[(False, True)]}")


if __name__ == "__main__":
    main()
