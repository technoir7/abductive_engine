"""
The checked copy of the reader's assertions (reading.grounded): under
ROOT/grounded/, each month's assertions with only those whose every name
and number is in their article. The raw assertions are kept as read.

    uv run python -m abductive.ground --root ~/Documents/art-press-texts
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .press import read_month
from .reading import Assertion, grounded


def ground_month(root: Path, paper: str, year: int, month: int) -> tuple[int, int]:
    """(assertions read, assertions dropped) for one month; (0, 0) if unread."""
    src = root / "assertions" / paper / f"{year}-{month:02d}.jsonl"
    texts = read_month(root, paper, year, month)
    if not src.exists() or texts is None:
        return 0, 0
    by_id = {t.id: t for t in texts}
    rows, total, dropped = [], 0, 0
    for line in src.read_text().splitlines():
        row = json.loads(line)
        t = by_id[row["id"]]
        article = " ".join((t.headline, t.summary, t.body))
        kept = [a for a in row["assertions"] if grounded(Assertion(**a), article, t.byline)]
        total, dropped = total + len(row["assertions"]), dropped + len(row["assertions"]) - len(kept)
        rows.append(row | {"assertions": kept})
    out = root / "grounded" / paper / src.name
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("".join(json.dumps(r) + "\n" for r in rows))
    return total, dropped


def main() -> None:
    parser = argparse.ArgumentParser(description="Write the checked copy of the assertions.")
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    total = dropped = 0
    for src in sorted((args.root / "assertions").glob("*/*.jsonl")):
        y, m = map(int, src.stem.split("-"))
        t, d = ground_month(args.root, src.parent.name, y, m)
        total, dropped = total + t, dropped + d
    print(f"{total} assertions, {dropped} dropped as not grounded ({dropped / max(total, 1):.1%})")


if __name__ == "__main__":
    main()
