"""Reading the saved texts month by month, resumably (ART-PLAN §7 step 3)."""
import json
from datetime import date

from abductive.press import ArtText, write_month
from abductive.read_press import UsageLimit, read_month_texts
from abductive.reading import ReadingError

GOOD = {"who": "w", "about": "a", "asserts": "s", "force": "reports", "stance": "neither"}


def texts(n):
    return [ArtText("nyt", f"id{i}", date(2015, 3, 1), "u", f"h{i}", "", "") for i in range(n)]


def echo(fail_on=()):
    calls = []

    def run(system, user):
        ids = [line[4:] for line in user.splitlines() if line.startswith("id: ")]
        calls.append(ids)
        if any(i in fail_on for i in ids):
            return "not json", {}
        return json.dumps({"articles": [{"id": i, "assertions": [GOOD]} for i in ids]}), {"output_tokens": len(ids)}
    run.calls = calls
    return run


def test_a_month_is_read_in_batches_and_written_with_its_usage(tmp_path):
    write_month(tmp_path, "nyt", 2015, 3, texts(5))
    run = echo()
    assert read_month_texts(tmp_path, "nyt", 2015, 3, run, batch=2) == 5
    assert [len(c) for c in run.calls] == [2, 2, 1]
    rows = [json.loads(line) for line in (tmp_path / "assertions" / "nyt" / "2015-03.jsonl").read_text().splitlines()]
    assert [r["id"] for r in rows] == [f"id{i}" for i in range(5)] and rows[0]["assertions"] == [GOOD]
    usage = [json.loads(line) for line in (tmp_path / "assertions" / "usage.jsonl").read_text().splitlines()]
    assert [u["articles"] for u in usage] == [2, 2, 1] and usage[0]["output_tokens"] == 2


def test_a_month_already_read_is_not_read_again(tmp_path):
    write_month(tmp_path, "nyt", 2015, 3, texts(2))
    read_month_texts(tmp_path, "nyt", 2015, 3, echo(), batch=2)
    run = echo()
    assert read_month_texts(tmp_path, "nyt", 2015, 3, run, batch=2) == 0
    assert run.calls == []


def test_a_failed_batch_is_split_and_an_unreadable_article_is_recorded_not_invented(tmp_path):
    write_month(tmp_path, "nyt", 2015, 3, texts(4))
    run = echo(fail_on={"id2"})
    assert read_month_texts(tmp_path, "nyt", 2015, 3, run, batch=4) == 3
    rows = [json.loads(line) for line in (tmp_path / "assertions" / "nyt" / "2015-03.jsonl").read_text().splitlines()]
    assert [r["id"] for r in rows] == ["id0", "id1", "id3"]
    failed = [json.loads(line) for line in (tmp_path / "assertions" / "failed.jsonl").read_text().splitlines()]
    assert [f["id"] for f in failed] == ["id2"]


def test_a_usage_limit_stops_the_run(tmp_path):
    write_month(tmp_path, "nyt", 2015, 3, texts(2))

    def limited(system, user):
        raise UsageLimit("usage limit reached")
    try:
        read_month_texts(tmp_path, "nyt", 2015, 3, limited, batch=2)
    except UsageLimit:
        pass
    else:
        raise AssertionError("should stop")
    assert not (tmp_path / "assertions" / "nyt" / "2015-03.jsonl").exists()
