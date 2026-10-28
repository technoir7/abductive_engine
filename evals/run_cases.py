"""Test 1 of ART-PLAN §8: the life of concepts. Each mechanism alone against
a concept's own past (writers, age), judged over every concept-year, with
20 deals of the feature among the same year's concepts as the control.

    uv run python -m evals.run_cases [--fine]

--fine grades the own past finely (test 1b): writers this year and so far
in doubling bins, with age."""
from __future__ import annotations

import argparse
import json
import random
from collections import Counter
from pathlib import Path

from abductive.art_series import load_claims
from abductive.cases import concept_years, dealt, judge

ROOT = Path.home() / "Documents" / "art-press-texts"
FEATURES = ("contested", "both_papers", "modality")
DEALS = 20


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--fine", action="store_true")
    parser.add_argument("--backoff", action="store_true", help="test 4: split cells start from the own-past cell")
    args = parser.parse_args()
    founded = {}
    for line in (ROOT / "concepts" / "concepts.jsonl").read_text().splitlines():
        row = json.loads(line)
        founded[row["id"]] = row["founded"]
    records = concept_years(load_claims(ROOT), founded, last_year=2025, fine=args.fine)
    print(f"{len(founded)} concepts, {len(records)} concept-years", flush=True)
    for f in FEATURES:
        real = judge(records, f, backoff=args.backoff)
        deals = [judge(dealt(records, f, random.Random(s)), f, backoff=args.backoff).gain for s in range(DEALS)]
        print(f"{f:<12} gain {real.gain:8.1f} nats over {real.cases}; deals max {max(deals):.1f} "
              f"mean {sum(deals) / len(deals):.1f}; above all deals: {real.gain > max(deals)}", flush=True)
        rates = Counter((r.features[f], r.outcome) for r in records)
        for v in sorted({v for v, _ in rates}):
            n = sum(rates[(v, o)] for o in range(3))
            print(f"    {f}={v}: {n} cases; next year none {rates[(v, 0)] / n:.1%}, one {rates[(v, 1)] / n:.1%}, "
                  f"several {rates[(v, 2)] / n:.1%}", flush=True)

    if args.backoff:
        together = judge(records, FEATURES, backoff=True)
        print(f"all three together: gain {together.gain:.1f} nats; positive years "
              f"{sum(g > 0 for g in together.by_year.values())} of {len(together.by_year)}")


if __name__ == "__main__":
    main()
