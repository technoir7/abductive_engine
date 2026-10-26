"""Art articles' texts from the two papers' API responses (ART-PLAN §3)."""
import json
from datetime import date

from abductive.press import ArtText, guardian_art, months, nyt_art, read_month, write_month


def test_nyt_keeps_only_articles_tagged_art_with_what_the_archive_gives():
    docs = [
        {"_id": "nyt://a/1", "pub_date": "2015-03-20T00:00:00+0000", "web_url": "u1",
         "headline": {"main": "A show"}, "abstract": "Abs.", "lead_paragraph": "Lead.",
         "byline": {"original": "By Holland Cotter"},
         "keywords": [{"name": "Subject", "value": "ART"}, {"name": "persons", "value": "Kusama, Yayoi"}]},
        {"_id": "nyt://a/2", "pub_date": "2015-03-21T00:00:00+0000", "web_url": "u2",
         "headline": {"main": "Baseball"}, "keywords": [{"name": "subject", "value": "Baseball"}]},
        {"_id": "nyt://a/3", "pub_date": "2015-03-22T00:00:00+0000", "web_url": "u3",
         "headline": None, "abstract": None, "lead_paragraph": None, "keywords": [{"name": "subject", "value": "Art"}]},
    ]
    got = nyt_art(docs)
    assert got[0] == ArtText("nyt", "nyt://a/1", date(2015, 3, 20), "u1", "A show", "Abs.", "Lead.", "By Holland Cotter",
                            (("Subject", "ART"), ("persons", "Kusama, Yayoi")))
    assert [t.id for t in got] == ["nyt://a/1", "nyt://a/3"] and got[1].headline == ""


def test_guardian_keeps_headline_standfirst_and_body_without_markup():
    results = [{"id": "artanddesign/2015/mar/20/x", "webPublicationDate": "2015-03-20T10:00:00Z", "webUrl": "u",
                "fields": {"headline": "H", "trailText": "<p>A <strong>bold</strong> claim</p>", "bodyText": "Body.",
                           "byline": "Jonathan Jones"},
                "tags": [{"id": "artanddesign/yayoi-kusama", "webTitle": "Yayoi Kusama"}]}]
    assert guardian_art(results) == [ArtText("guardian", "artanddesign/2015/mar/20/x", date(2015, 3, 20), "u",
                                             "H", "A bold claim", "Body.", "Jonathan Jones",
                                             (("artanddesign/yayoi-kusama", "Yayoi Kusama"),))]


def test_a_month_written_is_read_back_and_marks_the_month_done(tmp_path):
    texts = [ArtText("nyt", "i", date(2015, 3, 1), "u", "h", "s", "b", "by", (("persons", "Kusama, Yayoi"),))]
    assert read_month(tmp_path, "nyt", 2015, 3) is None
    write_month(tmp_path, "nyt", 2015, 3, texts)
    assert read_month(tmp_path, "nyt", 2015, 3) == texts
    write_month(tmp_path, "nyt", 2015, 4, [])            # a month with none is still done
    assert read_month(tmp_path, "nyt", 2015, 4) == []
    assert json.loads((tmp_path / "nyt" / "2015-03.jsonl").read_text())["headline"] == "h"


def test_months_from_first_to_last():
    assert months((2000, 11), (2001, 2)) == [(2000, 11), (2000, 12), (2001, 1), (2001, 2)]
