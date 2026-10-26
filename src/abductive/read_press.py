"""
Read the saved art texts (press.py) month by month and keep what each
article asserts (reading.py), resumably: a month's file is written whole,
so a run can stop at any point and start again where it left off.

    uv run python -m abductive.read_press --root ~/Documents/art-press-texts [--workers 4] [--only 2015-03]

Writes, under ROOT/assertions/: one JSON-lines file per paper and month,
usage.jsonl (one line per model call: tokens, cost, time) and failed.jsonl
(articles the model could not read in the form, recorded, never invented).
A usage limit is waited out, half an hour at a time for up to six hours;
then the run stops.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
from pathlib import Path

from .disk import ensure_room
from .press import FIRST, LAST, ArtText, months, read_month
from .reading import Assertion, ReadingError, Runner, claude_runner, read_batch

_LOG_LOCK = threading.Lock()
# Settled on the pilot (March 2015): about 10,000 tokens out per call either way.
BATCH = {"guardian": 5, "nyt": 10}


class UsageLimit(RuntimeError):
    pass


def _append(path: Path, row: dict) -> None:
    with _LOG_LOCK:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a") as f:
            f.write(json.dumps(row) + "\n")


def _read(texts: list[ArtText], run: Runner, root: Path, label: str) -> dict[str, list[Assertion]]:
    """Read a batch; on an answer outside the form, read its halves; an
    article that still fails alone is recorded in failed.jsonl."""
    try:
        got, usage = read_batch(texts, run)
        _append(root / "assertions" / "usage.jsonl", {"month": label, "articles": len(texts), **usage})
        return got
    except (ReadingError, subprocess.CalledProcessError, subprocess.TimeoutExpired, json.JSONDecodeError) as exc:
        if len(texts) == 1:
            _append(root / "assertions" / "failed.jsonl", {"month": label, "id": texts[0].id, "error": str(exc)[:300]})
            return {}
        half = len(texts) // 2
        return _read(texts[:half], run, root, label) | _read(texts[half:], run, root, label)


def read_month_texts(root: Path, paper: str, year: int, month: int, run: Runner, batch: int = 10) -> int:
    """Read one saved month unless already read. Returns articles read."""
    out = root / "assertions" / paper / f"{year}-{month:02d}.jsonl"
    texts = read_month(root, paper, year, month)
    if out.exists() or texts is None:
        return 0
    ensure_room(root)
    label = f"{paper} {year}-{month:02d}"
    got: dict[str, list[Assertion]] = {}
    for i in range(0, len(texts), batch):
        got |= _read(texts[i:i + batch], run, root, label)
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(".part")
    tmp.write_text("".join(json.dumps({"id": t.id, "published": t.published.isoformat(),
                                       "assertions": [asdict(a) for a in got[t.id]]}) + "\n"
                           for t in texts if t.id in got))
    tmp.rename(out)
    return len(got)


def _limited(run: Runner) -> Runner:
    """Turn the CLI's usage-limit failure into UsageLimit, which stops the run."""
    def guarded(system: str, user: str):
        try:
            return run(system, user)
        except subprocess.CalledProcessError as exc:
            text = f"{exc.stdout or ''} {exc.stderr or ''}".lower()
            if "limit" in text and ("usage" in text or "rate" in text or "reset" in text):
                raise UsageLimit(text[:300]) from exc
            raise
        except ReadingError as exc:
            if "limit" in str(exc).lower():
                raise UsageLimit(str(exc)[:300]) from exc
            raise
    return guarded


def patient(run: Runner, wait_s: float = 1800, tries: int = 12, sleep=None) -> Runner:
    """On a usage limit, wait WAIT_S and try again, up to TRIES times
    (six hours by default, more than a usage window); then stop."""
    import time
    sleep = sleep or time.sleep

    def waiting(system: str, user: str):
        for attempt in range(tries):
            try:
                return run(system, user)
            except UsageLimit:
                if attempt == tries - 1:
                    raise
                print(f"usage limit; waiting {wait_s / 60:.0f} minutes", flush=True)
                sleep(wait_s)
    return waiting


def main() -> None:
    parser = argparse.ArgumentParser(description="Read the saved art texts, resumably.")
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--paper", choices=["nyt", "guardian", "both"], default="both")
    parser.add_argument("--batch", type=int, default=None,
                        help="articles per call; default 5 for the Guardian's full texts, 10 for the NYT's paragraphs")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--model", default="haiku")
    parser.add_argument("--effort", default=None)
    parser.add_argument("--only", default=None, help="one month, YYYY-MM")
    args = parser.parse_args()
    run = patient(_limited(claude_runner(args.model, args.effort)))
    papers = ["guardian", "nyt"] if args.paper == "both" else [args.paper]
    todo = [(p, y, m) for (y, m) in months(FIRST, LAST) for p in papers
            if args.only is None or f"{y}-{m:02d}" == args.only]
    with ThreadPoolExecutor(args.workers) as pool:
        futures = [pool.submit(read_month_texts, args.root, p, y, m, run, args.batch or BATCH[p]) for p, y, m in todo]
        for (p, y, m), f in zip(todo, futures):
            try:
                n = f.result()
            except UsageLimit as exc:
                print(f"stopped: usage limit ({exc})", flush=True)
                pool.shutdown(cancel_futures=True)
                return
            if n:
                print(f"{p} {y}-{m:02d} {n}", flush=True)


if __name__ == "__main__":
    sys.exit(main())
