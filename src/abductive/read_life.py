"""
The life-or-work reading of every grounded claim (ART-PLAN §15.2), month by
month and resumably, on the user's subscription like the first reading. Each
month's file lists, per article, each claim's [subject, life] in the order
of its grounded claims; a claim refused even alone is kept as null and
listed in failed.jsonl to read again. Months are written whole (.part, then
renamed), so a stop loses only the months in progress.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from .read_press import UsageLimit, _append, _limited, patient
from .reading import ReadingError, Runner, claude_runner
from .reading_life import read_claims

BATCH = 100      # settled on the trial: no answer refused at 100 claims


def _read(claims: list[dict], run: Runner, root: Path) -> dict[tuple[str, int], tuple[str, str]]:
    """A batch's answers by (article id, claim number); on an answer outside
    the form, its halves; a claim refused alone goes to failed.jsonl."""
    try:
        got, usage = read_claims([(c["about"], c["asserts"]) for c in claims], run)
        _append(root / "life" / "usage.jsonl", {"claims": len(claims), **usage})
        return {(c["id"], c["n"]): g for c, g in zip(claims, got)}
    except (ReadingError, subprocess.CalledProcessError, subprocess.TimeoutExpired, json.JSONDecodeError) as exc:
        if len(claims) == 1:
            c = claims[0]
            _append(root / "life" / "failed.jsonl", {"paper": c["paper"], "month": c["month"], "id": c["id"],
                                                      "n": c["n"], "error": str(exc)[:300]})
            return {}
        half = len(claims) // 2
        return _read(claims[:half], run, root) | _read(claims[half:], run, root)


def read_month_life(root: Path, paper: str, stem: str, run: Runner, batch: int = BATCH) -> int:
    """Read one month's grounded claims unless done; the number answered."""
    out = root / "life" / paper / f"{stem}.jsonl"
    if out.exists():
        return 0
    articles = [json.loads(line) for line in (root / "grounded" / paper / f"{stem}.jsonl").open()]
    claims = [{"paper": paper, "month": stem, "id": a["id"], "n": n, "about": c["about"], "asserts": c["asserts"]}
              for a in articles for n, c in enumerate(a["assertions"])]
    got: dict = {}
    for i in range(0, len(claims), batch):
        got |= _read(claims[i:i + batch], run, root)
    out.parent.mkdir(parents=True, exist_ok=True)
    part = out.with_suffix(".part")
    with open(part, "w") as f:
        for a in articles:
            life = [list(got[(a["id"], n)]) if (a["id"], n) in got else None for n in range(len(a["assertions"]))]
            f.write(json.dumps({"id": a["id"], "life": life}) + "\n")
    part.rename(out)
    return len(got)


def main() -> None:
    parser = argparse.ArgumentParser(description="Read every grounded claim for subject and life, resumably.")
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--model", default="haiku")
    args = parser.parse_args()
    run = patient(_limited(claude_runner(args.model)))
    todo = sorted((p.parent.name, p.stem) for p in (args.root / "grounded").glob("*/*.jsonl"))
    with ThreadPoolExecutor(args.workers) as pool:
        futures = [pool.submit(read_month_life, args.root, paper, stem, run) for paper, stem in todo]
        for (paper, stem), f in zip(todo, futures):
            try:
                n = f.result()
            except UsageLimit as exc:
                print(f"stopped: usage limit ({exc})", flush=True)
                pool.shutdown(cancel_futures=True)
                return
            if n:
                print(f"{paper} {stem} {n}", flush=True)


if __name__ == "__main__":
    sys.exit(main())
