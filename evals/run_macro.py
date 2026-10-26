"""Run a population over macro's history and report what it came to.

    uv run python -m evals.run_macro [seed programmes...]

Learned from 2000, scored from 2003-04-04 (DESIGN §9)."""
from __future__ import annotations

import sys
import time
from datetime import date
from pathlib import Path

from abductive import macro
from abductive.baselines import Persistence
from abductive.observations import read_csv
from abductive.population import Population
from abductive.scheme import Scheme
from abductive.weeks import weeks as make_weeks

DATA = Path(__file__).parent.parent / "data" / "observations.csv"


def main(names: list[str]) -> None:
    w = make_weeks(read_csv(DATA), macro.fridays(date(2000, 1, 7)), macro.SERIES)
    vocab = {"persistence": (), "POE": macro.poe_vocabulary()}
    pop = Population([(n, Scheme(vocab[n], frozenset(), macro.SERIES)) for n in names])
    base, t0, engine, persistence = Persistence(), time.time(), [], []
    for week in w:
        e, p = pop.step(week), sum(base.score_and_learn(week).values())
        if week.friday >= macro.FIRST:
            engine.append(e), persistence.append(p)
    n = len(engine)
    print(f"{n} weeks in {time.time() - t0:.0f}s: engine {sum(engine) / n:.3f}, persistence {sum(persistence) / n:.3f} nats/week")
    print("leader:", pop.leader.name)
    for m in pop.members:
        print(f"  alive since {m.born}: {m.name}")
    print(len(pop.shifts), "shifts;", sum(s.conceptual for s in pop.shifts), "conceptual")
    for s in pop.shifts[-12:]:
        print(f"  {s.friday} {'CONCEPTUAL ' if s.conceptual else ''}{s.from_name}  →  {s.to_name}")


if __name__ == "__main__":
    main(sys.argv[1:] or ["persistence", "POE"])
