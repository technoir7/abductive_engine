"""Reading each claim for two more parts (ART-PLAN §15.2): what it is about
is a person, a work, an institution or other; and whether it concerns an
artist's life. An answer outside the form is refused, never repaired."""
import pytest

from abductive.reading import ReadingError
from abductive.reading_life import SYSTEM, read_claims

CLAIMS = [("Charmaine Watkiss's early career", "she faced discrimination as a footwear designer"),
          ("Broken Spectre", "is unlike anything I've experienced")]


def _runner(answer):
    seen = {}

    def run(system, user):
        seen["system"], seen["user"] = system, user
        return answer, {"cost_usd": 0.01}
    return run, seen


def test_each_claim_gets_its_subject_and_whether_it_concerns_a_life():
    run, seen = _runner("1 p y\n2 w n")
    got, usage = read_claims(CLAIMS, run)
    assert got == [("person", "yes"), ("work", "no")] and usage == {"cost_usd": 0.01}
    assert seen["system"] == SYSTEM
    assert "1 | about: Charmaine Watkiss's early career | asserts: she faced discrimination" in seen["user"]
    assert "2 | about: Broken Spectre | asserts: is unlike anything" in seen["user"]


def test_the_reader_is_not_shown_who_said_it():
    run, seen = _runner("1 p y\n2 w n")
    read_claims(CLAIMS, run)
    assert "who" not in seen["user"]


@pytest.mark.parametrize("answer", ["1 p y", "1 p y\n2 x n", "1 p y\n2 w maybe", "1 p y\n1 p y\n2 w n",
                                    "1 p y\n2 w n\n3 o n", "Here you go: 1 p y 2 w n"])
def test_an_answer_outside_the_form_is_refused(answer):
    run, _ = _runner(answer)
    with pytest.raises(ReadingError):
        read_claims(CLAIMS, run)


def test_blank_lines_and_code_fences_around_the_answer_are_allowed():
    run, _ = _runner("```\n1 p y\n\n2 w n\n```")
    assert read_claims(CLAIMS, run)[0] == [("person", "yes"), ("work", "no")]
