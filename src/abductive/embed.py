"""
Assertions as vectors, for grouping them by meaning (ART-PLAN §4), from the
checked copy (grounded/). A local model (nomic-embed-text through Ollama,
official library) embeds what each assertion is about and asserts; vectors
are cut to their first DIMS numbers (the model is trained so the first ones
carry the most) and kept at half precision, so 800,000 assertions take
about 400 MB rather than 2.4 GB.

    uv run python -m abductive.embed --root ~/Documents/art-press-texts

Writes ROOT/vectors/<paper>/<YYYY-MM>.f16 (one row per assertion) and
.keys.jsonl ([article id, index of the assertion in it]); a month is done
once both exist. With --ideas, each claim is embedded with proper names
removed (names.py, ART-PLAN §10.1) into ROOT/ideas/ instead.
"""
from __future__ import annotations

import argparse
import json
import math
import struct
import urllib.request
from pathlib import Path
from typing import Callable, Mapping, Sequence

from .disk import ensure_room
from .names import idea_phrase, proper_names

DIMS = 256
Embedder = Callable[[list[str]], list[list[float]]]


def phrase(a: dict) -> str:
    # nomic-embed-text expects a task prefix; "clustering" is the one for grouping.
    return f"clustering: {a['about']}: {a['asserts']}"


def shorten(v: Sequence[float], dims: int = DIMS) -> list[float]:
    cut = list(v[:dims])
    norm = math.sqrt(sum(x * x for x in cut)) or 1.0
    return [x / norm for x in cut]


def _paths(root: Path, paper: str, year: int, month: int, out: str = "vectors") -> tuple[Path, Path]:
    base = root / out / paper / f"{year}-{month:02d}"
    return base.with_suffix(".f16"), base.with_suffix(".keys.jsonl")


def embed_month(root: Path, paper: str, year: int, month: int, embed: Embedder, dims: int = DIMS,
                text: Callable[[Mapping], str] = phrase, out: str = "vectors") -> int:
    """Embed one month's checked assertions, each as TEXT gives it, into
    ROOT/OUT unless done; returns how many."""
    src = root / "grounded" / paper / f"{year}-{month:02d}.jsonl"
    vec_path, key_path = _paths(root, paper, year, month, out)
    if not src.exists() or (vec_path.exists() and key_path.exists()):
        return 0
    ensure_room(root)
    keys, texts = [], []
    for line in src.read_text().splitlines():
        row = json.loads(line)
        for i, a in enumerate(row["assertions"]):
            keys.append([row["id"], i])
            texts.append(text(a))
    values: list[float] = []
    for k in range(0, len(texts), 100):
        for v in embed(texts[k:k + 100]):
            values.extend(shorten(v, dims))
    vec_path.parent.mkdir(parents=True, exist_ok=True)
    vec_path.write_bytes(struct.pack(f"<{len(values)}e", *values))
    key_path.write_text("".join(json.dumps(k) + "\n" for k in keys))   # written last: marks the month done
    return len(keys)


def read_vectors(root: Path, paper: str, year: int, month: int, dims: int = DIMS, out: str = "vectors"):
    vec_path, key_path = _paths(root, paper, year, month, out)
    keys = [tuple(json.loads(line)) for line in key_path.read_text().splitlines()]
    raw = vec_path.read_bytes()
    values = struct.unpack(f"<{len(raw) // 2}e", raw)
    return keys, [list(values[i * dims:(i + 1) * dims]) for i in range(len(keys))]


def ollama_embedder(model: str = "nomic-embed-text", url: str = "http://localhost:11434/api/embed") -> Embedder:
    def embed(texts: list[str]) -> list[list[float]]:
        body = json.dumps({"model": model, "input": texts}).encode()
        req = urllib.request.Request(url, body, {"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=600) as r:
            return json.load(r)["embeddings"]
    return embed


def main() -> None:
    parser = argparse.ArgumentParser(description="Embed the checked assertions, month by month.")
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--ideas", action="store_true", help="embed with proper names removed, into ROOT/ideas/")
    args = parser.parse_args()
    embed = ollama_embedder()
    sources = sorted((args.root / "grounded").glob("*/*.jsonl"))
    text, out = phrase, "vectors"
    if args.ideas:
        names = proper_names(f for src in sources for line in src.read_text().splitlines()
                             for a in json.loads(line)["assertions"] for f in (a["about"], a["asserts"]))
        print(f"{len(names)} proper names")
        text, out = (lambda a: idea_phrase(a, names)), "ideas"
    total = 0
    for src in sources:
        y, m = map(int, src.stem.split("-"))
        total += embed_month(args.root, src.parent.name, y, m, embed, text=text, out=out)
    print(f"embedded {total} assertions")


if __name__ == "__main__":
    main()
