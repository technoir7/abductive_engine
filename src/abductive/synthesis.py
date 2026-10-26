"""
Concepts formed from the press's claims, in the order they were published
(ART-PLAN §4). Each claim, as a vector of its meaning (embed.py), joins the
live concept it is nearest, if its cosine with the concept's centre is at
least THETA and with the claim that founded it at least ANCHOR, or founds a
new concept. Nothing later can shape an earlier
concept. A concept nobody has asserted for DORMANT_MONTHS stops taking
claims, as talk is read against two years (POE art plan §5); it keeps what
it gathered.

THETA is fixed on the pilot month (March 2015's Guardian), never scored:
0.85 gave the most concepts held by two or more writers (54 of 634).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Hashable, Sequence

import numpy as np

THETA = 0.85
DORMANT_MONTHS = 24
# A claim must also be this near the claim that founded the concept, or the
# centre drifts and a few concepts become catch-alls. Chosen on the claims
# read by 2026-10-26 (2000–2007) by the same rule as THETA, the most
# concepts held by two or more writers (2,941 against 2,041 without it; the
# ten largest then hold 5.5% of claims, not 11%), never on prediction.
ANCHOR = 0.80


@dataclass
class Concept:
    founded: int
    last: int
    members: list[Hashable] = field(default_factory=list)
    writers: set[str] = field(default_factory=set)


class _Rows:
    """A matrix that grows a row at a time without copying on every row."""

    def __init__(self, width: int) -> None:
        self._data = np.zeros((64, width), np.float32)
        self.n = 0

    def append(self, row: np.ndarray) -> int:
        if self.n == len(self._data):
            self._data = np.vstack([self._data, np.zeros_like(self._data)])
        self._data[self.n] = row
        self.n += 1
        return self.n - 1

    @property
    def view(self) -> np.ndarray:
        return self._data[:self.n]

    def __setitem__(self, i: int, row: np.ndarray) -> None:
        self._data[i] = row


class Synthesis:
    def __init__(self, theta: float = THETA, dormant_months: int = DORMANT_MONTHS,
                 anchor: float | None = ANCHOR) -> None:
        self.theta, self.dormant, self.anchor = theta, dormant_months, anchor
        self.concepts: list[Concept] = []
        self._sums: _Rows | None = None           # sized by the first claim
        self._month: int | None = None
        self._live: list[int] = []                # concept index of each row of _live_centres
        self._live_centres: _Rows | None = None
        self._founders: _Rows | None = None       # each concept's founding claim
        self._live_founders: _Rows | None = None

    def _new_month(self, month: int, width: int) -> None:
        """Rebuild the live concepts once a month, not once a claim."""
        self._month = month
        self._live = [j for j, c in enumerate(self.concepts) if month - c.last <= self.dormant]
        self._live_centres, self._live_founders = _Rows(width), _Rows(width)
        for j in self._live:
            row = self._sums.view[j]
            self._live_centres.append(row / np.linalg.norm(row))
            self._live_founders.append(self._founders.view[j])

    def take(self, month: int, vector: Sequence[float], member: Hashable, writer: str) -> int:
        """Place one claim, made in MONTH (an index, never decreasing), and return its concept."""
        v = np.asarray(vector, np.float32)
        if self._sums is None:
            self._sums, self._founders = _Rows(v.shape[0]), _Rows(v.shape[0])
        if month != self._month:
            self._new_month(month, v.shape[0])
        j, row = -1, -1
        if self._live:
            sims = self._live_centres.view @ v
            if self.anchor is not None:
                sims = np.where(self._live_founders.view @ v >= self.anchor, sims, -np.inf)
            best = int(sims.argmax())
            if sims[best] >= self.theta:
                j, row = self._live[best], best
        if j < 0:
            j = self._sums.append(v)
            self._founders.append(v)
            self.concepts.append(Concept(founded=month, last=month))
            self._live.append(j)
            self._live_centres.append(v)
            self._live_founders.append(v)
        else:
            self._sums[j] = self._sums.view[j] + v
            total = self._sums.view[j]
            self._live_centres[row] = total / np.linalg.norm(total)
        c = self.concepts[j]
        c.last = month
        c.members.append(member)
        c.writers.add(writer)
        return j


def _month_index(stem: str) -> int:
    y, m = map(int, stem.split("-"))
    return (y - 2000) * 12 + m - 1


def _month_name(i: int) -> str:
    return f"{2000 + i // 12}-{i % 12 + 1:02d}"


def synthesise(root, theta: float = THETA, dormant_months: int = DORMANT_MONTHS, dims: int = 256) -> list[Concept]:
    """Form concepts from every embedded month of both papers, in order of
    publication month, and write ROOT/concepts/concepts.jsonl. A claim's
    writer is its article's byline, else who the reader said asserted it."""
    import json
    from pathlib import Path

    from .embed import read_vectors
    from .press import read_month
    root = Path(root)
    months = sorted({p.name.removesuffix(".keys.jsonl") for p in (root / "vectors").glob("*/*.keys.jsonl")})
    s = Synthesis(theta, dormant_months)
    for stem in months:
        y, m = map(int, stem.split("-"))
        for paper in ("guardian", "nyt"):
            if not (root / "vectors" / paper / f"{stem}.keys.jsonl").exists():
                continue
            keys, vectors = read_vectors(root, paper, y, m, dims)
            bylines = {t.id: t.byline for t in read_month(root, paper, y, m) or []}
            claims = {r["id"]: r["assertions"] for r in map(json.loads, (root / "grounded" / paper / f"{stem}.jsonl")
                                                               .read_text().splitlines())}
            for (article, i), v in zip(keys, vectors):
                writer = bylines.get(article) or claims[article][i]["who"]
                s.take(_month_index(stem), v, (paper, article, i), writer)
    out = root / "concepts" / "concepts.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("".join(json.dumps({"id": j, "founded": _month_name(c.founded), "last": _month_name(c.last),
                                       "writers": sorted(c.writers), "members": [list(x) for x in c.members]}) + "\n"
                           for j, c in enumerate(s.concepts)))
    return s.concepts


if __name__ == "__main__":
    import argparse
    from pathlib import Path
    parser = argparse.ArgumentParser(description="Form concepts from the embedded claims.")
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    concepts = synthesise(args.root)
    shared = sum(1 for c in concepts if len(c.writers) >= 2)
    print(f"{len(concepts)} concepts, {shared} held by two or more writers")
