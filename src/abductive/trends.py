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


def kmeans(X: np.ndarray, k: int, rng: np.random.Generator, iters: int = 25,
           init: np.ndarray | None = None) -> tuple[np.ndarray, np.ndarray]:
    """Spherical k-means on unit rows. Starts from INIT's first k centres
    (last year's, ART-PLAN §10.2), the rest seeded by k-means++ on cosine
    distance. Returns unit centres and each row's group."""
    n = len(X)
    k = min(k, n)
    centres = np.empty((k, X.shape[1]), np.float32)
    given = 0 if init is None else min(k, len(init))
    if given:
        centres[:given] = init[:given]
        d = np.maximum(1 - np.concatenate([np.max(X[i:i + _CHUNK] @ centres[:given].T, axis=1)
                                           for i in range(0, n, _CHUNK)]), 0)
    else:
        centres[0] = X[rng.integers(n)]
        d = np.maximum(1 - X @ centres[0], 0)
        given = 1
    for j in range(given, k):
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


def broad_groups(labels: np.ndarray, writers: Sequence[str], subjects: Sequence[str], least: int = LEAST,
                 least_writers: int | None = None) -> set[int]:
    """Groups whose claims come from at least LEAST_WRITERS (default LEAST)
    writers about at least LEAST subjects."""
    least_writers = least if least_writers is None else least_writers
    w: dict[int, set] = {}
    s: dict[int, set] = {}
    for g, wr, su in zip(labels.tolist(), writers, subjects):
        w.setdefault(g, set()).add(wr)
        s.setdefault(g, set()).add(su)
    return {g for g in w if len(w[g]) >= least_writers and len(s[g]) >= least}


def choose_k(X: np.ndarray, writers: Sequence[str], subjects: Sequence[str], rng: np.random.Generator,
             start: int = 50, least: int = LEAST, least_writers: int | None = None,
             init: np.ndarray | None = None) -> tuple[int, np.ndarray, np.ndarray]:
    """The k giving the most broad groups, doubling from START until the
    count falls (or k passes the number of claims). INIT: centres to start
    from, most important first. Returns k, its centres and labels."""
    best = (0, None, None)
    best_n = -1
    k = start
    while k <= len(X):
        centres, labels = kmeans(X, k, rng, init=init)
        n = len(broad_groups(labels, writers, subjects, least, least_writers))
        if n < best_n:
            break
        if n > best_n:
            best, best_n = (k, centres, labels), n
        k *= 2
    return best


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
    """Each group's words ranked by class TF-IDF: the word's share of the
    group's words times log(1 + average words per group / the word's count
    overall), so words common everywhere ("the", "exhibition") sink."""
    counts = {g: Counter(w for t in ts for w in _TOKEN.findall(t.lower())) for g, ts in texts.items()}
    overall = sum(counts.values(), Counter())
    average = sum(overall.values()) / max(len(counts), 1)

    def rank(c: Counter) -> list[str]:
        size = sum(c.values())
        scored = [(-(n / size) * math.log(1 + average / overall[w]), w) for w, n in c.items() if n >= min_count]
        return [w for _, w in sorted(scored)[:top]]
    return {g: rank(c) for g, c in counts.items()}


def moving(shares: Sequence[float]) -> bool:
    """A trend whose share of the conversation at some point doubled or
    halved; otherwise it is background."""
    return max(shares) >= 2 * min(shares)
