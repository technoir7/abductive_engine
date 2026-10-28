"""Concepts as cases for POE's art domain (POE REFACTOR_SPEC D29): each
concept-year with its own past graded finely, its features and next year's
writers; 2025 is the open year (2026 is not over). POE's
evals/concept_snapshot.py turns the file into the domain's snapshot.

    uv run python -m evals.export_concepts OUT.json"""
from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path

from abductive.art_series import load_claims
from abductive.cases import concept_labels, concept_years

ROOT = Path.home() / "Documents" / "art-press-texts"
OPEN = 2025
POOL = ("contested", "both_papers", "modality")


def main() -> None:
    founded = {json.loads(l)["id"]: json.loads(l)["founded"] for l in (ROOT / "concepts" / "concepts.jsonl").read_text().splitlines()}
    claims = load_claims(ROOT)
    records, rows = concept_years(claims, founded, last_year=OPEN + 1, fine=True), []
    for r in records:
        row = asdict(r)
        row["case"] = str(r.case)
        if r.year == OPEN:
            row["outcome"] = None
        rows.append(row)
    names = concept_labels(claims)
    labels = {str(r.case): names[r.case] for r in records if r.year == OPEN and r.case in names}
    Path(sys.argv[1]).write_text(json.dumps({"pool": POOL, "records": rows, "labels": labels}))
    print(f"{len(rows)} concept-years, {len(labels)} open -> {sys.argv[1]}")


if __name__ == "__main__":
    main()
