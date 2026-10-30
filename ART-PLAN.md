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

**Built 2026-10-26** (`synthesis.py`, `art_series.py`, `evals/run_art.py`),
with two choices made in building, for review:
- **θ = 0.85,** by the rule above, on the Guardian's pilot month alone
  (the NYT's was not yet downloaded): 54 concepts held by two or more
  writers, against 42 at 0.80 and 38 at 0.90.
- **Dormancy:** a concept unasserted for 24 months stops taking claims,
  matching POE's two-year reading of talk, so that each claim is compared
  with live concepts only (thousands, not hundreds of thousands).

On the claims read by then (81,571; Guardian 2000–2007, NYT 2000–2002):
17,307 concepts, 2,105 held by two or more writers. The most widely held
were recognisable debates of the years: Tate Modern's arrival (267
writers), Hockney's claim that old masters painted with lenses (263),
feminism and women artists (211), the New York scene (185). **A weakness:**
a concept's centre moves as it grows, so a few become catch-alls ("the
exhibition", "the state of art"); the ten largest hold 11% of the claims.
Fixed the same evening: a claim must also be within 0.80 of the claim
that founded the concept. Chosen by the same rule as θ (the most concepts
held by two or more writers), on the claims read so far, never on
prediction: 3,023 such concepts against 2,105, and the ten largest hold
5.5% of claims rather than 11%.

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
- **Noted before running:** the engine proposes a link only from 30 or
  more of a series' recent surprises (scheme.MIN_CASES), set for weeks. In
  quarters that is seven and a half years, so only long-lived concepts can
  gain links; the rest are scored on persistence alone. Not changed for
  this replay; if it finds nothing, this is the first suspect.

### Matched control (planned 2026-10-28, before it runs)

The first run's random deals each gave about 6,400 series against the real
concepts' 2,692, because concepts dealt at random spread across the years
and so more pass the 5-writer, 8-quarter rule. To compare like with like:
- each of the five deals again, keeping 2,692 of its chosen series drawn at
  random (`--series 2692`, seeded by the deal);
- the real concepts rerun with each quarter's scores saved, to see whether
  the gain is spread across quarters or comes from a few.
- **Reading:** concepts formed by meaning beat the matched deals if their
  gain over persistence (nats a quarter) is above all five.

**Result (2026-10-28).** Matched deals 0–4, engine minus persistence, nats a
quarter: −0.07, −0.01, −0.21, −0.05, −0.06 (logs `jobs/logs/matched_deal*.log`).
The real concepts' +0.55 is above all five, so it is not the number of
series. But the links it rests on read as coincidences (§8), so the gain is
evidence that meaning-formed concepts change in an orderly way, not that
these links are the order.

## 8. A method for art: cases and mechanisms (2026-10-28)

### What the runs so far show

1. **Aggregates carry no structure.** A month's or quarter's share of
   coverage by topic (POE replays 15–16) is mostly how much was printed and
   chance.
2. **Links between particular concepts are coincidences.** The art replay's
   leader beat persistence in 66 of 95 quarters (+0.55 nats a quarter;
   random concepts −0.02 to −0.68), but its links read as nonsense:
   Clement Greenberg → Ai Weiwei's detention, Dalí → the looting of Iraq's
   museums. A rarely asserted concept's state works as a clock, and the
   child concept's change differs before and after: the engine has found
   that concepts *fade*, through whatever parent marks the time.
3. **Cases pooled under one rule do carry structure.** Replay 17 asks one
   question of 9,665 artists at once and finds a real, ordered relation:
   the NYT's attention to an artist comes with or before Chicago's
   acquisitions (lag 1 +288, same year +266, next year +180 nats; no
   shuffle of 100 as high).

### The method

The humanities reason from particular cases to what holds across them
(Ginzburg's clues; Bourdieu's consecration is a claim about every
career; Moretti, *Graphs, Maps, Trees*, 2005, reads the life cycles of
genres). So:
- **A case** is something with a history in the discourse: an artist, a
  concept (a debate), an institution.
- **Its state each year** is graded from what was asserted about it, by
  the table of forms (D25): quantity (how many writers), quality
  (approval, disapproval, both: contested), relation (both papers, or
  one), modality (asserted as prediction or doubt), and its age.
