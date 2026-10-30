"""The trial of the life-or-work reading (ART-PLAN §15.2): one month's
claims from both papers, read in batches, with each call's cost recorded
and scaled to every grounded claim. Writes to ~/Documents/art-press-texts/life/."""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from abductive.reading import ReadingError, claude_runner
from abductive.reading_life import read_claims

ROOT = Path.home() / "Documents" / "art-press-texts"
ALL_CLAIMS = 561_133
FIRST_READING_USD = 67.88      # assertions/usage.jsonl, list price


def month_claims(month: str) -> list[dict]:
    out = []
    for paper in ("guardian", "nyt"):
        for line in (ROOT / "grounded" / paper / f"{month}.jsonl").open():
            art = json.loads(line)
            out += [{"paper": paper, "id": art["id"], "n": i, "about": a["about"], "asserts": a["asserts"],
                     "who": a["who"]} for i, a in enumerate(art["assertions"])]
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--month", default="2026-08")
    ap.add_argument("--batch", type=int, default=100)
    ap.add_argument("--effort", default=None)
    args = ap.parse_args()
    claims = month_claims(args.month)
    run = claude_runner("haiku", args.effort)
    tag = f"{args.month}_b{args.batch}_{args.effort or 'default'}"
    out, usage_path = ROOT / "life" / f"pilot_{tag}.jsonl", ROOT / "life" / f"pilot_{tag}_usage.jsonl"
    cost = tokens_out = 0.0
    failed = 0
    start = time.time()
    with out.open("w") as f, usage_path.open("w") as u:
        for i in range(0, len(claims), args.batch):
            part = claims[i:i + args.batch]
            try:
                got, usage = read_claims([(c["about"], c["asserts"]) for c in part], run)
            except ReadingError as exc:
                failed += len(part)
                print("refused:", exc)
                continue
            u.write(json.dumps(usage) + "\n")
            cost += usage.get("cost_usd") or 0
            tokens_out += usage.get("output_tokens") or 0
            for c, (subject, life) in zip(part, got):
                f.write(json.dumps(dict(c, subject=subject, life=life)) + "\n")
    read = len(claims) - failed
    scaled = cost / read * ALL_CLAIMS if read else float("nan")
    print(json.dumps({"claims": len(claims), "read": read, "refused": failed, "cost_usd": round(cost, 4),
                      "output_tokens": tokens_out, "minutes": round((time.time() - start) / 60, 1),
                      "scaled_to_all_usd": round(scaled, 2),
                      "share_of_first_reading": round(scaled / FIRST_READING_USD, 2)}))


if __name__ == "__main__":
    main()
