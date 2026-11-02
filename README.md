# Abductive engine

[![CI](https://github.com/technoir7/abductive_engine/actions/workflows/ci.yml/badge.svg)](https://github.com/technoir7/abductive_engine/actions/workflows/ci.yml)

The reading half of a project about how beliefs should be formed and judged.
Its sibling, the [Probabilistic Ontology Engine](https://github.com/technoir7/probabilistic_ontology_engine)
(POE), is given its concepts and forms hypotheses about how they connect. This
engine goes one step back: it forms the concepts too. It began on the macro
economy and turned to art, where the evidence is what critics wrote.

**Live:** art's results appear on the
[Epistemic State Monitor](https://epistemic-monitor-production.up.railway.app)
(the ART_REGIME tab), served by POE.

## What it does for art

1. **Fetches the art press.** Every Guardian `artanddesign` article and every
   NYT article with the subject "Art", January 2000 to September 2026
   (`press.py`). The texts stay outside git.
2. **Reads it in a fixed form.** A language model (Claude Haiku) reports what
   each article asserts: who claims what, about what, with what force
   (reports, judges, predicts, doubts) and stance (approval, disapproval,
   neither); later, each claim's subject and whether it is about an artist's
   life (`reading.py`, `reading_life.py`). An answer outside the form is
   refused, never repaired. The model reads; the engine judges.
3. **Checks the reading.** A claim is kept only if every name and number in
   it appears in its article: 561,133 claims (`ground.py`).
4. **Forms concepts and trends.** Claims become vectors of their meaning (a
   local embedding model), with proper names removed, and are grouped into
   concepts in the order they were published, then into trends followed
   year by year (`synthesis.py`, `names.py`, `trends.py`). A trend needs at
   least 36 writers and 10 subjects over three years. All five episodes fixed
   in advance (NFTs, restitution, Black artists and race, AI-made art,
   graffiti) peak where expected.
5. **Judges cases.** An artist, a concept or a trend is a case; a mechanism
   ("a case in this state this year tends to this outcome next year") is
   judged across every case at once, against each case's own past, with
   controls that deal a feature at random within the year and give each case
   the features of the year after (`cases.py`, `case_engine.py`).
6. **Exports to POE**, which runs the final case engine on artists,
   concepts, trends and four kinds of success (critics approve, more press,
   a museum buys, a place in Artprice's Top 500), and writes the reports
   (`evals/export_*.py`).

What holds so far: the NYT's attention comes with or before museum
acquisitions; a contested debate outlives an uncontested one of the same
size and age; being written about in an argued-over trend predicts every
kind of success but the market. What does not: aggregate talk, links
between particular concepts, controversy about an artist bringing
acquisitions, and life stories as a forecast of anything.

## Documents

- [EPISTEMOLOGY.md](EPISTEMOLOGY.md): the philosophy (Kant's table of forms,
  abduction, testimony, judging across cases, and how a model's writing is
  checked).
- [DESIGN.md](DESIGN.md): the technical design and build order (the macro
  side is paused after step 4).
- [ART-PLAN.md](ART-PLAN.md): every art step, planned in writing before it
  was built or run, with its predictions, results and dated deviations.
- POE's [SNAPSHOT.md](https://github.com/technoir7/probabilistic_ontology_engine/blob/main/SNAPSHOT.md):
  how the three repositories fit together.

## Running

```bash
uv sync
uv run pytest          # 146 tests, under a second
```

The art pipeline needs Guardian and NYT API keys, Claude Code for the
reading, and Ollama for the local models; see ART-PLAN §3–§6. The macro
side reads `data/observations.csv` (FRED series, as POE serves them).
