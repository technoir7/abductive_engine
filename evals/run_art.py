"""The art replay (ART-PLAN §7, step 6): concepts formed from the press,
their writers per quarter predicted by a population of schemes.

    uv run python -m evals.run_art [--shuffle SEED]

--shuffle deals the claims into concepts of the same sizes at random (the
control). Scored from 2003 Q1; learned from 2000."""
from __future__ import annotations

import argparse
import random
import time
from pathlib import Path

from abductive.art_series import degrees, load_claims, periods, select, shuffled_concepts
from abductive.baselines import Independence, Persistence
from abductive.concepts import Concept, Form, Reproduction
from abductive.population import Population
from abductive.scheme import Scheme
from abductive.weeks import Change

ROOT = Path.home() / "Documents" / "art-press-texts"
SCORED_FROM = 12          # 2003 Q1, in quarters since 2000


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--shuffle", type=int, default=None)
    parser.add_argument("--last", type=int, default=106, help="last quarter (106 = 2026 Q3)")
    args = parser.parse_args()
    claims = load_claims(ROOT)
    if args.shuffle is not None:
        claims = shuffled_concepts(claims, random.Random(args.shuffle))
    chosen = select(claims)
    deg = degrees(claims)
    quarters = periods(deg, chosen, first=0, last=args.last)
    kinds = {f"c{k}": Change.DIFFERENCE for k in chosen}
    vocab = tuple(Concept(Form((s,), Reproduction.ZSCORE, 4, (-0.5, 0.5)), occasion="art replay") for s in kinds)
    pop = Population([("persistence", Scheme((), frozenset(), kinds)), ("concepts", Scheme(vocab, frozenset(), kinds))])
    base, indep = Persistence(), Independence()
    t0, scores = time.time(), {"engine": [], "persistence": [], "independence": []}
    for i, q in enumerate(quarters, start=1):
        e = pop.step(q)
        p, n = sum(base.score_and_learn(q).values()), sum(indep.score_and_learn(q).values())
        if i >= SCORED_FROM:
            scores["engine"].append(e), scores["persistence"].append(p), scores["independence"].append(n)
    k = len(scores["engine"])
    print(f"{len(claims)} claims, {len(chosen)} series, {k} quarters scored in {time.time() - t0:.0f}s")
    print("nats a quarter: " + ", ".join(f"{name} {sum(v) / k:.2f}" for name, v in scores.items()))
    print("leader:", pop.leader.name[:300])
    print(len(pop.shifts), "shifts;", sum(s.conceptual for s in pop.shifts), "conceptual")


if __name__ == "__main__":
    main()
