# The art phase: reading the press

Status: first draft, 2026-10-26, for review. No code until approved.

## 1. Why

POE's replay 15 counted the art press's topic tags month by month and found
no relation it could hold. Counting is the wrong instrument for a
humanities subject: what the press says has to be read before it can be
weighed (EPISTEMOLOGY §9). This phase reads it, and judges what it reads as
the engine judges numbers.

Two strategies, one inside the other:
- **Read, don't count.** A language model reports what each article
  asserts. The engine forms concepts from those assertions and tests them.
- **Explain surprises.** Where the record breaks its pattern, rival
  explanations are formed from what was asserted around it and judged by
  what follows (Peirce: a surprising fact, then the hypothesis that would
  make it unsurprising). Carlo Ginzburg's "evidential paradigm" (*Clues,
  Myths, and the Historical Method*, 1989) is the humanities' own name for
  this: knowledge from clues and particular cases.

## 2. The boundary (EPISTEMOLOGY §9, settled here)

- **The model reads.** For each article, the assertions it makes, in a fixed
  form: who asserts (the critic, the paper, a person quoted), about what
  (an artist, institution, movement, medium, the market, in the text's own
  words), what is asserted (a short phrase in the text's words), its force
  (reports, judges, predicts, doubts) and its stance (approval, disapproval,
  neither). No categories of ours: the model does not sort claims into
  themes we chose.
- **The engine judges.** It groups assertions into concepts, counts and
  grades them under the table of forms, forms connections, keeps rival
  schemes, and gives them up on the evidence. The model never proposes what
  to believe.

## 3. The texts

| Paper | Articles | Text read |
|---|---|---|
| Guardian, `artanddesign`, 2000–2026 | about 33,000 | headline, standfirst, body (Open Platform, non-commercial) |
| NYT, articles tagged Art, 2000–2026 | about 42,000 | headline, abstract, lead paragraph (all the Archive API gives) |

Only the assertions are kept, each with its article id and date; the texts
are discarded once read, for copyright.

## 4. Concepts from assertions

- **Grouping.** Assertions about the same subject with near phrasing are
  one concept's instances. Nearness is measured by a local embedding model,
  with a threshold fixed before the replay. Open question: how to group
  without the grouping becoming the thesis. The test is the random
  control (DESIGN §7): concepts grouped at random must do worse.
- **Degrees.** Each concept, each quarter: how many independent sources
  assert it (quantity), the balance of approval over disapproval (quality),
  read against its own past as POE reads talk.
- **Trust.** A source's predictions are checked against what is asserted
  later; sources whose predictions come true weigh more (Hume, *Enquiry*
  §10).

## 5. Surprises and their explanations

- **What is surprising.** A concept far above its own past, or a measured
  break: the yearly report figures (online share 25% in 2020) and museum
  acquisitions from POE's art data.
- **Rival explanations.** Formed by the engine from the concepts asserted
  in the year before and around the surprise: each rival is "this concept
  bears on that one", the abductive engine's ordinary links.
- **Judgment.** Prequential over testimony: a rival is credited only for
  what it anticipates in the next one to three years' assertions, against
  each concept's own persistence (DESIGN §8). Refuted on decisive evidence,
  as for macro.

## 6. Cost of reading (decision for the user)

About 75,000 articles. Two depths:

| Depth | Read | Tokens in | Tokens out |
|---|---|---|---|
| Light | headline and summary, both papers | about 11 million | about 2–3 million |
| Full | Guardian bodies as well | about 45 million | about 4 million |

Options: a small Claude model through the subscription, the Claude API
(its batch service halves the price), or the local qwen model (free,
slower, less accurate). Whichever is chosen, a pilot first: one year of
both papers (about 3,500 articles), its usage measured, and 50 assertions
checked by hand against their articles for accuracy, before the rest is
read.

### Measured 2026-10-26 (one month of texts, one paragraph read)

- **Download.** Guardian: one month of art articles with full text is
  0.7 MB (131 articles, 800 words each on average); all years about
  0.2 GB. NYT: the Archive API sends every article of the month, 19 MB, of
  which 232 were art (84 words each of headline, abstract and lead); all
  years about 6 GB, once.
- **Claude (Haiku, through Claude Code).** One NYT paragraph: 5 seconds,
  7 assertions, all accurate; about 3,300 tokens in (mostly fixed
  overhead, cached) and 1,150 out (490 of them thinking); Claude Code
  priced it at $0.0012. All 75,000 articles one at a time: about 4 days in
  the background, light on the computer, about $90 at that price; less by
  reading several articles a call.
- **qwen3.6 27B (local).** With thinking: 7 minutes for the same
  paragraph, 6 accurate assertions copied word for word, pronouns left
  unresolved ("about: She"). Without thinking: no assertions at all.
  Reading everything would take about a year of the computer's full
  attention. Not usable here.
- **How often.** Reading is once for the history, then each month's new
  articles (about 300, about half an hour, about $0.40). The assertions are
  kept, so the engine can be rerun on them as often as wanted; reading
  again is needed only if the reading instructions change, so they are
  settled on a pilot first.

### The pilot month (March 2015, read 2026-10-26)

363 articles (131 Guardian full texts, 232 NYT paragraphs), Haiku through
Claude Code, five Guardian or ten NYT articles a call, two calls at once:
19 minutes; 2,655 assertions (Guardian 14.5 an article, NYT 3.3); no
article failed; $0.31 at the price Claude Code reports ($0.0016 a Guardian
article, $0.0004 an NYT one). Of 63 assertions checked by hand against
their articles, all were in the text; two faults found in the first trials
were fixed before the month was read (a writer named from the model's own
knowledge, now given the byline; a rhetorical question reported as a
statement, now forbidden). Low effort was cheaper but merged separate
assertions into one, so normal effort is kept.

Whole corpus, extrapolated: about $70 at that price; about 25 hours with
four calls at once.

### Checked against the text (added 2026-10-26)

A second hand check, of a 2001 review, found two of twenty assertions
adding what the article did not say: a place the model knew ("at
Wapping") and a star rating. Rather than change the instructions partway
through the reading, every assertion is checked mechanically
(`reading.grounded`): each name, number and number-word it uses must be in
its article or byline. About 2% fail (Guardian 2.3%, NYT 1.7% of the first
44,000); a sample of those failing were mostly real additions (a first
name the article never gives, a critic named when the byline names
another, ratings). The raw assertions are kept; analysis reads the checked
copy under `grounded/` (`abductive.ground`).

### Reception by artist (the first concept family, built)

A judgement belongs to an artist when the artist's full name, as Chicago or
Cleveland gives it, is in what it is about (POE `evals/reception.py`).
In the first 17,000 judgements, 15% linked to 482 artists. Replay 17 asks
of these, as of the papers' tags, whether critics' approval comes before
acquisitions; it runs when the reading is done.

### Grouping by meaning (designed 2026-10-26, for review)

Embedding works: claims near each other in nomic-embed-text's space
(official Ollama library, 270 MB, local) share a meaning across articles
and writers. In 2003's Guardian, a claim about Niemeyer's Brasília had as
neighbours three other claims about Niemeyer as a sculptural architect;
one about Letchworth losing its character had claims about the decline of
public design in British towns. Vectors are kept cut to 256 numbers at
half precision, about 400 MB for the corpus.

The design, for review before it is built:
- **Synthesis in time order.** Claims are taken up month by month, as
  published. Each joins the concept whose members it is nearest, if near
  enough (cosine at least θ), or founds a new concept. Nothing later can
  shape an earlier concept (Kant's synthesis of apprehension,
  reproduction and recognition; DESIGN §4).
- **θ fixed before the replay**, on the pilot month only (March 2015, then
  never scored): the value that gives the most concepts asserted in two or
  more articles by different writers. A concept that one article alone
  holds is a paraphrase, not a shared view.
- **Degrees,** per concept per quarter: how many different writers assert
  it (quantity); approval minus disapproval among its judgements
  (quality); each against its own past, as POE reads talk.
- **Then the engine's own work:** concepts become the series the abductive
  engine already handles (schemes, links, rival programmes, refutation;
  DESIGN §§5–7), scored prequentially against each concept's persistence.
- **Random control:** the same claims grouped at random into concepts of
  the same sizes. If those do as well, grouping by meaning added nothing.

## 7. Build order

Each step test first.

1. **Texts.** Fetch one year, read nothing yet.
2. **Pilot reading.** One year: assertions, usage, accuracy. Report back
   before going on.
3. **All years**, at the chosen depth and model.
4. **Concepts** from assertions (grouping, degrees, trust), with the random
   control. Reception by artist is built (above). Next: institutions by
   name the same way (museums' and galleries' names as the papers tag
   them), then what is asserted, grouped by meaning, which needs a local
   embedding model: a download for the user to approve (vetted sources
   only).
5. **Surprises and rival explanations**, scored on what follows.
6. **Replay**, planned first, 2001–2026. The plan:

### The art replay (planned 2026-10-26, before it runs)

- **Series.** Each concept held by at least 5 different writers in at least
  8 different quarters, a rule fixed here: its writers per quarter (how many
  writers asserted it), 2000 Q1 to 2026 Q3. Changes are differences.
- **Periods.** Quarters, as the engine's weeks: one observation each,
  every series observed every quarter (0 writers is an observation).
- **Vocabulary.** Each series' z-score over 4 quarters with cuts at ±0.5
  (high, ordinary, low talk of it), from the engine's fixed table; a
  scheme's links run from one concept's state last quarter to another's
  change, learned by the population as for macro (DESIGN §§5–7).
- **Scored** prequentially from 2003 (three years learned first), in nats
  a quarter, against independence and each series' persistence.
- **Random control.** The same, run on concepts dealt at random from the
  same claims with the same sizes (art_series.shuffled_concepts), five
  deals.
- **Questions.**
  1. Do links between concepts hold, for 4 quarters or more? Which?
  2. Does the engine predict the quarters better than persistence?
  3. Do concepts formed by meaning beat concepts dealt at random?
  4. Surprises: in quarters where a concept's writers jump beyond its
     past (z above 2), which concepts' states the quarter before does the
     engine's proposal name? Listed, with the claims, for reading.
- **Against the design:** links that come and go each quarter; no gain
  over persistence; random concepts doing as well.
