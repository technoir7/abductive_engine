"""
The art press's texts (ART-PLAN §3): every art article of the Guardian's
`artanddesign` section and of the NYT's articles with subject "Art", with
what each API gives (the Guardian's headline, standfirst, body and byline;
the NYT's headline, abstract, lead paragraph and byline, which is all its
archive has).

Kept as one JSON-lines file per paper and month, outside git (copyright):
a month's file marks it done, so a fetch can stop and resume. The NYT
archive sends every article of a month (about 19 MB); only art is kept.

    uv run python -m abductive.press --out ~/Documents/art-press-texts --paper both

Needs GUARDIAN_API_KEY and NYT_API_KEY in the environment.
"""
from __future__ import annotations

import argparse
import calendar
import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import Optional

FIRST, LAST = (2000, 1), (2026, 9)
_TAG = re.compile(r"<[^>]+>")


@dataclass(frozen=True)
class ArtText:
    paper: str
    id: str
    published: date
    url: str
    headline: str
    summary: str
    body: str
    byline: str = ""   # who wrote it, as the paper gives it; "" when it names no one
    # The editors' tags, as (kind or id, name): the NYT's keywords ("persons",
    # "Kusama, Yayoi"), the Guardian's keyword tags (id, title). Kept for
    # matching artists across sources (POE docs/art-artists-plan.md).
    tags: tuple[tuple[str, str], ...] = ()


def months(first: tuple[int, int], last: tuple[int, int]) -> list[tuple[int, int]]:
    out, (y, m) = [], first
    while (y, m) <= last:
        out.append((y, m))
        y, m = (y, m + 1) if m < 12 else (y + 1, 1)
    return out


def nyt_art(docs: list[dict]) -> list[ArtText]:
    out = []
    for d in docs:
        subjects = {k["value"].strip().lower() for k in d.get("keywords") or []
                    if (k.get("name") or "").lower() == "subject"}
        if "art" in subjects:
            out.append(ArtText("nyt", d["_id"], date.fromisoformat(d["pub_date"][:10]), d.get("web_url") or "",
                               (d.get("headline") or {}).get("main") or "", d.get("abstract") or "",
                               d.get("lead_paragraph") or "", ((d.get("byline") or {}).get("original") or ""),
                               tuple((k.get("name") or "", k.get("value") or "") for k in d.get("keywords") or [])))
    return out


def guardian_art(results: list[dict]) -> list[ArtText]:
    def plain(s: str) -> str:
        return html.unescape(_TAG.sub("", s or "")).strip()
    return [ArtText("guardian", r["id"], date.fromisoformat(r["webPublicationDate"][:10]), r.get("webUrl") or "",
                    plain(r["fields"].get("headline")), plain(r["fields"].get("trailText")),
                    plain(r["fields"].get("bodyText")), plain(r["fields"].get("byline")),
                    tuple((t["id"], t.get("webTitle") or "") for t in r.get("tags") or []))
            for r in results]


def _path(root: Path, paper: str, year: int, month: int) -> Path:
    return root / paper / f"{year}-{month:02d}.jsonl"


def write_month(root: Path, paper: str, year: int, month: int, texts: list[ArtText]) -> None:
    path = _path(root, paper, year, month)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".part")
    tmp.write_text("".join(json.dumps(asdict(t) | {"published": t.published.isoformat()}) + "\n" for t in texts))
    tmp.rename(path)   # a month is done only when whole


def read_month(root: Path, paper: str, year: int, month: int) -> Optional[list[ArtText]]:
    path = _path(root, paper, year, month)
    if not path.exists():
        return None
    return [ArtText(**(r | {"published": date.fromisoformat(r["published"]),
                            "tags": tuple(tuple(t) for t in r.get("tags", ()))}))
            for r in map(json.loads, path.read_text().splitlines())]


def _get(url: str, tries: int = 5) -> dict:
    for i in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=300) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code not in (429, 500, 502, 503, 504):
                raise
        except (urllib.error.URLError, TimeoutError):
            pass
        time.sleep(60 * (i + 1))
    raise RuntimeError("gave up: " + url.split("api-key")[0])


def fetch_nyt(year: int, month: int) -> list[ArtText]:
    key = os.environ["NYT_API_KEY"]
    return nyt_art(_get(f"https://api.nytimes.com/svc/archive/v1/{year}/{month}.json?api-key={key}")["response"]["docs"])


def fetch_guardian(year: int, month: int) -> list[ArtText]:
    key, last, out, page = os.environ["GUARDIAN_API_KEY"], calendar.monthrange(year, month)[1], [], 1
    while True:
        q = urllib.parse.urlencode({"section": "artanddesign", "from-date": f"{year}-{month:02d}-01",
                                    "to-date": f"{year}-{month:02d}-{last}", "page-size": 200, "page": page,
                                    "show-fields": "headline,trailText,bodyText,byline", "show-tags": "keyword",
                                    "api-key": key})
        r = _get("https://content.guardianapis.com/search?" + q)["response"]
        out += guardian_art(r["results"])
        if page >= r.get("pages", 1):
            return out
        page += 1
        time.sleep(1)


# Seconds between months: the NYT allows 5 calls a minute, the Guardian 1 a second.
_PAUSE = {"nyt": 12.0, "guardian": 1.0}
_FETCH = {"nyt": fetch_nyt, "guardian": fetch_guardian}


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch the art press's texts, resumably.")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--paper", choices=["nyt", "guardian", "both"], default="both")
    args = parser.parse_args()
    for paper in (["guardian", "nyt"] if args.paper == "both" else [args.paper]):
        for y, m in months(FIRST, LAST):
            if read_month(args.out, paper, y, m) is not None:
                continue
            texts = _FETCH[paper](y, m)
            write_month(args.out, paper, y, m, texts)
            print(f"{paper} {y}-{m:02d} {len(texts)}", flush=True)
            time.sleep(_PAUSE[paper])


if __name__ == "__main__":
    sys.exit(main())
