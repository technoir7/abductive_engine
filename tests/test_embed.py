"""Assertions turned into vectors for grouping by meaning (ART-PLAN §4)."""
import json
import math

from abductive.embed import embed_month, phrase, read_vectors, shorten


def test_a_vector_is_shortened_and_made_unit_length():
    v = shorten([3.0, 4.0, 12.0], dims=2)
    assert [round(x, 3) for x in v] == [0.6, 0.8]


def test_a_month_is_embedded_once_in_order_and_read_back(tmp_path):
    out = tmp_path / "grounded" / "nyt"
    out.mkdir(parents=True)
    a = {"who": "w", "about": "Kusama", "asserts": "dazzles", "force": "judges", "stance": "approval"}
    rows = [{"id": "x", "published": "2015-03-01", "assertions": [a, a | {"asserts": "bores"}]},
            {"id": "y", "published": "2015-03-02", "assertions": []}]
    (out / "2015-03.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
    seen = []

    def fake(texts):
        seen.extend(texts)
        return [[1.0, float(i), 0.0, 0.0] for i, _ in enumerate(texts)]
    assert embed_month(tmp_path, "nyt", 2015, 3, fake, dims=2) == 2
    assert seen == [phrase(a), phrase(a | {"asserts": "bores"})]
    keys, vectors = read_vectors(tmp_path, "nyt", 2015, 3, dims=2)
    assert keys == [("x", 0), ("x", 1)]
    assert [round(x, 2) for x in vectors[1]] == [round(1 / math.sqrt(2), 2)] * 2
    assert embed_month(tmp_path, "nyt", 2015, 3, fake, dims=2) == 0     # done already


def test_ideas_are_embedded_as_given_into_their_own_folder(tmp_path):
    out = tmp_path / "grounded" / "nyt"
    out.mkdir(parents=True)
    a = {"who": "w", "about": "Kusama", "asserts": "dazzles", "force": "judges", "stance": "approval"}
    (out / "2015-03.jsonl").write_text(json.dumps({"id": "x", "assertions": [a]}) + "\n")
    seen = []

    def fake(texts):
        seen.extend(texts)
        return [[1.0, 0.0] for _ in texts]
    assert embed_month(tmp_path, "nyt", 2015, 3, fake, dims=2, text=lambda a: a["asserts"], out="ideas") == 1
    assert seen == ["dazzles"]
    assert read_vectors(tmp_path, "nyt", 2015, 3, dims=2, out="ideas")[0] == [("x", 0)]
    assert not (tmp_path / "vectors").exists()
