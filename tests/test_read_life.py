"""Running the life-or-work reading over every grounded claim (ART-PLAN
§15.2): month by month, resumably, each claim's two parts kept beside the
claim, and a batch refused as a whole read again in halves."""
import json

from abductive.read_life import read_month_life
from abductive.reading import ReadingError


def _grounded(root, paper, stem, articles):
    p = root / "grounded" / paper / f"{stem}.jsonl"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("".join(json.dumps({"id": i, "published": "2026-08-01",
                                     "assertions": [{"who": "W", "about": a, "asserts": "x", "force": "reports",
                                                     "stance": "neither"} for a in abouts]}) + "\n"
                         for i, abouts in articles))


def _answer(user):
    rows = [line.split(" | ")[0:2] for line in user.splitlines()]
    return "\n".join(f"{n} {'p y' if 'life' in about else 'w n'}" for n, about in rows)


def test_each_claim_gets_its_two_parts_beside_it_in_order(tmp_path):
    _grounded(tmp_path, "nyt", "2026-08", [("a1", ["about: her life", "about: a work"]), ("a2", ["about: life story"])])
    calls = []

    def run(system, user):
        calls.append(user)
        return _answer(user), {"cost_usd": 0.001}
    assert read_month_life(tmp_path, "nyt", "2026-08", run, batch=2) == 3
    rows = [json.loads(x) for x in (tmp_path / "life" / "nyt" / "2026-08.jsonl").read_text().splitlines()]
    assert rows == [{"id": "a1", "life": [["person", "yes"], ["work", "no"]]}, {"id": "a2", "life": [["person", "yes"]]}]
    assert len(calls) == 2 and len((tmp_path / "life" / "usage.jsonl").read_text().splitlines()) == 2
    assert read_month_life(tmp_path, "nyt", "2026-08", run, batch=2) == 0 and len(calls) == 2    # done months are skipped


def test_a_refused_batch_is_read_in_halves_and_a_claim_refused_alone_is_kept_unread(tmp_path):
    _grounded(tmp_path, "nyt", "2026-08", [("a1", ["about: her life", "about: bad", "about: a work"])])

    def run(system, user):
        if "bad" in user:
            raise ReadingError("answer outside the form")
        return _answer(user), {}
    assert read_month_life(tmp_path, "nyt", "2026-08", run, batch=3) == 2
    rows = [json.loads(x) for x in (tmp_path / "life" / "nyt" / "2026-08.jsonl").read_text().splitlines()]
    assert rows == [{"id": "a1", "life": [["person", "yes"], None, ["work", "no"]]}]
    failed = [json.loads(x) for x in (tmp_path / "life" / "failed.jsonl").read_text().splitlines()]
    assert [(f["paper"], f["month"], f["id"], f["n"]) for f in failed] == [("nyt", "2026-08", "a1", 1)]
