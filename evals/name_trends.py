"""ART-PLAN §10.5 and §11: a short name for each trend, written by the
local model (qwen3.6 through Ollama, free) from its distinctive words and
sample claims, and whether it is a theme. Names the given trends, or every
candidate for the lists POE shows (evals/export_trends.py); keeps names
already written.

    uv run python -m evals.name_trends [ID ...]"""
from __future__ import annotations

import json
import sys
import urllib.request
from pathlib import Path

from evals.export_trends import candidate_lists

ROOT = Path.home() / "Documents" / "art-press-texts"
MODEL = "qwen3.6:27b"
PROMPT = """These claims come from art criticism in two newspapers. They were grouped together because they share an idea.

Words that set the group apart: {words}

Sample claims:
{claims}

Name the shared idea in 2 to 5 plain words, the way an art critic would name a theme or trend (for example "craft and the handmade", "museums returning looted objects", "art made with AI"). Name the idea, not a person, show or institution.

Then say which it is:
- "theme": a particular subject, issue, debate or movement that a reader could follow in the news (looted objects, AI, gender, heists, climate, a medium coming back)
- "general": art or the art world in general: artists' role, identity or reputation, critics, styles or movements in general, institutions, exhibitions, prizes, obituaries, a medium in general
- "none": the claims share no idea, only a way of writing

Answer with JSON only: {{"name": "...", "kind": "theme" | "general" | "none"}}"""


def ask(prompt: str) -> dict:
    """The local model's JSON answer to PROMPT (deterministic: temperature 0)."""
    body = json.dumps({"model": MODEL, "prompt": prompt, "stream": False, "think": False, "format": "json",
                       "options": {"temperature": 0}}).encode()
    req = urllib.request.Request("http://localhost:11434/api/generate", body, {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as r:
        return json.loads(json.load(r)["response"])


def name(trend: dict) -> dict:
    out = ask(PROMPT.format(words=", ".join(trend["words"]), claims="\n".join(f"- {c}" for c in trend["sample"])))
    if not out.get("name", "").strip() or out.get("kind") not in ("theme", "general", "none"):
        raise ValueError(f"trend {trend['id']}: bad answer {out!r}")
    return {"name": out["name"].strip(), "kind": out["kind"]}


def main() -> None:
    trends = {t["id"]: t for t in map(json.loads, (ROOT / "trends" / "trends.jsonl").read_text().splitlines())}
    path = ROOT / "trends" / "names.json"
    names = json.loads(path.read_text()) if path.exists() else {}
    wanted = [int(a) for a in sys.argv[1:]] or sorted({t for ts in candidate_lists().values() for t in ts})
    for k in wanted:
        if str(k) in names:
            continue
        names[str(k)] = name(trends[k])
        path.write_text(json.dumps(names, indent=0))
        print(f"#{k}: {names[str(k)]['name']} [{names[str(k)]['kind']}]  ({' '.join(trends[k]['words'][:6])})", flush=True)


if __name__ == "__main__":
    main()
