"""Rival schemes and programmes (DESIGN §§5–7, level 3): schemes are compared
on the weeks both were scored, the leader changes when a rival is ahead,
a scheme goes only when decisively refuted, and variants come from what the
evidence prompts."""
from abductive.population import Population
from abductive.scheme import Scheme
from tests.test_scheme import KINDS, X_UP, driven


def bare(*vocabulary):
    return Scheme(vocabulary, frozenset(), KINDS)


def run(pop, weeks):
    for w in weeks:
        pop.step(w)
    return pop


def test_a_variant_the_evidence_prompts_takes_the_lead_within_its_programme():
    pop = run(Population([("X", bare(X_UP))]), driven(300))
    assert pop.leader.scheme.links == {(X_UP, "Y")}
    shift = pop.shifts[-1]
    assert not shift.conceptual and shift.to_programme == "X"


def test_a_programme_with_the_concepts_the_evidence_needs_takes_over():
    pop = run(Population([("none", bare()), ("X", bare(X_UP))]), driven(300))
    assert pop.leader.programme == "X"
    assert any(s.conceptual and (s.from_programme, s.to_programme) == ("none", "X") for s in pop.shifts)


def test_a_decisively_refuted_scheme_goes():
    pop = run(Population([("none", bare()), ("X", bare(X_UP))]), driven(300))
    assert "none" not in {m.programme for m in pop.members}


def test_where_the_evidence_cannot_tell_them_apart_rivals_survive():
    pop = run(Population([("none", bare()), ("X", bare(X_UP))]), driven(300, effect=0.0))
    assert {m.programme for m in pop.members} == {"none", "X"}
    assert pop.leader.programme == "none"   # the incumbent keeps a tie
    assert pop.shifts == []


def test_a_scheme_is_not_credited_or_blamed_for_weeks_before_its_birth():
    pop = Population([("X", bare(X_UP))])
    seed = pop.members[0]
    for w in driven(300):
        pop.step(w)
        if len(pop.members) > 1:
            break
    newborn = pop.members[-1]
    assert newborn.born == w.friday and newborn.born > seed.born
    assert pop.evidence(newborn, seed) == 0.0 == pop.evidence(seed, newborn)


def test_a_link_that_stops_bearing_is_dropped_by_a_variant():
    pop = run(Population([("X", bare(X_UP))]), driven(300) + driven(400, seed=1, effect=0.0))
    assert pop.leader.scheme.links == frozenset()
