"""The checked copy of the assertions: only those grounded in their article."""
import json
from datetime import date

from abductive.ground import ground_month
from abductive.press import ArtText, write_month


def test_a_month_keeps_grounded_assertions_and_counts_the_rest(tmp_path):
    write_month(tmp_path, "nyt", 2015, 3, [ArtText("nyt", "i", date(2015, 3, 1), "u", "Kusama at Zwirner", "", "", "")])
    keep = {"who": "the paper", "about": "Kusama", "asserts": "shows at Zwirner", "force": "reports", "stance": "neither"}
    drop = {"who": "the paper", "about": "Kusama", "asserts": "rated four stars", "force": "judges", "stance": "approval"}
    out = tmp_path / "assertions" / "nyt"
    out.mkdir(parents=True)
    (out / "2015-03.jsonl").write_text(json.dumps({"id": "i", "published": "2015-03-01", "assertions": [keep, drop]}) + "\n")
    assert ground_month(tmp_path, "nyt", 2015, 3) == (2, 1)
    got = [json.loads(line) for line in (tmp_path / "grounded" / "nyt" / "2015-03.jsonl").read_text().splitlines()]
    assert got == [{"id": "i", "published": "2015-03-01", "assertions": [keep]}]
