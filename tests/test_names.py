"""Proper names, found by how a corpus writes them (ART-PLAN §10.1)."""
from abductive.names import idea_phrase, proper_names, without_names


def test_a_word_almost_never_written_lowercase_is_a_name():
    fields = ["Picasso painted it", "a show of Picasso", "black paint", "Black artists", "her black dress",
              "ai is everywhere", "the AI boom", "the AI art"]
    names = proper_names(fields, max_lower=0.05)
    assert "picasso" in names
    assert "black" not in names


def test_the_first_word_of_a_field_is_not_counted():
    # "Paint" is capitalised only because it opens the field.
    assert "paint" not in proper_names(["Paint dries", "wet paint"], max_lower=0.05)


def test_names_are_removed_wherever_they_stand_and_capitals_are_kept():
    names = frozenset({"mire", "lee", "moma", "nft"})
    assert without_names("Mire Lee's machine sculptures", names) == "machine sculptures"
    assert without_names("the show at MoMA, briefly", names) == "the show at , briefly"
    assert without_names("an NFT boom", names) == "an NFT boom"


def test_an_idea_phrase_is_about_and_asserts_without_names():
    names = frozenset({"kabakov", "ilya"})
    a = {"about": "Ilya Kabakov", "asserts": "died in May, mourned by Kabakov's students"}
    assert idea_phrase(a, names) == "clustering: : died in May, mourned by students"
