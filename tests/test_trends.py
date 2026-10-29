"""Trends: claims grouped by idea year by year, followed across years
(ART-PLAN §10)."""
import numpy as np

from abductive.trends import broad_groups, choose_k, distinctive_words, follow, kmeans, moving


def _blobs(rng, centres, n):
    X = np.vstack([c + 0.05 * rng.standard_normal((n, len(c))) for c in centres])
    return (X / np.linalg.norm(X, axis=1, keepdims=True)).astype(np.float32)


def test_kmeans_finds_separate_ideas():
    rng = np.random.default_rng(0)
    X = _blobs(rng, np.eye(4), 30)
    _, labels = kmeans(X, 4, np.random.default_rng(1))
    assert len(set(labels)) == 4
    assert all(len(set(labels[i * 30:(i + 1) * 30])) == 1 for i in range(4))


def test_a_broad_group_has_many_writers_on_many_subjects():
    labels = np.array([0] * 12 + [1] * 12 + [2] * 12)
    writers = [f"w{i}" for i in range(12)] + ["one critic"] * 12 + [f"w{i}" for i in range(12)]
    subjects = [f"s{i}" for i in range(12)] * 2 + ["one story"] * 12
    assert broad_groups(labels, writers, subjects, least=10) == {0}


def test_k_is_the_one_giving_the_most_broad_groups():
    rng = np.random.default_rng(0)
    X = _blobs(rng, np.eye(8), 20)                 # eight ideas, each broad
    writers = [f"w{i % 20}" for i in range(len(X))]
    subjects = [f"s{i % 20}" for i in range(len(X))]
    k, labels = choose_k(X, writers, subjects, np.random.default_rng(1), start=2, least=15)
    assert k == 8 and len(broad_groups(labels, writers, subjects, least=15)) == 8


def test_a_group_is_followed_by_its_best_match_holding_half_its_shared_claims():
    before = {"a": {1, 2, 3, 4}, "b": {5, 6, 7, 8}}
    after = {"x": {1, 2, 3, 9}, "y": {5, 6, 10}, "z": {7, 8, 4, 11}}
    # x: 3 of its 4 overlap claims from a, mutual best -> follows a.
    # y: 2 from b; z: 2 from b, 1 from a; b's best is a tie (y, z) -> the
    # first, y, which holds all its shared claims from b.
    assert follow(before, after) == {"x": "a", "y": "b"}


def test_words_that_set_a_group_apart_rank_first():
    texts = {"t": ["ai images generated", "ai generated art"], "u": ["the art show", "art show opens"]}
    assert distinctive_words(texts, top=2)["t"] == ["ai", "generated"]


def test_a_trend_moves_if_its_share_doubled_or_halved():
    assert moving([0.10, 0.12, 0.09, 0.11]) is False
    assert moving([0.02, 0.03, 0.05]) is True
    assert moving([0.08, 0.03]) is True
