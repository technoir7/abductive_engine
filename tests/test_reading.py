"""Reading (ART-PLAN §2): the model reports what each article asserts, in a
fixed form; anything outside the form is refused, not repaired."""
import json
from datetime import date

import pytest

from abductive.press import ArtText
from abductive.reading import Assertion, ReadingError, read_batch

A = ArtText("nyt", "nyt://1", date(2015, 3, 20), "u", "A show", "Abs.", "Lead.")
B = ArtText("guardian", "g/2", date(2015, 3, 21), "u", "H", "S", "Body.", "Jonathan Jones")
GOOD = {"who": "the paper", "about": "the show", "asserts": "is at the Guggenheim", "force": "reports", "stance": "neither"}


def fake(answer, usage=None):
    calls = []

    def run(system, user):
        calls.append((system, user))
        return json.dumps({"articles": answer}), usage or {"output_tokens": 10}
    run.calls = calls
    return run


def test_each_article_gets_its_assertions_and_the_call_its_usage():
    run = fake([{"id": "nyt://1", "assertions": [GOOD]}, {"id": "g/2", "assertions": []}], {"output_tokens": 42})
    got, usage = read_batch([A, B], run)
    assert got == {"nyt://1": [Assertion(**GOOD)], "g/2": []}
    assert usage == {"output_tokens": 42}
    user = run.calls[0][1]
    assert "nyt://1" in user and "Lead." in user and "Body." in user and "byline: Jonathan Jones" in user


def test_an_article_left_out_of_the_answer_is_an_error():
    with pytest.raises(ReadingError):
        read_batch([A, B], fake([{"id": "nyt://1", "assertions": []}]))


def test_a_force_or_stance_outside_the_form_is_an_error():
    for bad in ({**GOOD, "force": "suggests"}, {**GOOD, "stance": "mixed"}, {k: v for k, v in GOOD.items() if k != "who"}):
        with pytest.raises(ReadingError):
            read_batch([A], fake([{"id": "nyt://1", "assertions": [bad]}]))


def test_an_answer_that_is_not_json_is_an_error():
    with pytest.raises(ReadingError):
        read_batch([A], lambda s, u: ("Here are the assertions: ...", {}))


def test_json_wrapped_in_a_code_fence_is_accepted():
    body = "```json\n" + json.dumps({"articles": [{"id": "nyt://1", "assertions": []}]}) + "\n```"
    assert read_batch([A], lambda s, u: (body, {}))[0] == {"nyt://1": []}


def test_words_around_the_json_are_ignored_not_the_json_changed():
    body = "Here you go:\n" + json.dumps({"articles": [{"id": "nyt://1", "assertions": [GOOD]}]}) + "\nDone."
    assert read_batch([A], lambda s, u: (body, {}))[0] == {"nyt://1": [Assertion(**GOOD)]}


def test_a_claim_naming_what_the_text_does_not_is_not_grounded():
    from abductive.reading import grounded
    text = ("Keith Haring's series of paintings, The Ten Commandments, hangs in a Victorian pumping station. "
            "Until August 31. Since his death in 1990, Haring has dissolved into the ether of the mass media.")
    ok = Assertion("Jonathan Jones", "Keith Haring", "died in 1990", "reports", "neither")
    place = Assertion("Jonathan Jones", "the Keith Haring exhibition at Wapping", "runs until August 31", "reports", "neither")
    rating = Assertion("Jonathan Jones", "the Keith Haring exhibition", "receives four stars out of five", "judges", "approval")
    paraphrase = Assertion("Jonathan Jones", "Haring's art", "has become blandly invisible in mass media", "judges", "disapproval")
    assert grounded(ok, text, byline="Jonathan Jones")
    assert grounded(paraphrase, text, byline="Jonathan Jones")
    assert not grounded(place, text, byline="Jonathan Jones")      # a place the text does not name
    assert not grounded(rating, text, byline="Jonathan Jones")     # a number the text does not give
    assert not grounded(ok, text, byline="")                       # a writer the text does not name
    assert grounded(Assertion("the paper", "Keith Haring", "died in 1990", "reports", "neither"), text, byline="")


def test_accents_and_a_capital_that_only_starts_a_sentence_are_not_new_names():
    from abductive.reading import grounded
    text = "Late works by Buñuel and Ernst. there is a bed by Emin."
    a = Assertion("the paper", "Bunuel's late work", "There is a bed by Emin", "reports", "neither")
    assert grounded(a, text, byline="")
