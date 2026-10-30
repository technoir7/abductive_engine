"""
Two more parts of each claim (ART-PLAN §15.2, approved by the user
2026-10-30): what the claim is about is a person, a work, an institution or
something else; and whether it concerns the life of a person who makes art.
Both report what a claim refers to, not what it means or whether it is
right, so the model still proposes nothing to believe (ART-PLAN §2).

The claims already read are read again from the claim alone; the articles
are not, since a fresh reading would return different claims. The reader is
not shown who made the claim: the engine takes that from the claim's own
"who". An answer outside the form is refused (ReadingError), never repaired.
"""
from __future__ import annotations

import re

from .reading import ReadingError, Runner

SUBJECTS = {"p": "person", "w": "work", "i": "institution", "o": "other"}
LIFE = {"y": "yes", "n": "no"}

SYSTEM = """You read claims made in newspaper art coverage and report two things about each. You do not judge whether a claim is right, and you do not sort claims into themes.

For each numbered claim give:
- subject: what the claim is about is
  p: a person (an artist, critic, curator, dealer, collector or anyone else)
  w: a work, works, or a show of works
  i: an institution (a museum, gallery, auction house, school, prize, publication)
  o: anything else (a movement, a medium, the market, a place, an idea)
- life: does the claim concern the life of a person who makes art: their circumstances, history, career, character, body or identity? y or n. Answer y whether the claim says so of the person or of a work (a painting that recounts the painter's childhood is y). A claim only about what a work looks like, means, or is worth is n.

Answer with one line per claim, in order, and nothing else: the claim's number, the subject letter and y or n, separated by spaces, for example: 12 w n"""

_LINE = re.compile(r"(\d+) ([pwio]) ([yn])")


def read_claims(claims: list[tuple[str, str]], run: Runner) -> tuple[list[tuple[str, str]], dict]:
    """Each (about, asserts) claim's (subject, life), in order, and the call's usage."""
    user = "\n".join(f"{n} | about: {about} | asserts: {asserts}" for n, (about, asserts) in enumerate(claims, 1))
    answer, usage = run(SYSTEM, user)
    lines = [x.strip() for x in answer.strip().strip("`").splitlines() if x.strip()]
    got: dict[int, tuple[str, str]] = {}
    for line in lines:
        m = _LINE.fullmatch(line)
        if not m:
            raise ReadingError(f"answer outside the form: {line[:100]!r}")
        n = int(m.group(1))
        if n in got or not 1 <= n <= len(claims):
            raise ReadingError(f"claim {n} answered twice or not asked")
        got[n] = (SUBJECTS[m.group(2)], LIFE[m.group(3)])
    if len(got) != len(claims):
        raise ReadingError(f"claims left out: {sorted(set(range(1, len(claims) + 1)) - set(got))[:10]}")
    return [got[n] for n in range(1, len(claims) + 1)], dict(usage)