- **A mechanism** is a hypothesis about every case at once: "a case in
  state F this year tends to be in outcome O next year", e.g. *contested
  concepts last longer*. It is judged prequentially over all cases (each
  year predicted from earlier years only; log Bayes factor against the
  case's own past), as replay 17 judges the press.
- **Controls:** the feature dealt at random among the cases of the same
  year (keeps how common it is, breaks its tie to the case); for order,
  next year's feature as a placebo.
- **Forecasting** is the scored predictions themselves, and, forward, a
  list of cases with their predicted next state and the mechanism behind
  it, checked when the year is in.
- Features are the table's headings applied to every case alike, never
  chosen for an expected answer.

### Test 1: the life of concepts (planned before it runs)

- **Cases.** Every concept (`concepts.jsonl`, all 114,581), from the year
  after its founding while alive (not yet two years unasserted, the
  synthesis rule, which is known at the time). Years 2001–2025; 2026 is
  partial and left out.
- **Outcome.** Next year's different writers: none, one, several.
- **Own past.** This year's writers (none / one / several) and age
  (founded last year / 2–4 years / older).
- **Mechanisms, each alone against own past:** contested (none /
  one-sided / both approval and disapproval this year); both papers this
  year (no / yes); a prediction or doubt asserted this year (no / yes).
- **Controls:** 20 deals of each feature among the same year's cases;
  next-year placebo.
- **Reading:** a mechanism holds if its gain is above all 20 deals and
  above its placebo. Then the holding mechanisms together, and the same on
  artists (test 2: NYT attention, critics' approval, contested, both
  papers → acquisition).

### Test 1 results, as planned (2026-10-28)

114,581 concepts, 263,241 concept-years (2000–2024 states, 2001–2025
outcomes). Every mechanism beat all 20 deals by hundreds of nats:
contested +663 (deals at most −57), both papers +519 (−22), modality +361
(−24). Next year several writers: contested 70% against 23% one-sided and
5% neither; both papers 78% against 8%; prediction or doubt 44% against 10%.
*Deviation:* the planned next-year placebo was dropped before running: a
concept's own feature next year implies its writers next year, the outcome.

### Test 1b: size accounted for finely (planned before it runs)

"Several writers" puts 2 and 200 together, and large concepts are more
often contested and in both papers, so the mechanisms may only measure
size. Test 1b repeats test 1 with the own past graded finely: this year's
writers in doubling bins (0, 1, 2, 3–4, 5–8, 9–16, 17+), the writers so far
in the same bins (standing), and age. A mechanism holds if it still beats
all 20 deals.

### Test 1b results (2026-10-28)

With size graded finely, most of test 1 was size. Contested **+35 nats**
(deals −269 to −320): still positive and far above chance; it costs in
2001–2006 while its finer table is learned and pays in every year from
2007 to 2024 (18 of 18). Both papers −75 and modality −58: above their
deals (they carry some information), but they do not pay for the finer
table they need, so they do not hold as forecasting mechanisms. **So:
a debate praised and condemned in a year outlives one of the same size
and age that is not** (Hirschman's voice; controversy as attention's
engine). The lesson for method: grade a case's own size finely, or any
feature that grows with size will pass for a mechanism.

### Test 3: a forecast of 2026 (planned before it runs)

2026 has not been used. Every concept alive at the end of 2025 is
forecast for 2026 from tables learned on 2000–2024 states only (fine own
past; own past alone, and with contested). Scored on its writers in
January–September 2026, all that exists, so every forecast expects more
than nine months bring; the comparison between the two forecasts stays
fair. Reading: contested holds forward if its 2026 gain is positive and
above 20 deals. Listed for reading: the 15 concepts given the highest
chance of several writers in 2026, with what happened.

### Test 2: artists' discourse mechanisms (planned before it runs)

Replay 17's panel (9,665 artists), POE `evals/replay17.py`, target museum
acquisitions, own past as in replay 17, with a new signal: contested (in a
year, critics both approve and disapprove of the artist). Read as replay
17: shuffles of each artist's years, and the next-year placebo (valid
here: the feature is the press's, the outcome the museums').

### Test 3 results (2026-10-28)

9,896 concepts alive at the end of 2025. Contested's gain on 2026: **+2.0
nats** (20 deals: at most +0.4, mean −3.0), so it holds forward. Of the
1,425 concepts forecast more likely than not to have several writers, 882
did in nine months; 145 not so forecast did. The most confident forecasts
are catch-all concepts ("the exhibition", "art", 1,000+ claims): trivial
forecasts, and a sign that the anchor rule (0.80) has not stopped all
catch-alls.

### Test 2 results (2026-10-28)

Critics contested about an artist (1,463 artist-years, 576 artists) →
museum acquisitions: +1.5 nats, within its shuffles (−1.7 to +17.3);
Chicago −15, Cleveland −25. Museums do not follow controversy.

### Test 4: new cells start from what is known (planned before it runs)

A feature splits each own-past cell; under a uniform Dirichlet(1) prior
each new cell starts knowing nothing, so a feature with real but weak
information pays a learning cost it may never earn back (both papers,
modality in 1b). Test 4 gives each split cell the own-past cell's
prediction as its prior, with weight 3 (the uniform prior's weight, so
no stronger): p = (n_y + 3 p_own(y)) / (n + 3). Fixed here, not tuned.
Rerun 1b's three features, then the three together. Reading as 1b.
*Amended before running, from the unit tests:* the split cell's prior
counts each case twice (in its cell and in the own-past cell), which made
pure noise "pay" (+161 nats on a test panel). The baseline is therefore
the same estimator with the feature left out, so only the feature
differs; noise then costs a little and never pays.

### Test 4 results (2026-10-28)

With split cells starting from the own-past cell, and the baseline the
same estimator (so sharper, and harder to beat): contested **+12.7 nats**
(deals at most −259), both papers −119 (deals at most −99: not above
them), modality −90 (above deals, still not paying), all three together
−288 (positive in 4 of 24 years). Backoff does not rescue the weak
features; contested remains the one concept mechanism that holds.

### What the method has found so far

- **Holds:** the NYT's attention comes with or before Chicago's
  acquisitions (replay 17, 9,665 artists); a contested debate outlives an
  uncontested one of the same size and age (every year since 2007, and
  forward on 2026).
- **Does not hold:** aggregate talk (replays 15–16); links between
  particular concepts; the Guardian or critics' approval leading museums;
  controversy about an artist bringing acquisitions; papers and modality
  as concept mechanisms once size is graded finely.
- **Method, as it now stands:** cases, not aggregates; one hypothesis
  across all cases; prequential log Bayes factor against the case's own
  past graded finely; controls by dealing the feature within the year
  (meaning), shuffling a case's years (fame), and the next-year placebo
  when feature and outcome come from different bodies (order).

## 9. The engine on cases (planned 2026-10-28, before it is built)

The engine's method (DESIGN §§5–7): rival schemes kept side by side,
each judged prequentially, a leader that changes only when a rival is
decisively ahead, and every change recorded. On cases:
- **A scheme** is a set of mechanisms (features), each case's outcome
  predicted from its own past and those features (backoff tables, test 4).
