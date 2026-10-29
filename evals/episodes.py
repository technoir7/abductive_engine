"""ART-PLAN §10, known episodes: a test of the trends, never an input.
Words and peak years as fixed in the plan before grouping.

    uv run python -m evals.episodes"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path.home() / "Documents" / "art-press-texts"
EPISODES = [
    ("NFTs and crypto art", {"nft", "nfts", "crypto"}, range(2021, 2023)),
    ("return of looted objects", {"restitution", "looted", "repatriation", "bronzes"}, range(2019, 2024)),
    ("Black artists and race", {"black", "race", "racial", "racism"}, range(2020, 2023)),
    ("AI-made art", {"ai"}, range(2023, 2027)),
    ("street art and Banksy", {"street", "graffiti"}, range(2000, 2015)),
]


def main() -> None:
    trends = [json.loads(line) for line in (ROOT / "trends" / "trends.jsonl").read_text().splitlines()]
    for name, words, peak in EPISODES:
        found = [t for t in trends if words & set(t["words"])]
        passed = [t for t in found if int(max(t["shares"], key=t["shares"].get)) in peak]
        print(f"{name}: {'PASS' if passed else 'MISS'} ({len(found)} trends name it, {len(passed)} peak in "
              f"{peak.start}-{peak.stop - 1})")
        for t in sorted(found, key=lambda t: -t["claims"])[:6]:
            top = max(t["shares"], key=t["shares"].get)
            print(f"   #{t['id']} {t['start']}-{t['last']} {t['claims']} claims, peak {top} "
                  f"({t['shares'][top]:.1%}): {' '.join(t['words'])}")


if __name__ == "__main__":
    main()
