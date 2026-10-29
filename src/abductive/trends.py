"""
Trends (ART-PLAN §10): the press's claims grouped by idea, year by year,
and followed across years.

Every year the last three years' claims (as idea vectors, proper names
removed) are grouped by spherical k-means; a claim takes its group from
its own year's grouping, so nothing written later shapes it. A group is a
trend if many writers make its claims about many subjects. One year's
group continues the last year's when each is the other's best match by the
claims both groupings share.
"""
from __future__ import annotations

import math
import re
from collections import Counter
from typing import Hashable, Mapping, Sequence

import numpy as np

LEAST = 10            # writers, and subjects, for a group to be broad
_CHUNK = 8192         # rows scored at once, to bound memory


def _nearest(X: np.ndarray, centres: np.ndarray) -> np.ndarray:
    return np.concatenate([np.argmax(X[i:i + _CHUNK] @ centres.T, axis=1) for i in range(0, len(X), _CHUNK)])


def kmeans(X: np.ndarray, k: int, rng: np.random.Generator, iters: int = 25) -> tuple[np.ndarray, np.ndarray]:
    """Spherical k-means on unit rows, seeded by k-means++ on cosine
    distance. Returns unit centres and each row's group."""
    n = len(X)
    k = min(k, n)
    centres = np.empty((k, X.shape[1]), np.float32)
    centres[0] = X[rng.integers(n)]
    d = np.maximum(1 - X @ centres[0], 0)
    for j in range(1, k):
        total = d.sum()
        centres[j] = X[rng.choice(n, p=d / total) if total > 0 else rng.integers(n)]
        d = np.minimum(d, np.maximum(1 - X @ centres[j], 0))
    labels = _nearest(X, centres)
    for _ in range(iters):
        sums = np.zeros_like(centres)
        np.add.at(sums, labels, X)
        norms = np.linalg.norm(sums, axis=1)
        kept = norms > 0                       # an emptied group keeps its centre
        centres[kept] = sums[kept] / norms[kept, None]
        new = _nearest(X, centres)
        if np.array_equal(new, labels):
            break
        labels = new
    return centres, labels


def broad_groups(labels: np.ndarray, writers: Sequence[str], subjects: Sequence[str], least: int = LEAST) -> set[int]:
    """Groups whose claims come from at least LEAST writers about at least
    LEAST subjects."""
    w: dict[int, set] = {}
    s: dict[int, set] = {}
    for g, wr, su in zip(labels.tolist(), writers, subjects):
        w.setdefault(g, set()).add(wr)
        s.setdefault(g, set()).add(su)
    return {g for g in w if len(w[g]) >= least and len(s[g]) >= least}


def choose_k(X: np.ndarray, writers: Sequence[str], subjects: Sequence[str], rng: np.random.Generator,
             start: int = 50, least: int = LEAST) -> tuple[int, np.ndarray]:
    """The k giving the most broad groups, doubling from START until the
    count falls (or k passes the number of claims)."""
    best_k, best_labels, best_n = 0, None, -1
    k = start
    while k <= len(X):
        _, labels = kmeans(X, k, rng)
        n = len(broad_groups(labels, writers, subjects, least))
        if n < best_n:
            break
        if n > best_n:
            best_k, best_labels, best_n = k, labels, n
        k *= 2
    return best_k, best_labels


def follow(before: Mapping[Hashable, set], after: Mapping[Hashable, set]) -> dict:
    """Which group of BEFORE each group of AFTER continues: each the other's
    best match by shared claims (ties to the first), and the match holding at
    least half of the after-group's claims that BEFORE also grouped."""
    seen = set().union(*before.values()) if before else set()
    shared = {(b, a): len(bm & am) for b, bm in after.items() for a, am in before.items() if bm & am}
    best_of_after: dict = {}
    best_of_before: dict = {}
    for (b, a), n in shared.items():
        if n > shared.get((b, best_of_after.get(b)), 0):
            best_of_after[b] = a
        if n > shared.get((best_of_before.get(a), a), 0):
            best_of_before[a] = b
    return {b: a for b, a in best_of_after.items()
            if best_of_before.get(a) == b and 2 * shared[(b, a)] >= len(after[b] & seen)}


_TOKEN = re.compile(r"[a-z][a-z'-]+")


def distinctive_words(texts: Mapping[Hashable, Sequence[str]], top: int = 10, min_count: int = 1) -> dict:
    """Each group's words ranked by count in the group times how rare they
    are overall (log of all words over the word's count)."""
    counts = {g: Counter(w for t in ts for w in _TOKEN.findall(t.lower())) for g, ts in texts.items()}
    overall = sum(counts.values(), Counter())
    total = sum(overall.values())

    def rank(c: Counter) -> list[str]:
        scored = [(-n * math.log(total / overall[w]), w) for w, n in c.items() if n >= min_count]
        return [w for _, w in sorted(scored)[:top]]
    return {g: rank(c) for g, c in counts.items()}


def moving(shares: Sequence[float]) -> bool:
    """A trend whose share of the conversation at some point doubled or
    halved; otherwise it is background."""
    return max(shares) >= 2 * min(shares)
