"""
Rival schemes and programmes: level 3 (DESIGN §§5–7).

A programme is a vocabulary and every scheme descended from it; a variant
changes links only, so it stays in its programme. (A changed vocabulary
starts a new programme: concept formation, build step 6.)

Every scheme is scored each week. Two schemes are compared only on the
weeks both were scored, by the log Bayes factor between them, recent weeks
counting more, so a young scheme is neither credited nor blamed for weeks
before its birth (Lakatos: credit only for novel predictions).

- The leader changes when a rival is ahead of it on that comparison; the
  incumbent keeps a tie. A change of leader is a structural shift within a
  programme, or a conceptual shift between programmes (Kuhn's normal
  science and revolution).
- A scheme goes only when a rival beats it by a log Bayes factor above
  ln 100 (Jeffreys' "decisive"). Trailing is not refutation, so every
  programme's best survives until refuted.
- Every few weeks each programme's best proposes a variant: the link its
  surprises support, or the loss of a link the evidence now doubts. When
  the population is full, room is made by dropping the weakest scheme that
  is not its programme's best; if every scheme is, the variant waits.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date
from itertools import count
from typing import Iterable, Optional

from .scheme import HALF_LIFE_WEEKS, Link, Scheme
from .weeks import Week

DECISIVE = math.log(100)
DOUBTED = 0.05          # a link this unlikely to exist is offered for removal
PROPOSE_EVERY = 4       # weeks between rounds of proposals
_DECAY = 0.5 ** (1 / HALF_LIFE_WEEKS)
_ids = count()


@dataclass(eq=False)
class Member:
    scheme: Scheme
    programme: str
    born: date
    id: int

    @property
    def name(self) -> str:
        if not self.scheme.links:
            return f"{self.programme}: no links"
        return f"{self.programme}: " + "; ".join(sorted(_describe(link) for link in self.scheme.links))


@dataclass(frozen=True)
class Shift:
    friday: date
    from_name: str
    to_name: str
    from_programme: str
    to_programme: str

    @property
    def conceptual(self) -> bool:
        return self.from_programme != self.to_programme


class Population:
    def __init__(self, seeds: Iterable[tuple[str, Scheme]], max_size: int = 12) -> None:
        self.members: list[Member] = [Member(s, name, date.min, next(_ids)) for name, s in seeds]
        if not self.members:
            raise ValueError("a population needs at least one scheme")
        self.max_size = max_size
        self.leader = self.members[0]
        self.shifts: list[Shift] = []
        self._evidence: dict[tuple[int, int], float] = {}   # (a, b) with a < b: for a over b
        self._weeks = 0

    def evidence(self, a: Member, b: Member) -> float:
        """The log Bayes factor for A over B, on the weeks both were scored."""
        if a.id == b.id:
            return 0.0
        key = (min(a.id, b.id), max(a.id, b.id))
        e = self._evidence.get(key, 0.0)
        return e if a.id < b.id else -e

    def step(self, week: Week) -> float:
        """Score and learn one week. Returns the engine's score for it: that of
        the scheme leading before the week was seen, so it too is out of sample."""
        scores = {m.id: sum(m.scheme.score_and_learn(week).values()) for m in self.members}
        engine = scores[self.leader.id]
        for i, a in enumerate(self.members):
            for b in self.members[i + 1:]:
                key = (min(a.id, b.id), max(a.id, b.id))
                lo, hi = (a, b) if a.id < b.id else (b, a)
                self._evidence[key] = _DECAY * self._evidence.get(key, 0.0) + scores[lo.id] - scores[hi.id]
        self._lead(week.friday)
        self._refute()
        self._weeks += 1
        if self._weeks % PROPOSE_EVERY == 0:
            self._propose(week.friday)
        return engine

    def _lead(self, friday: date) -> None:
        challenger = max(self.members, key=lambda m: self.evidence(m, self.leader))
        if self.evidence(challenger, self.leader) > 0:
            old, self.leader = self.leader, challenger
            self.shifts.append(Shift(friday, old.name, challenger.name, old.programme, challenger.programme))

    def _refute(self) -> None:
        self.members = [m for m in self.members
                        if m is self.leader or max(self.evidence(r, m) for r in self.members) <= DECISIVE]
        live = {m.id for m in self.members}
        self._evidence = {k: v for k, v in self._evidence.items() if k[0] in live and k[1] in live}

    def _best(self, programme: str) -> Member:
        return max((m for m in self.members if m.programme == programme),
                   key=lambda m: self.evidence(m, self.leader))

    def _propose(self, friday: date) -> None:
        for programme in dict.fromkeys(m.programme for m in self.members):
            best = self._best(programme)
            change = _change(best.scheme)
            if change is None:
                continue
            add, remove = change
            links = (best.scheme.links | {add} if add else best.scheme.links) - ({remove} if remove else set())
            if any(m.programme == programme and m.scheme.links == links for m in self.members):
                continue
            if len(self.members) >= self.max_size and not self._make_room():
                continue
            self.members.append(Member(best.scheme.variant(add=add, remove=remove), programme, friday, next(_ids)))

    def _make_room(self) -> bool:
        bests = {self._best(p).id for p in {m.programme for m in self.members}}
        spare = [m for m in self.members if m.id not in bests and m is not self.leader]
        if not spare:
            return False
        weakest = min(spare, key=lambda m: self.evidence(m, self.leader))
        self.members.remove(weakest)
        return True


def _change(scheme: Scheme) -> Optional[tuple[Optional[Link], Optional[Link]]]:
    """(add, remove): drop a doubted link first, else add the prompted one."""
    doubted = [link for link in scheme.links if scheme.existence(link) < DOUBTED]
    if doubted:
        return None, min(doubted, key=scheme.existence)
    prompted = scheme.proposal()
    return (prompted, None) if prompted else None


def _describe(link: Link) -> str:
    concept, series = link
    return f"{concept.form.describe()} → {series}"

