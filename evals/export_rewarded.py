"""ART-PLAN §12.2: what critics rewarded in the year to September 2026,
description only. For each theme with at least 10 verdicts this year
(§11's argued-over candidates, themes whose names fit, one per name) and
for each medium (the papers' tags on the claim's article): approvals,
disapprovals and a sample of each.

    uv run python -m evals.export_rewarded OUT.json"""
from __future__ import annotations

import json
import random
import sys
from collections import defaultdict

from abductive.cases import year_to_september
from abductive.trend_lists import LEAST_WRITERS, shown
from evals.export_trends import NOW, ROOT, _claim_text, _rows, _trends, candidate_lists
from abductive.trend_lists import year_stats
from evals.export_trends import _claims

SAMPLE = 4
MEDIA = {("guardian", "artanddesign/painting"): "painting", ("guardian", "artanddesign/photography"): "photography",
         ("guardian", "artanddesign/sculpture"): "sculpture", ("guardian", "artanddesign/installation"): "installation",
         ("guardian", "artanddesign/drawing"): "drawing", ("guardian", "artanddesign/video-art"): "video",
         ("guardian", "artanddesign/ceramics"): "ceramics", ("nyt", "Photography"): "photography",
         ("nyt", "Sculpture"): "sculpture", ("nyt", "Textiles"): "textiles", ("nyt", "Ceramics and Pottery"): "ceramics"}


def _media_of_articles() -> dict:
    out = {}
    for paper in ("guardian", "nyt"):
        for path in sorted((ROOT / paper).glob(f"{NOW - 1}-1*.jsonl")) + sorted((ROOT / paper).glob(f"{NOW}-0*.jsonl")):
            for line in path.read_text().splitlines():
                a = json.loads(line)
                tags = a.get("tags", [])
                out[(paper, a["id"])] = {MEDIA[(paper, v if paper == "nyt" else k)] for k, v in tags
                                         if (paper, v if paper == "nyt" else k) in MEDIA and (paper != "nyt" or k == "subject")}
    return out


def main() -> None:
    rows = [r for r in _rows(ROOT) if 2000 + year_to_september(r["month"]) == NOW]
    names = {int(k): v for k, v in json.loads((ROOT / "trends" / "names.json").read_text()).items()}
    fit = {int(k): v for k, v in json.loads((ROOT / "trends" / "fit.json").read_text()).items()}
    stats = year_stats(_claims(_rows(ROOT)))
    broad = {k for k in _trends(ROOT) if stats.n(k, NOW) >= LEAST_WRITERS}
    themes = shown(candidate_lists(ROOT), {k: v["kind"] for k, v in names.items()}, fit,
                   {k: v["name"] for k, v in names.items()}, broad)["argued"]
    media = _media_of_articles()
    groups: dict = defaultdict(lambda: {"approval": [], "disapproval": []})
    for r in rows:
        if r["force"] != "judges" or r["stance"] not in ("approval", "disapproval"):
            continue
        if r["trend"] in themes:
            groups[("trend", names[r["trend"]]["name"])][r["stance"]].append(r)
        for m in media.get((r["paper"], r["article"]), ()):
            groups[("medium", m)][r["stance"]].append(r)
    rng = random.Random(0)
    out = []
    for (kind, name), g in groups.items():
        a, d = len(g["approval"]), len(g["disapproval"])
        if a + d < 10:
            continue
        out.append({"kind": kind, "name": name, "approvals": a, "disapprovals": d,
                    "approved": _claim_text(ROOT, rng.sample(g["approval"], min(SAMPLE, a))),
                    "disapproved": _claim_text(ROOT, rng.sample(g["disapproval"], min(SAMPLE, d)))})
    out.sort(key=lambda x: (x["kind"], -x["approvals"] / (x["approvals"] + x["disapprovals"])))
    json.dump({"year": NOW, "rewarded": out}, open(sys.argv[1], "w"), ensure_ascii=False)
    for x in out:
        print(f"{x['kind']:7} {x['name'][:40]:40} {x['approvals']:3} for {x['disapprovals']:3} against")


if __name__ == "__main__":
    main()
