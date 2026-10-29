"""
Proper names, found by how the corpus itself writes them (ART-PLAN §10.1),
so that claims can be grouped by their idea rather than by whom or what
they name. A word is a name if, wherever it is not the first word of a
field, it is almost never written lowercase: Picasso and Tate never are,
black and craft often are. Words in capitals (AI, NFT) are kept: they are
as often terms as names.
"""
from __future__ import annotations

import re
from collections import Counter
from typing import Iterable, Mapping

MAX_LOWER = 0.05
_WORD = re.compile(r"[A-Za-z][A-Za-z'’-]*")
_CAPITALS = re.compile(r"[A-Z]{2,}s?")


def _stem(word: str) -> str:
    return re.sub(r"['’]s$", "", word).lower()


def proper_names(fields: Iterable[str], max_lower: float = MAX_LOWER) -> frozenset[str]:
    upper, lower = Counter(), Counter()
    for field in fields:
        for w in _WORD.findall(field)[1:]:
            (upper if w[0].isupper() else lower)[_stem(w)] += 1
    return frozenset(w for w, n in upper.items() if lower[w] < max_lower * (n + lower[w]))


def without_names(text: str, names: frozenset[str]) -> str:
    def keep(m: re.Match) -> str:
        w = m.group(0)
        return w if _CAPITALS.fullmatch(w) or _stem(w) not in names else ""
    return re.sub(r"\s+", " ", _WORD.sub(keep, text)).strip()


def idea_phrase(a: Mapping[str, str], names: frozenset[str]) -> str:
    return f"clustering: {without_names(a['about'], names)}: {without_names(a['asserts'], names)}"
