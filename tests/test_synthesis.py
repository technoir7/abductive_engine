"""Concepts formed from claims in time order (ART-PLAN §4, grouping by
meaning): a claim joins the nearest live concept if near enough, or founds
one; a concept unasserted for long goes dormant."""
import math

from abductive.synthesis import Synthesis


def unit(*xs):
    n = math.sqrt(sum(x * x for x in xs))
    return [x / n for x in xs]


def test_a_near_claim_joins_and_a_far_one_founds_a_concept():
    s = Synthesis(theta=0.9, dormant_months=24)
    a = s.take(0, unit(1, 0), ("g", "x", 0), "Jones")
    b = s.take(0, unit(1, 0.1), ("g", "y", 0), "Cumming")
    c = s.take(0, unit(0, 1), ("g", "y", 1), "Cumming")
    assert a == b != c
    assert s.concepts[a].writers == {"Jones", "Cumming"} and len(s.concepts[a].members) == 2


def test_a_concept_unasserted_for_longer_than_the_window_is_dormant():
    s = Synthesis(theta=0.9, dormant_months=24)
    a = s.take(0, unit(1, 0), ("g", "x", 0), "Jones")
    assert s.take(24, unit(1, 0), ("g", "y", 0), "Jones") == a      # within two years: joins
    assert s.take(49, unit(1, 0), ("g", "z", 0), "Jones") != a      # 25 months on: a new concept


def test_a_concept_remembers_when_it_was_founded_and_last_asserted():
    s = Synthesis(theta=0.9, dormant_months=24)
    a = s.take(3, unit(1, 0), ("g", "x", 0), "Jones")
    s.take(7, unit(1, 0), ("g", "y", 0), "Jones")
    assert (s.concepts[a].founded, s.concepts[a].last) == (3, 7)


def test_concepts_are_formed_over_saved_months_and_written(tmp_path):
    import json
    from datetime import date

    from abductive.embed import embed_month
    from abductive.press import ArtText, write_month
    from abductive.synthesis import synthesise
    claim = {"who": "w", "about": "Kusama", "asserts": "dazzles", "force": "judges", "stance": "approval"}
    for m in (1, 2):
        write_month(tmp_path, "guardian", 2004, m,
                    [ArtText("guardian", f"a{m}", date(2004, m, 1), "u", "Kusama", "", "", f"Writer {m}")])
        g = tmp_path / "grounded" / "guardian"
        g.mkdir(parents=True, exist_ok=True)
        (g / f"2004-{m:02d}.jsonl").write_text(json.dumps({"id": f"a{m}", "published": f"2004-{m:02d}-01",
                                                           "assertions": [claim]}) + "\n")
        embed_month(tmp_path, "guardian", 2004, m, lambda texts: [[1.0, 0.0] for _ in texts], dims=2)
    concepts = synthesise(tmp_path, dims=2)
    assert len(concepts) == 1 and concepts[0].writers == {"Writer 1", "Writer 2"}
    rows = [json.loads(line) for line in (tmp_path / "concepts" / "concepts.jsonl").read_text().splitlines()]
    assert rows[0]["founded"] == "2004-01" and rows[0]["members"] == [["guardian", "a1", 0], ["guardian", "a2", 0]]
