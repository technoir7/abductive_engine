"""ART-PLAN §11, deviation 2: does a theme's name fit this year's claims?
The local model (as evals/name_trends.py) is given the name and ten of
this year's claims (of its biggest year before, if silent this year),
drawn at random (seed 0), and says which are about it.
Writes ROOT/trends/fit.json (trend -> share that fit); keeps answers already
written.

    uv run python -m evals.check_trend_names"""
from __future__ import annotations

import json
import random
from collections import defaultdict

from abductive.cases import year_to_september
from abductive.trend_lists import BEFORE
from evals.export_trends import NOW, ROOT, _claim_text, _rows, candidate_lists
from evals.name_trends import MODEL, ask

CLAIMS = 10
PROMPT = """A group of claims from art criticism was given this name: "{name}".

Here are claims from the group:
{claims}

For each claim, in order, say whether it is about {name}. Answer with JSON only: {{"fits": [true or false for each claim]}}"""


def main() -> None:
    names = json.loads((ROOT / "trends" / "names.json").read_text())
    path = ROOT / "trends" / "fit.json"
    fit = json.loads(path.read_text()) if path.exists() else {}
    themes = sorted({t for ts in candidate_lists().values() for t in ts if names[str(t)]["kind"] == "theme"})
    by_year = defaultdict(list)
    for r in _rows(ROOT):
        y = 2000 + year_to_september(r["month"])
        if r["trend"] in themes and NOW - BEFORE <= y <= NOW:
            by_year[(r["trend"], y)].append(r)
    for k in themes:
        if str(k) in fit:
            continue
        # A trend silent this year (fading) is checked on its biggest year of the ones before.
        rows = by_year[(k, NOW)] or max((by_year[(k, y)] for y in range(NOW - BEFORE, NOW)),
                                        key=lambda rs: len({r["writer"] for r in rs}))
        claims = _claim_text(ROOT, random.Random(0).sample(rows, min(CLAIMS, len(rows))))
        out = ask(PROMPT.format(name=names[str(k)]["name"], claims="\n".join(f"{i + 1}. {c}" for i, c in enumerate(claims))))
        fits = out.get("fits")
        if not isinstance(fits, list) or len(fits) != len(claims) or not all(isinstance(f, bool) for f in fits):
            raise ValueError(f"trend {k}: bad answer {out!r}")
        fit[str(k)] = sum(fits) / len(fits)
        path.write_text(json.dumps(fit, indent=0))
        print(f"#{k} {names[str(k)]['name']}: {sum(fits)}/{len(fits)}", flush=True)


if __name__ == "__main__":
    main()
