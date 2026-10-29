"""ART-PLAN §10.5: a short name for each trend, written by the local model
(qwen3.6 through Ollama, free) from its distinctive words and sample
claims. Names trends alive in the last two years, and any trend the
episodes test or the forecasts list; keeps names already written.

    uv run python -m evals.name_trends [ID ...]"""
from __future__ import annotations

import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path.home() / "Documents" / "art-press-texts"
MODEL = "qwen3.6:27b"
PROMPT = """These claims come from art criticism in two newspapers. They were grouped together because they share an idea.

Words that set the group apart: {words}

Sample claims:
{claims}

Name the shared idea in 2 to 5 plain words, the way an art critic would name a theme or trend (for example "craft and the handmade", "museums returning looted objects", "art made with AI"). Name the idea, not a person, show or institution. If the claims share only a kind of thing (exhibitions opening, obituaries), name that plainly.

Answer with JSON only: {{"name": "..."}}"""


def name(trend: dict) -> str:
    body = json.dumps({"model": MODEL, "prompt": PROMPT.format(words=", ".join(trend["words"]),
                                                               claims="\n".join(f"- {c}" for c in trend["sample"])),
                       "stream": False, "think": False, "format": "json", "options": {"temperature": 0}}).encode()
    req = urllib.request.Request("http://localhost:11434/api/generate", body, {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as r:
        text = json.load(r)["response"]
    out = json.loads(text)["name"].strip()
    if not out:
        raise ValueError(f"trend {trend['id']}: empty name from {text!r}")
    return out


def main() -> None:
    trends = {t["id"]: t for t in map(json.loads, (ROOT / "trends" / "trends.jsonl").read_text().splitlines())}
    path = ROOT / "trends" / "names.json"
    names = json.loads(path.read_text()) if path.exists() else {}
    wanted = [int(a) for a in sys.argv[1:]] or [t["id"] for t in trends.values() if t["last"] >= 2025]
    for k in wanted:
        if str(k) in names:
            continue
        names[str(k)] = name(trends[k])
        path.write_text(json.dumps(names, indent=0))
        print(f"#{k}: {names[str(k)]}  ({' '.join(trends[k]['words'][:6])})", flush=True)


if __name__ == "__main__":
    main()
