"""Trends from the idea vectors (ART-PLAN §10, steps 2–6).

    uv run python -m evals.build_trends

Writes ROOT/trends/trends.jsonl (one row per trend: start, years, shares,
distinctive words, moving, sample claims) and ROOT/trends/claims.jsonl
(each claim's trend, month, writer, paper, force, stance), and prints each
year's k and broad groups.
"""
from __future__ import annotations

import json
import random
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

from abductive.embed import read_vectors
from abductive.names import proper_names, without_names
from abductive.press import read_month
from abductive.trends import _nearest, broad_groups, choose_k, distinctive_words, follow, moving

ROOT = Path.home() / "Documents" / "art-press-texts"
FIRST, LAST = 2000, 2026
SPAN = 3                 # years in each grouping
LEAST_WRITERS = 36       # three a quarter on average over SPAN years (ART-PLAN §10, deviation 1)
LEAST_SUBJECTS = 10
START_K = 25
SAMPLES = 15


def load(root: Path):
    """Every embedded claim: its metadata and idea vector, in month order."""
    sources = sorted((root / "grounded").glob("*/*.jsonl"))
    rows = {p: [json.loads(line) for line in p.read_text().splitlines()] for p in sources}
    names = proper_names(f for rs in rows.values() for r in rs for a in r["assertions"] for f in (a["about"], a["asserts"]))
    meta, vectors = [], []
    for p in sorted(sources, key=lambda p: (p.stem, p.parent.name)):
        paper, stem = p.parent.name, p.stem
        y, m = map(int, stem.split("-"))
        if not (root / "ideas" / paper / f"{stem}.keys.jsonl").exists():
            raise FileNotFoundError(f"{paper} {stem} has no idea vectors: run abductive.embed --ideas")
        keys, vecs = read_vectors(root, paper, y, m, out="ideas")
        bylines = {t.id: t.byline for t in read_month(root, paper, y, m) or []}
        claims = {r["id"]: r["assertions"] for r in rows[p]}
        for (article, i), v in zip(keys, vecs):
            a = claims[article][i]
            meta.append({"paper": paper, "article": article, "i": i, "month": stem, "year": y,
                         "writer": bylines.get(article) or a["who"], "subject": a["about"].strip().lower(),
                         "force": a["force"], "stance": a["stance"], "about": a["about"], "asserts": a["asserts"],
                         "idea": f"{without_names(a['about'], names)} {without_names(a['asserts'], names)}"})
            vectors.append(v)
    return meta, np.asarray(vectors, np.float32)


def group_years(meta, X):
    """Each year's grouping of its last SPAN years, started from last year's
    centres (those this year's claims are nearest to most, first); returns
    per year the claims grouped, their labels and the broad groups."""
    years = np.array([m["year"] for m in meta])
    out, centres = {}, None
    for y in range(FIRST, LAST + 1):
        idx = np.flatnonzero((years >= y - SPAN + 1) & (years <= y))
        writers = [meta[i]["writer"] for i in idx]
        subjects = [meta[i]["subject"] for i in idx]
        init = None
        if centres is not None:
            pull = np.bincount(_nearest(X[idx], centres), minlength=len(centres))
            init = centres[np.argsort(-pull, kind="stable")]
        k, centres, labels = choose_k(X[idx], writers, subjects, np.random.default_rng(y), start=START_K,
                                      least=LEAST_SUBJECTS, least_writers=LEAST_WRITERS, init=init)
        broad = broad_groups(labels, writers, subjects, LEAST_SUBJECTS, LEAST_WRITERS)
        out[y] = (idx, labels, broad)
        print(f"{y}: {len(idx)} claims, k={k}, {len(broad)} broad groups", flush=True)
    return out


def chains(grouped):
    """Each year's group -> trend id, following groups across years."""
    trend: dict[int, dict[int, int]] = {}
    next_id = 0
    for y in sorted(grouped):
        idx, labels, _ = grouped[y]
        after = defaultdict(set)
        for i, g in zip(idx.tolist(), labels.tolist()):
            after[g].add(i)
        cont = {}
        if y - 1 in grouped:
            pidx, plabels, _ = grouped[y - 1]
            before = defaultdict(set)
            overlap = set(idx.tolist())
            for i, g in zip(pidx.tolist(), plabels.tolist()):
                if i in overlap:
                    before[g].add(i)
            cont = follow(before, after)
        trend[y] = {}
        for g in after:
            if g in cont:
                trend[y][g] = trend[y - 1][cont[g]]
            else:
                trend[y][g], next_id = next_id, next_id + 1
    return trend


def main() -> None:
    out_dir = ROOT / "trends"
    out_dir.mkdir(parents=True, exist_ok=True)
    meta, X = load(ROOT)
    print(f"{len(meta)} claims", flush=True)
    grouped = group_years(meta, X)
    trend = chains(grouped)

    of_claim = {}
    start: dict[int, int] = {}
    for y, (idx, labels, broad) in grouped.items():
        for i, g in zip(idx.tolist(), labels.tolist()):
            if meta[i]["year"] == y:
                of_claim[i] = trend[y][g]
        for g in broad:
            start.setdefault(trend[y][g], y)
    with open(out_dir / "claims.jsonl", "w") as f:
        for i, m in enumerate(meta):
            f.write(json.dumps({"trend": of_claim[i], "start": start.get(of_claim[i]), **{k: m[k] for k in ("paper", "article", "i", "month", "writer",
                                                                            "force", "stance")}}) + "\n")
    writers_in = defaultdict(set)
    year_writers = defaultdict(set)
    members = defaultdict(list)
    for i, t in of_claim.items():
        m = meta[i]
        writers_in[(t, m["year"])].add(m["writer"])
        year_writers[m["year"]].add(m["writer"])
        members[t].append(i)
    words = distinctive_words({t: [meta[i]["idea"] for i in ms] for t, ms in members.items()}, top=10, min_count=3)
    rng = random.Random(0)
    with open(out_dir / "trends.jsonl", "w") as f:
        for t, y0 in sorted(start.items(), key=lambda kv: kv[0]):
            last = max(meta[i]["year"] for i in members[t])
            shares = {y: len(writers_in[(t, y)]) / len(year_writers[y]) for y in range(y0, last + 1)}
            sample = rng.sample(members[t], min(SAMPLES, len(members[t])))
            f.write(json.dumps({
                "id": t, "start": y0, "last": last, "claims": len(members[t]),
                "writers": len({meta[i]["writer"] for i in members[t]}),
                "shares": {str(y): round(s, 5) for y, s in shares.items()},
                "moving": moving(list(shares.values())), "words": words[t],
                "sample": [f"{meta[i]['month']} {meta[i]['about']}: {meta[i]['asserts']}" for i in sample],
            }) + "\n")
    moving_n = sum(1 for line in open(out_dir / "trends.jsonl") if json.loads(line)["moving"])
    print(f"{len(start)} trends, {moving_n} moving; claims in trends: "
          f"{sum(1 for t in of_claim.values() if t in start)} of {len(meta)}")


if __name__ == "__main__":
    main()