- **The population** is every subset of the feature pool (3 features for
  concepts: 8 schemes; 4 for artists: 16). With so few, all are kept
  alive; proposing from surprises is needed only for larger pools.
- **Leadership:** evidence between two schemes is their decayed sum of
  yearly log score differences, half-life 5 years (the art world's slower
  clock; macro uses weeks). The leader changes when a rival is ahead by
  more than 3 nats (Jeffreys' "strong"); the incumbent keeps ties. Each
  change is a shift, read as a change in what drives the case.
- **The engine's forecast** each year is the leader's, scored against own
  past alone.
- **Runs:** concepts (fine own past; contested, both papers, modality) and
  artists (own past as replay 17; NYT, Guardian, approval, contested last
  year → museum acquisitions).
- **Reading:** which mechanisms lead, when the leader changes, and whether
  the engine's forecast beats own past. Against the design: a leader that
  changes every year, or an engine worse than own past.

### §9 results (2026-10-28)

- **Concepts** (263,241 concept-years; pool contested, both papers,
  modality; 8 schemes): own past leads 2001–2013; **one shift, in 2014, to
  contested**, held to the end. From then the engine beats own past by
  +38 nats (8 of 10 years). Both papers and modality never lead.
- **Artists** (241,625 artist-years, POE `evals/artist_records.py`; pool
  NYT, Guardian (from 2010), approval, contested last year → museum
  acquisitions; 16 schemes): NYT and contested lead in 2001–2002 on little
  evidence, then **NYT alone from 2003 to the end**; the engine beats the
  artist's own acquisition history in every year from 2002, +275 nats in
  all. The Guardian, critics' approval and controversy never join it.
- Against the design: neither leader flickers (two and one shifts in
  24 years), and the engine never does worse than own past over a run.

## 10. Trends (planned 2026-10-29, before it is built or run)

**Why.** The user read the art report and asked which *trends* are
contested (craft revival, AI, identity, activism). The engine cannot say:
its concepts (§4) are about 10,000 small topics ("Lord Bath's stolen
Titian", "the Arena Homme+ issue"), because claims were grouped by what
they are about, a name first. Trends appear only as scraps ("craft" twice,
"NFTs" twice, AI never). Two flaws to avoid in a coarser grouping: banal
groups ("museums", "painting", "the market") and young trends (AI art)
swallowed by old groups or too new to judge.

**1. Group by the idea, not the name.** Each claim is embedded again
(nomic-embed-text, local) as "about: asserts" with proper names removed. A
word is a proper name if, past the first word of its field, it is written
lowercase in under 5% of its uses in the whole corpus (measured
2026-10-29: Picasso, Tate, MoMA, Benin 0%; black 60%, indigenous 16%,
impressionism 49%, craft 85%). Words in capitals (AI, NFT) are kept: as
often terms as names. "Mire Lee's machine sculptures" keeps "machine
sculptures"; "Ilya Kabakov: died in May" keeps "died in May".

**2. Group each period by itself.** Every year Y, the claims of Y−2 to Y
are grouped by spherical k-means; the claims of Y take their group from
Y's grouping. So a claim is grouped by what was written up to the end of
its year, never later, and a new idea forms its own group in the years it
is written about instead of joining one formed decades earlier.

**3. A trend is broad.** A group counts as a trend if, in its three years,
at least 10 different writers make its claims about at least 10 different
subjects (distinct "about" texts): not one critic's hobby horse, not one
story. Each year's k is the one giving the most such groups, searched by
doubling from 50 until the count falls (the same kind of rule as θ: most
shared groups, never chosen on prediction).

**4. Trends are followed across years.** Year Y's group B continues year
Y−1's group A when they are each other's best match by shared claims (the
two groupings share two years) and A holds at least half of B's shared
claims. A trend is a chain of such groups.

**5. Named by what sets it apart.** Each trend's words are ranked by how
much more common they are in its claims than in all claims; the local
model (qwen3.6, free) writes a 2–5 word name from the top words and 15
claims. Names are checked by reading claims before they are shown.

**6. Background or moving.** By its share of all writers each year: a
trend whose share has at least doubled or halved at some point is moving;
otherwise it is background ("museums", if it is steady). Background trends
stay in the data and in the engine; the report lists moving ones.

**7. The engine on trends, by quarter.** Cases are trends; steps are
quarters, 2000 Q1 to 2026 Q3, the open quarter (forecast: 2026 Q4).
- Own past: writers this quarter and over the previous four, in doubling
  bins, and age (first year, up to 3 years, older).
- Outcome: next quarter's writers fall a doubling bin or more, hold, or
  rise a bin or more.
- Features (pool as for concepts): contested (the minority side's share of
  approving and disapproving judgements), both papers (the smaller
  paper's share of writers), modality (share of claims that predict or
  doubt). Each is 0 when absent, else 1 or 2 by whether it is below or
  above that quarter's median among trends that have it.
- The case engine (§9) with a 5-year half-life, i.e. 20 quarters.
- Young trends are forecast by the leading mechanism, learned on all
  trends; the report flags trends with under 3 years of claims.

**Checks.**
- *Random grouping:* claims dealt at random into trends within each year,
  sizes kept, run through the same engine. Real trends must gain more over
  own past than all five deals.
- *Random features:* the leader's features dealt among each quarter's
  trends, five deals, as replay 18.
- *Known episodes, a test only, never an input.* Written down now, before
  grouping. Each should appear as a trend whose distinctive words name it
  and whose share peaks in the years given:
  1. NFTs and crypto art: peak 2021–2022.
  2. Return of looted objects (Benin Bronzes, restitution): rising from
     2018, peak 2019–2023.
  3. Black artists and race in the art world: peak 2020–2022.
  4. AI-made art: rising from 2022, peak 2023 or later.
  5. Street art and Banksy: peak before 2015 (a pre-2020 control).
  A miss is reported, not fixed by changing the rules to find it.
  Operationally: a trend matches an episode if one of the episode's words
  is among its 10 most distinctive words; it passes if its share of
  writers peaks in the years given. Words, fixed before grouping: (1) nft,
  nfts, crypto; (2) restitution, looted, repatriation, bronzes; (3) black,
  race, racial, racism; (4) ai; (5) street, graffiti.
- **Against the design:** trends that read as kinds of thing ("exhibition
  openings"), a handful of giant groups, or episodes found only as
  scattered small groups.
- **Order:** grouping, names and episodes are shown to the user before
  anything goes into POE or the app.

### §10 deviations, decided on a pilot before any prediction (2026-10-29)

Pilot: the Guardian's claims 2000–2004 (idea vectors), grouping only.
1. **The bar for a broad group, 10 writers → 36.** At 10, "most broad
   groups" picks groups of about 20 claims (k = 800 for 15,000 claims):
   fragments, not trends. 36 writers in three years is three a quarter on
   average, the least for the engine to see a trend rise or fall by
   doubling bins. Subjects stay at 10. Groups then read as themes ("young
   artists, new generation, YBAs", "war, photographs, soldiers",
   "materials, bronze, plastic, glass"). Stability (two groupings of
   overlapping years agreeing) was tried as the rule instead and rejected:
   it always prefers the fewest groups (k = 25: "painting", "exhibition").
2. **Each year's grouping starts from last year's centres** (ordered by how
   many of this year's claims each draws), new centres seeded by k-means++.
   Grouped afresh, only 42% of broad groups were followed into the next
   year, so trends would break at year ends and look like deaths; started
   from last year's, 68%. Still causal: last year's centres were formed
   from claims before.

### §10 results, quarterly (2026-10-29)

955 trends (506,308 of 561,133 claims), 52,969 trend-quarters judged.
- **No mechanism holds.** Against own past over all quarters: contested
  −118 nats, modality −149, both papers −176; every combination worse.
  The leader is own past from 2003 Q3 on; engine − own past −12.6 nats.
- **Random groupings** (five): −19.9, −7.9, +1.9, −20.6, −12.2. Real
  trends are not distinguishable from them on this test.
- **Known episodes:** 3 of 5 pass. NFTs (peak 2022), Black artists and
  race (peaks 2020–2022), graffiti (peak 2006). Misses: AI art is a trend
  that rose sharply from 2022 (claims 8 in 2020, 92 in 2023) but is
  grouped with robots and machines talk from 2009, whose share peaked in
  2012; restitution is found ("looted antiquities, returned", peak 2003,
  Iraq) but the Benin Bronzes years are not its peak.

### Test 10b: a year ahead (planned 2026-10-29, before it runs)

Concepts' finding (contested → taken up again) was judged a year ahead; a
quarter may be too short for trends of a few writers a quarter. One rerun,
nothing else changed but the step: years ending in September (so the open
year, October 2025 to September 2026, is complete), own past this year
and last, outcome next year's writers falling, holding or rising a
doubling bin, half-life 5 years, the same five random groupings and
feature deals. Whatever it shows is reported; no further horizons.

### Test 10b result, and two faults found reading it (2026-10-29)

**Result as planned:** a year ahead, no mechanism holds either (contested
−79 nats, modality −72, both papers −65; random groupings −7.8 to +6.2).
Reading the open year's lists showed two faults in the build, which make
both runs unfair; fixed and both rerun once, as below, with nothing else
changed:
1. **Trends broken by k changing.** Each year's k came from a doubling
   grid, so it jumped (800 → 400 in 2026, whose window is nine months
   short; also 2006, 2007, 2009, 2015), dropping half the centres at once:
   hundreds of trends "died" and were "born" again in one year. Now k is
   the window's claims over 81, the median claims per group of the rule's
   own 27 yearly choices, so k moves smoothly and only the centres that
   draw the fewest claims are dropped (deviation 3).
2. **The rise/fall scale was capped.** Doubling bins stop at 17+ writers,
   so a trend with 17 or more writers could not rise; a year ahead most
   trends are there. Trend bins are now uncapped, own past and outcome.

### §10 results after the two fixes (2026-10-29)

814 trends (520,532 of 561,133 claims); k moves smoothly (699 in 2025, 603
in 2026).
- **Known episodes: 5 of 5 pass.** NFTs (peaks 2021, 2022); restitution
  and repatriation (peak 2021); Black artists and race (peak 2020, and
  2022); AI-made art, now its own trend (broad from 2025, peak 2025);
  graffiti (peak 2006). The fixes were made for the faults above, not for
  the misses, but AI and restitution changed with them; read accordingly.
- **No mechanism holds, a quarter or a year ahead.** Quarterly: contested
  −159 nats, modality −192, both papers −220; engine − own past −9.0
  (random groupings −9.5 to −20.1). Yearly: contested −96, modality −86,
  both papers −83; −23.8 (random groupings −13.0 to −32.0). Own past leads
  from 2004 (quarterly) and 2005 (yearly) to the end.
- **Reading.** Disagreement keeps a small topic in the press (concepts,
  §9) and press coverage leads museum buying (artists), but no sign in how
  critics write about a trend tells whether the whole trend grows. Trends
  are for describing the present (what is argued over, what is growing),
  forecast by their own past only.

## 11. Trends shown in POE (planned 2026-10-29, before it is built)

The user agreed to show trends on POE's art tab and in its report, and asked
why AI was absent from the first lists. Display only: nothing here feeds a
forecast or a test.

**Why AI was absent (measured before this plan).** AI has its own trend
(#1977), but the first lists kept trends with 15+ writers this year (AI has
12), and AI's share is falling (critics writing on it: 2.9% in the year to
Sep 2023, 1.7% now), so it is not "growing". In the papers' art pages AI
is a modest topic: about 5% of Guardian art articles mention it since 2023
and 1–3% are about it; NYT art articles hardly do (under 1%), partly
because its archive gives only the lead paragraph and AI-art stories are
often filed outside "Art". The lists below are chosen to show what is new,
not to bring AI in; that AI then appears under "new" is a consequence, said
here because the rules were set after seeing it was missing.

**Period.** The open year runs October 2025 to September 2026 ("this
year", as in Test 10b), set against the three years to September before.

**Population.** Trends with at least 12 writers this year: the breadth
floor (36 writers over three years) for one year.

**Names.** The local model names each candidate again with a sharper
question: "theme" only for a particular subject, issue, debate or movement
that could be followed in the news; "general" for art or the art world in
general (artists' role or reputation, critics, styles, institutions,
exhibitions, a medium in general); "none" for no shared idea. Lists show
themes only. Names are read against claims before they are shown.

**Lists**, each up to 12, a trend may be in more than one:
1. **New**: broad for the first time in 2021 or later, by writers this year.
2. **Growing**: this year's share of writers at least 1.5 times its
   average share over the three years before (new this year counts), by
   that ratio.
3. **Fading**: this year's share at most half its highest share in the
   three years before, which had 12+ writers, by that highest share.
4. **Argued over**: at least 10 verdicts this year (approval or
   disapproval), by the minority side's share of verdicts.

Each trend shown carries its name, writers and share each year, the papers
it is in, its top words and eight of this year's claims (three at
first; eight from 2026-10-29, so the report can say what critics argued).

**The finding goes with them.** The trends also go to POE as a third case
set (years to September, as Test 10b, outcome "holds or grows next year")
so POE's own case engine judges whether a mechanism predicts a trend's
growth; per §10 it should find none. The report must say that the lists
describe the present and are not forecasts.

### §11 deviations, decided on reading the first lists (2026-10-29)

1. **No cap on a list.** AI is the 13th new theme by writers, one past the
   cap of 12. The cap was a display choice, so lists now keep every theme
   and the panel shows 12 with the rest on request; the report gets the
   first 8. Changed after seeing AI fall just past the cap, said so here.
2. **Names checked by rule, not by eye.** Reading three claims of this year
   showed several young groups held together by phrasing, not idea ("art in
   storage and display": a maquette studio, a storage unit, a coin-slot
   piece; "art and warfare": an alarm system, an earthquake, an arson
   attack). Each theme on a list is checked: the local model is given its
   name and ten of this year's claims (drawn at random, seed 0) and says
   which are about it. A trend is listed only if at least half fit.
3. **A theme silent this year** (it can still be fading) has no claims of
   this year to check, so its name is checked on its biggest year of the
   three before. Found when the check reached one.
4. **One trend per name.** The grouping sometimes hands an idea to a new
   trend number (food and art: one trend 2.1% → 0% while another rises
   0% → 2.3% in 2024), so it showed as both new and fading, and some names
   came twice. Each list keeps the first trend of each name, and a trend
   leaves "fading" when a trend of the same name has 12+ writers this year
   (it carries on under another number). The names are the local model's,
   so this merges only what it called the same.

## 12. The work most likely to succeed now (planned 2026-10-29, before it is built or run)

The user asked to use the analysis to describe "the ideal work of art most
likely to succeed today", knowing the terms need defining. This section
defines them, says what is tested, and fixes the predictions before any run.
Nothing is built until the user has read it.

### 12.1 Terms

- **Success** is four things, kept apart, because the fields that consecrate
  art can disagree (Bourdieu: critics' esteem and the market can pull in
  opposite directions). Each is an outcome for an artist the year after:
  1. *Critics approve*: approving verdicts about the artist next year
     (none, one, several).
  2. *More press*: articles naming the artist next year, in either paper
     (none, one, several).
  3. *Museum buys*: works acquired by Chicago or Cleveland next year (the
     existing artists case set).
  4. *Market*: the artist's place in Artprice's yearly Top 500 artists by
     auction turnover next year (not listed / ranks 101–500 / top 100, in
     either the all-artists or the contemporary ranking), from Artprice's
     free reports (§12.7). Only years with a table are cases; a gap year is
     missing, never "not listed". Claims in the press that report a sale or
     price (about 7,700, some 250 a year) are kept as the market as critics
     see it, for the market report's description, not as an outcome.
- **A work** is described, not observed: the engine's cases are artists, and
  a work is known through what critics said about it (its subject, the
  trends its claims fall in, its medium from the papers' own tags, the tone
  of the verdicts).
- **Today** is the year to September 2026, as in §11. The portrait is for
  the year after.

### 12.2 Step 1: what critics rewarded this year (description only)

For the year to September 2026: approvals against disapprovals by trend (all
trends with at least 10 verdicts, named as in §11) and by medium (the
papers' tags), with a sample of approved and of disapproved claims for each.
No forecast is drawn from it; it gives the portrait its detail.

### 12.3 Step 2: what an artist's coverage predicts (the test)

Cases: every artist in the artists panel (museum-acquired, ~9,700), by year
2000–2025, as in replay 18. Features of an artist's year, from the claims
whose subject names them (reception.py's rule), each graded none / one /
several claims:
- *in a new trend*, *in a growing trend*, *in a fading trend*, *in an argued
  trend*: the §11 list rules applied to every year, not only 2026, to all
  trends (the theme filter needs names, which only 2026's candidates have);
- *painting*, *photography*, *sculpture*: articles naming the artist that
  carry the paper's tag for that medium;
- *NYT coverage*: the existing leader for museum buying, so a new feature
  must do better than what is already known.
Own past, graded finely (doubling bins): the outcome this year and the
years before. Each of the four outcomes is its own case set,
judged by the case engine (every subset of the eight features a rival,
5-year half-life, shift at 3 nats), with the usual controls: each feature
dealt at random among the year's artists (5 deals), and a placebo using the
feature's value from the year after instead of this one.

**Predictions, fixed before the run:**
- Museum buys: NYT coverage stays the leader; no trend or medium feature
  adds 3 nats over it.
- More press: own past (already in the press) does most of the work; NYT
  coverage adds; trend features add little, since trends themselves are not
  predictable (§10).
- Critics approve: being in an argued trend may lower the chance of
  approval and raise disapproval; no confident prediction for media.
- Market as reported: NYT coverage leads (the Times reports sales of the
  artists it covers); trend and medium features add little.
Whatever comes out is reported, including no gain anywhere.

### 12.4 Step 3: the portraits

One full report for each kind of success (critics approve, more press,
museum buys, market as reported), each written by the POE report model
from the engine's findings only, as the trend-list reports are: for that
kind of success, what the leading mechanism favours (which
features, how strongly, since when, and the artists it raises most); where
the kinds agree and where they pull apart; and step 1's detail of what
critics rewarded this year, labelled as description. Where nothing beat own
past, the portrait says the honest answer is "no feature of the work
helps; what helps is already being written about". It is told to use only
what is in the data. No image.

### 12.5 Where it shows

A "success" panel on POE's art tab: four columns (one per kind of success,
market labelled "as the press reports it"), each with its leader, gain over
own past, the features that help, and a button that opens its full report;
step 1's bars above them. Reports refresh like the other reports. The three success case sets are kept apart from the
existing case panels (artists, concepts, trends) so those stay as they are.

### 12.6 Cost

All local, except four written reports on the server (under a cent each). Building
records: minutes. Each case set: 256 rival schemes over ~250,000
artist-years; estimated under half an hour each.

### 12.7 Real market data: options found (2026-10-29), nothing bought

Every source needs an account the user would make; Claude makes none.
- AuctionAsk API: lots by artist with price realised and date, 5.4M records
  from 200+ houses; auction results only on the $99/month tier (50,000
  requests, enough for the panel's ~9,700 artists in one month); years
  covered and terms on storing data not stated, to check first.
- Art Market API: auction results by artist over about 20 years; no prices
  published.
- TheBasis.Art: free per-artist statistics; single prices metered ($19 for
  50), too few for 9,700 artists; API pricing not published.
- Altfn Data: 4.1M records 1989–2026, bulk download; enterprise pricing.
- Artnet, Artprice: largest, by subscription; no bulk use.
- Artsy: public API being retired.
- Free research sets: Princeton (34,200 sales, 590 living artists,
  1996–2012), too narrow for the panel.
- **Reports already held** (~/Documents/art-market-reports/, read
  2026-10-29). Art Basel & UBS 2017–2025: yearly market shares by medium
  (dealers and auctions, by price band), female artists' share of sales and
  of artists shown, established against emerging; no named artists. Hiscox
  Artist Top 100, 2024 edition: auction sales of works made after 2000 at
  Christie's, Sotheby's and Phillips, 2019–2023, with named artists (top
  fives by value, under-45s, women, lots; a full profile of the top
  artist); one edition only.
  Too few years and artists for the case engine (it needs many cases each
  year), so they are used as **checks and context, not outcomes**: the
  market report sets the press's picture against Art Basel's medium and
  gender shares for the same years, and against whether Hiscox's named
  top artists are the ones the press reports selling. Figures are read
  first-print and dated to each report's publication, as in POE's
  report_figures.csv. Other Hiscox editions are free from Hiscox's site;
  fetched only if the user agrees.
- **Artprice, free reports (downloaded 2026-10-29 from imgpublic.artprice.com
  to ~/Documents/art-market-reports/artprice/, outside git).** Each annual
  report ends with the Top 500 artists by auction turnover (rank, name,
  dates, turnover; recent ones also lots sold and unsold and best price),
  and each contemporary report (July to June, artists born after 1945) a
  Top 500 of its own. Read by POE evals/artprice.py, keeping a row only
  when it reads cleanly and its turnover is no higher than the rank above:
  all artists 2009 (498 of 500 ranks), 2010 (428), 2014 (415), 2015 (416),
  2018–2025 (491–499); contemporary 2015 (460), 2019–2021 and 2023–2026
  (496–500). Unusable: 2011 (its text does not extract), contemporary 2022
  (199 rows, almost none matching any museum artist, so misread). No free
  report found for 2012–2013 or 2016–2017. About 140–190 of each year's
  all-artists 500 match an artist the two museums acquired (by name in
  any order and birth year), and about 100 of the contemporary 500; most of
  the rest are artists neither museum collects (many Chinese). So the
  market outcome covers the market's top, for museum-collected artists
  only, with gaps.
- Hiscox Artist Top 100, 2023 edition (French, from hiscox.fr) added; no
  2025 edition found at a free address. Used as a check only.
- Artsy's public API: still up while being retired, but it needs a
  developer account (the user's to make), its documented resources are
  for Artsy's own live auctions rather than prices realised, and it may go
  without notice. Not used.

### §9 amended: combined mechanisms back off to their parts (2026-10-29, before any rerun)

The user noticed that "NYT coverage" beat "NYT + Guardian", and every
combination lost to its parts. The cause is the backoff: a scheme's cells
started from each case's own past alone, so a combined scheme had to learn
the NYT effect again inside every finer cell, from nothing, and lost to
NYT alone whatever the Guardian added. A combination now starts each cell
from the average prediction of the schemes with one feature fewer (the
lattice of its parts, down to own past), with the same weight as before.
A feature that adds nothing then costs next to nothing; one that adds
information adds it. Everything else stays: scoring, half-life, the
3-nat shift, the controls. All case sets are rerun (artists, concepts,
trends, yearly and quarterly) and their results replaced, the old ones
kept in the record above. Expected: combinations come close to their best
part, so leaders may become combinations, and some gains change.

**Amended again, the same day, before any rerun on real data.** Two fixes
of the count tables were tried on made-up cases and rejected:
(1) cells starting from their parts' prediction counted the same cases
twice, so on near-certain outcomes "f + noise" beat "f" by 31 nats;
(2) weighing, in each cell, "follow the parts" against the cell's own
counts (context-tree weighting) cut what a useless feature costs by 40–80%
but let deeper combinations win on lucky runs, since a mixture of mixtures
is not one model. The question "does X add anything beyond NYT?" is the
standard question for an additive model, so mechanisms now combine
additively: each scheme is a multinomial logistic model of next year's
outcome on each case's own past (one term per own-past grade, as the
tables had) plus one term per mechanism level, fitted each year on the
years before only (L2 prior: sd 3 on own-past terms, sd 1 on mechanism
terms), scored on the year, as before. A useless mechanism gets a term
near zero and costs next to nothing; a useful one shows its size and sign
(helps or hurts), which the portraits need. What is lost: interactions
(two mechanisms mattering only together) are caught only in part. A
combination may lead only when it stands 3 nats ahead of each of its
parts. Everything else (standing, half-life, shift, controls) is as
before. Both engines are run on artists, concepts and trends and compared
before either replaces the other in POE.

### §9 amended: results with the additive engine (2026-10-29)

Run in POE (services/cases.py) on the shipped case sets, yearly:
- Artists: NYT + critics' approval leads from 2023 (engine − own past
  +223 nats over 2002–2024). Alone: NYT +218, approval adds about 23,
  Guardian about 2, contested about 0. History of the leader: NYT from
  2003, NYT + approval from 2009, all four from 2016, NYT + approval from
  2023. The tables had NYT alone, +177.
- Concepts: contested + both papers + modality from 2002 (engine +153; the
  triple +779 over all years; both papers alone +509, modality +191,
  contested +168). The tables had contested alone (+38) and scored both
  papers −119: the clearest case of the flaw.
- Trends: nothing holds over the years (engine −0.3; every rival −17 to
  −2); contested has stood 3 nats ahead only since 2024.
- Control: each feature dealt at random among the year's cases, three
  deals: −61 to +10 nats for every feature, against the hundreds above.
Not yet rerun: the quarterly trends and the single-mechanism judgements in
this repo (cases.judge, case_engine.py), which still use tables; the
yearly trends above give the same finding.

### §12 deviations (2026-10-29)

1. **Fewer control runs.** Each feature dealt at random 5 times for all
   eight features and four outcomes is 160 runs of 256 rival models each
   (about 100 s to 5 min a run). Instead: each feature of each outcome's
   leader dealt 3 times, plus the next-year placebo, on 8 cores (about an
   hour).
2. **A market case needs a table this year and next.** The first run gave
   the market +1,004 nats for growing + argued trends + sculpture + NYT. In
   a year without a table (2013, 2017) the artist's current place is
   unknown, and press coverage can stand in for it (the famous are written
   about), which is a leak, not a finding. Found on seeing that result,
   so said here; the market cases are now the years 2009, 2014 and 2018–2024
   (open: 2025).
3. **A market case also needs a table some year before.** The run with
   controls gave the market's leader (argued trend + sculpture + NYT) +384
   nats as a rival set but the engine only +31. Almost all of the gap came
   from 2014, the first scored year: the only year learned before it was
   2009, when no artist had an earlier table, so the own-past model had
   never seen a known past place and the press features stood in for it,
   as in deviation 2. The leader was chosen on that windfall. Found on
   reading the result, so said here; 2009 is now dropped as a market case
   (it has no earlier table), so 2014 is learned only and 2018–2024 are
   scored. The market alone was rerun; the first run's summary is kept
   (success/market_before_dev3.json).
4. **Years start at 2003, not 2000.** The trend features need the §11
   lists, which start in 2003; the four case sets run 2003–2025.
5. **The placebo is no test for approval and press.** An approval is a
   claim, so next year's trend claims include next year's approvals, and
   next year's NYT and medium-tagged articles are next year's press: the
   year-after features count part of the outcome and are bound to win
   (they did, by about 11,000 and 17,000 nats). The plan missed this. For
   those two the dealt control and the gain over own past carry the case,
   and the panel and reports say so; the placebo stands for museum buys
   and the market, where the outcome is counted apart from the press.

### §12 results (2026-10-29)

Run in POE (evals/success_run.py) on the four case sets, 2003–2024 scored
(market 2018–2024), every rival the 255 sets of the eight features. "Adds"
is how much the engine loses when that feature is dealt at random (3
deals, all alike to a decimal).
- **Critics approve**: growing + argued trend + painting + NYT, since
  2022, +342 nats over own past. Argued adds 131, NYT 62, growing 37,
  painting 2. All push up (argued +0.89 on the log-odds for one claim).
  Placebo not a test (deviation 5). Prediction (argued trends lower
  approval) wrong: being argued over goes with more approvals next year.
- **More press**: new + growing + argued trend + NYT, since 2025, +143.
  Argued adds 61, growing 17, NYT 6, new 0 (it joined the leader in the
  last year, so no scored year used it). Pushes: argued +0.59, growing
  +0.35; new trend −0.85 and NYT −0.59 (with the same press this year,
  claims in a new trend or a NYT share of it mean less press next year).
  Placebo not a test. Prediction (own past does most, NYT adds, trends add
  little) wrong on the trends: argued trends add the most.
- **Museum buys**: argued trend + photography + NYT, since 2015, +227.
  Argued adds 41, NYT 62; photography nothing (dealt, the engine gains
  3 more). Placebo +191: coverage before the purchase predicts it better
  than coverage after, so it leads. Prediction (NYT stays leader, nothing
  adds 3 nats) wrong: an argued trend adds about 40.
- **Market (Artprice Top 500)**: after deviation 3, growing trend + NYT,
  since 2023 (NYT alone from 2018), +2.4 over 2018–2024; dealt, −3.6
  (growing) and −7.8 (NYT); placebo +7.2. Nothing in the coverage reliably
  predicts next year's place; what there is goes with the market rather
  than ahead of it. Prediction (NYT leads, the rest adds little) right on
  the order, but the lead is too small to claim. Before deviation 3:
  argued + sculpture + NYT, +31 (the 2014 windfall).
- Medium barely matters anywhere: painting adds 2 nats to approval,
  photography nothing to museum buys, sculpture nothing to the market once
  fixed. The feature that adds most to three of the four kinds is being
  written about inside a trend critics argue over.

### 12.8 An image prompt at the end of each report (planned 2026-10-29, before it is built)

Amends 12.4's "no image": each report ends with an image prompt, a text an
image model could draw from, labelled as an illustration of what a
"successful" work looks like by that measure. The engine makes no image.
Every choice is made by a rule, the same for all four kinds, so that the
four prompts differ only where the findings do:
- **None where nothing is claimed.** Where the strength verdict is "too
  small to claim anything" (the market now), the section says there is
  nothing to illustrate and gives no prompt.
- **Subject: one theme, by rule.** From this year's trend lists, the theme
  the leading features favour most: the largest sum of the leader's push
  (for one claim) over the lists the theme is on, so a list that pushes
  down (press's new trend) counts against it. Ties go to the most
  approvals less disapprovals this year, then the most writers. If the
  leader uses no list, every theme ties on the first step. Now:
  approve, indigenous and subcontinental art; press and museum, women
  artists' careers. Which particular theme helps was never tested (only
  "a theme on this list"); the prompt says the theme is this year's.
- **Medium, by rule.** The medium in the leading features that pushes
  up most; if none, the medium with the most approvals less disapprovals
  this year, labelled as not tested. Now: approve, painting; press and
  museum, photography (museum's from the leader, though it adds nothing).
- **The writer writes only the description**: one paragraph, 40 to 90
  words, the work's subject and medium in plain visual terms, drawn from
  the theme's words and what critics said in it; no names of real people,
  works or places. Code adds the label above it and a fixed setting
  after it, so nothing the data does not say is left to the writer or the
  image model: "The work alone in an empty white gallery, photographed
  straight on for a museum catalogue, in even, soft daylight."
- Prompt version 5; four report calls, under a cent each.
- Making images is outside the engine. Rule fixed before any are made, so
  none is picked: one run per prompt, every image it returns shown.

### 12.8 amended: how each prompt was made, said before it (2026-10-30, before it is built)

Each report gets a section just before the image prompt that explains how
the prompt was made. Code writes it from the same rule's inputs, so it
states the rule's reasons exactly and the writer cannot reword them:
- the theme: which lists the findings favour and which way each pushes
  (a list that pushes down is said to count against), how many themes
  tied, the approvals that broke the tie, and the theme that came next;
  that only being on a list was tested, not this theme;
- the medium: from the findings (and what dealing it at random showed it
  adds), or from this year's approvals (description, not tested); that
  only the media the papers tag were tested, naming the media critics
  judged this year that never could be;
- that the work's details are a reading of the theme's words and claims,
  not findings, and the setting is the same for every prompt.
Nothing in it comes from outside the data (so nothing on what the two
museums tend to collect, which the data does not record).

### 12.9 The market's image prompt describes instead (planned 2026-10-30, before it is built)

Where nothing predicts a kind of success (the market now), its prompt
describes what goes with that success instead of what leads to it, as the
market's year-after control found (coverage travels with a place in the
Top 500). Rules, fixed before looking at the result:
- **Who.** Our artists in Artprice's latest Top 500 table (now 2025:
  303 of them, both series, as the case set reads them).
- **Subject.** Among this year's themes (the trend lists' year, to
  September), the one whose claims name the most of these artists; ties
  to the most claims about them, then this year's approvals less
  disapprovals. The reasons give how many it names and the theme next.
- **Medium.** The medium tag on the most articles naming these artists
  in the same year; ties in the order painting, photography, sculpture.
  Only those three are tagged, said as before.
- The counts are made offline (evals/success_snapshot.py, from the press,
  claims and Artprice tables) and shipped in the snapshot; the rule runs
  in narrative._image_subject like the others. The reasons section says
  first that this prompt describes, not predicts, and why.
- Same label, writer's description and fixed setting as §12.8. One
  report call.
