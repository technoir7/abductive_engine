"""
Each concept's degrees by quarter (ART-PLAN §4): how many different writers
asserted it (quantity) and how many of its judgements approve or disapprove
(quality). A writer counts once a quarter however often they repeat
themselves. The random control deals the same claims into concepts of the
same sizes at random, each claim keeping its time and writer: if concepts
formed by meaning do no better than these, grouping by meaning added
nothing.
"""
from __future__ import annotations

import random
from dataclasses import dataclass, replace


@dataclass(frozen=True)
class Claim:
    concept: int
    month: str        # YYYY-MM
    writer: str
    force: str
    stance: str


def quarter(month: str) -> int:
    """Quarters since January 2000."""
    y, m = map(int, month.split("-"))
    return (y - 2000) * 4 + (m - 1) // 3


def degrees(claims: list[Claim]) -> dict[int, dict[int, dict[str, int]]]:
    """Concept -> quarter -> {"writers", "approval", "disapproval"}."""
    writers: dict[tuple[int, int], set[str]] = {}
    out: dict[int, dict[int, dict[str, int]]] = {}
    for c in claims:
        q = quarter(c.month)
        cell = out.setdefault(c.concept, {}).setdefault(q, {"writers": 0, "approval": 0, "disapproval": 0})
        seen = writers.setdefault((c.concept, q), set())
        if c.writer not in seen:
            seen.add(c.writer)
            cell["writers"] += 1
        if c.force == "judges" and c.stance in ("approval", "disapproval"):
            cell[c.stance] += 1
    return out


def shuffled_concepts(claims: list[Claim], rng: random.Random) -> list[Claim]:
    labels = [c.concept for c in claims]
    rng.shuffle(labels)
    return [replace(c, concept=label) for c, label in zip(claims, labels)]


def select(claims: list[Claim], min_writers: int = 5, min_quarters: int = 8) -> list[int]:
    """Concepts held by at least MIN_WRITERS different writers in at least
    MIN_QUARTERS different quarters (the art replay's rule)."""
    writers: dict[int, set[str]] = {}
    quarters: dict[int, set[int]] = {}
    for c in claims:
        writers.setdefault(c.concept, set()).add(c.writer)
        quarters.setdefault(c.concept, set()).add(quarter(c.month))
    return sorted(k for k in writers if len(writers[k]) >= min_writers and len(quarters[k]) >= min_quarters)


DORMANT_QUARTERS = 8   # as synthesis.DORMANT_MONTHS


def periods(deg: dict[int, dict[int, dict[str, int]]], chosen: list[int], first: int, last: int):
    """The engine's periods, one a quarter from FIRST+1 to LAST: each chosen
    concept's writers that quarter and its change, while the concept exists,
    from the quarter it was founded until DORMANT_QUARTERS after it was last
    asserted. Before or after, it is not observed: a concept not yet formed
    is not a concept no one is talking about."""
    import calendar
    from datetime import date

    from .weeks import Week
    def writers(k: int, q: int) -> float:
        return float(deg.get(k, {}).get(q, {}).get("writers", 0))

    def alive(k: int, q: int) -> bool:
        asserted = [x for x in deg.get(k, {}) if x <= q]
        return bool(asserted) and q - max(asserted) <= DORMANT_QUARTERS

    out = []
    for q in range(first + 1, last + 1):
        y, m = 2000 + q // 4, (q % 4) * 3 + 3
        live = [k for k in chosen if alive(k, q)]
        level = {f"c{k}": writers(k, q) for k in live}
        changes = {f"c{k}": writers(k, q) - writers(k, q - 1) for k in live}
        out.append(Week(date(y, m, calendar.monthrange(y, m)[1]), changes, level))
    return out


def load_claims(root) -> list[Claim]:
    """Every claim with its concept (concepts/concepts.jsonl), month, writer
    (the byline, else who asserted it), force and stance."""
    import json
    from pathlib import Path

    from .press import read_month
    root = Path(root)
    concept_of: dict[tuple, int] = {}
    for line in (root / "concepts" / "concepts.jsonl").read_text().splitlines():
        row = json.loads(line)
        for paper, article, i in row["members"]:
            concept_of[(paper, article, i)] = row["id"]
    out = []
    for path in sorted((root / "grounded").glob("*/*.jsonl")):
        paper, stem = path.parent.name, path.stem
        y, m = map(int, stem.split("-"))
        bylines = {t.id: t.byline for t in read_month(root, paper, y, m) or []}
        for line in path.read_text().splitlines():
            row = json.loads(line)
            for i, a in enumerate(row["assertions"]):
                k = concept_of.get((paper, row["id"], i))
                if k is not None:
                    out.append(Claim(k, stem, bylines.get(row["id"]) or a["who"], a["force"], a["stance"]))
    return out
