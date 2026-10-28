"""ART-PLAN §9: the engine on cases. Concepts (fine own past; contested,
both papers, modality), or artists from a records file written by POE
(evals/artist_records.py).

    uv run python -m evals.run_case_engine concepts
    uv run python -m evals.run_case_engine artists --records FILE"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from abductive.art_series import load_claims
from abductive.case_engine import CaseEngine
from abductive.cases import Record, concept_years

ROOT = Path.home() / "Documents" / "art-press-texts"


def _concepts():
    founded = {json.loads(l)["id"]: json.loads(l)["founded"] for l in (ROOT / "concepts" / "concepts.jsonl").read_text().splitlines()}
    return concept_years(load_claims(ROOT), founded, last_year=2025, fine=True), ("contested", "both_papers", "modality")


def _artists(path: Path):
    data = json.loads(path.read_text())
    return [Record(r["year"], tuple(r["own"]), r["features"], r["outcome"], r["case"]) for r in data["records"]], tuple(data["pool"])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("cases", choices=["concepts", "artists"])
    parser.add_argument("--records", type=Path)
    args = parser.parse_args()
    records, pool = _concepts() if args.cases == "concepts" else _artists(args.records)
    by_year = defaultdict(list)
    for r in records:
        by_year[r.year].append(r)
    engine, total = CaseEngine(pool), [0.0, 0.0]
    for i, y in enumerate(sorted(by_year)):
        e, o = engine.step(y, by_year[y])
        if i > 0:
            total[0] += e
            total[1] += o
            print(f"{y}: leader {engine.leader or '(own past)'}; engine - own {e - o:+.1f}", flush=True)
    print(f"engine - own past over all scored years: {total[0] - total[1]:+.1f} nats")
    print("shifts:", [(s.year, s.frm, s.to) for s in engine.shifts])


if __name__ == "__main__":
    main()
