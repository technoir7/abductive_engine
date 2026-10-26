"""
Reading the art press (ART-PLAN §2): a language model reports what each
article asserts, in a fixed form, and nothing else. It reads; the engine
judges. An answer outside the form is refused (ReadingError), never
repaired, so what the engine is given is what the model said.

The model is called through a `run(system, user) -> (text, usage)`
function, so the reading is tested without one; `claude_runner` runs Claude
Code headless on the user's subscription.
"""
from __future__ import annotations

import json
import subprocess
import tempfile
from dataclasses import dataclass
from typing import Callable, Mapping

from .press import ArtText

FORCES = ("reports", "judges", "predicts", "doubts")
STANCES = ("approval", "disapproval", "neither")

SYSTEM = """You read newspaper art coverage and report what it asserts. You do not interpret beyond the text, and you do not sort claims into themes.

For each article below, list every assertion it makes about the art world: artists, works, exhibitions, institutions, movements, media, the market, critics, audiences. For each give:
- who: who asserts it: the writer as named in the byline, or a person quoted, by name; if no writer is named, "the paper". Never name anyone the text does not name.
- about: what it is about, in the text's own words, naming the person or thing rather than a pronoun
- asserts: what is asserted, a short phrase in the text's own words
- force: one of reports (states a fact), judges (gives a verdict or valuation), predicts (says what will happen), doubts (questions or denies)
- stance: toward the subject: approval, disapproval, or neither

A question the writer asks is not an assertion; do not turn it into one.

Answer with JSON only, no other text: {"articles": [{"id": "<the article's id>", "assertions": [{"who": "...", "about": "...", "asserts": "...", "force": "...", "stance": "..."}]}]}, one entry for every article given, in order. An article that asserts nothing about the art world gets "assertions": []."""

Runner = Callable[[str, str], tuple[str, Mapping]]


class ReadingError(ValueError):
    pass


@dataclass(frozen=True)
class Assertion:
    who: str
    about: str
    asserts: str
    force: str
    stance: str


def _article(t: ArtText) -> str:
    parts = [f"id: {t.id}", f"published: {t.published.isoformat()}", f"byline: {t.byline or '(none)'}",
             f"headline: {t.headline}"]
    if t.summary:
        parts.append(f"summary: {t.summary}")
    if t.body:
        parts.append(f"text: {t.body}")
    return "\n".join(parts)


def _parse(text: str) -> dict:
    """The first JSON object in the answer; a fence or words around it are
    ignored, the object itself is taken as given."""
    start = text.find("{")
    try:
        if start < 0:
            raise json.JSONDecodeError("no object", text, 0)
        return json.JSONDecoder().raw_decode(text, start)[0]
    except json.JSONDecodeError as exc:
        raise ReadingError(f"not JSON: {text[:200]!r}") from exc


def _assertion(raw: Mapping) -> Assertion:
    try:
        a = Assertion(**{k: raw[k] for k in ("who", "about", "asserts", "force", "stance")})
    except (KeyError, TypeError) as exc:
        raise ReadingError(f"assertion outside the form: {raw}") from exc
    if a.force not in FORCES or a.stance not in STANCES or not all(isinstance(v, str) for v in vars(a).values()):
        raise ReadingError(f"assertion outside the form: {raw}")
    return a


def read_batch(texts: list[ArtText], run: Runner) -> tuple[dict[str, list[Assertion]], Mapping]:
    """Each article's assertions by id, and the call's usage."""
    answer, usage = run(SYSTEM, "\n\n---\n\n".join(_article(t) for t in texts))
    try:
        entries = {e["id"]: e["assertions"] for e in _parse(answer)["articles"]}
    except (KeyError, TypeError) as exc:
        raise ReadingError(f"answer outside the form: {answer[:200]!r}") from exc
    missing = [t.id for t in texts if t.id not in entries]
    if missing:
        raise ReadingError(f"articles left out: {missing}")
    return {t.id: [_assertion(a) for a in entries[t.id]] for t in texts}, usage


def claude_runner(model: str = "haiku", effort: str | None = None) -> Runner:
    """Claude Code headless, no tools, run from an empty directory so no
    project instructions are read. Uses the logged-in subscription."""
    def run(system: str, user: str) -> tuple[str, Mapping]:
        cmd = ["claude", "-p", "--model", model, "--system-prompt", system, "--tools", "",
               "--strict-mcp-config", "--no-session-persistence", "--output-format", "json"]
        if effort:
            cmd += ["--effort", effort]
        with tempfile.TemporaryDirectory() as empty:
            out = subprocess.run(cmd + [user], cwd=empty, capture_output=True, text=True, stdin=subprocess.DEVNULL,
                                 timeout=600, check=True)
        result = json.loads(out.stdout)
        if result.get("is_error"):
            raise ReadingError(f"claude: {result.get('result')}")
        usage = dict(result.get("usage") or {}) | {"cost_usd": result.get("total_cost_usd"),
                                                    "duration_ms": result.get("duration_ms")}
        return result["result"], usage
    return run
