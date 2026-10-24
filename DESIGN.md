# Abductive engine: design

*Draft, 2026-10-24. Nothing is built yet. Decisions still open are listed in
section 12.*

The philosophy behind this design is in [EPISTEMOLOGY.md](EPISTEMOLOGY.md).
This document is the technical plan that follows from it. Where the two
disagree, EPISTEMOLOGY.md states the intent.

## 1. The question

The Probabilistic Ontology Engine (POE) is given its variables. For macro
they are eight yes/no signals written by hand ("inflation shock", "credit
spread stress", ...). Since its D24 it is given no hypotheses about how
they connect, and forms its own from the evidence. Replayed over 2003–2026
with hand-written worldviews, none built from these signals explained the
weeks better than persistence (each signal following its own last week).
POE's open problem 1 asks whether that is a verdict on the worldviews or on
the vocabulary.

This engine is given only observations. It forms the concepts it reasons
with, under a fixed table of forms modelled on Kant's categories. It keeps
rival conceptual schemes alive, and drops a scheme when the evidence refutes
it. It asks:

> Given the same evidence, does an engine that forms its own concepts find
> structure the hand-written vocabulary could not express, and do its
> changes of conceptual scheme line up with the times the economy changed?

Like POE, it demonstrates epistemology and does not aim to forecast.
Predictive fit is how its beliefs are judged, not what it is optimised for.

## 2. Two engines, one source of data

*Agreed 2026-10-24.*

```
FRED, ... ──> POE ──observations──> abductive engine
               │                          │
               └──> dashboard <───────────┘
```

- **POE owns the data.** It fetches, as it does now, and also keeps the raw
  numbers it fetches. Today it keeps only its yes/no signals. This engine
  fetches nothing itself.
- **Data flows one way.** POE serves observations; nothing this engine
  learns goes back into POE. If POE took in formed concepts, the two engines
  would blur together, and the comparison between hand-written and formed
  concepts (question 2 in section 9) would be lost. POE never needs to know
  this engine exists.
- **Results go to the dashboard,** which reads each engine through its own
  API and can show them side by side.
- **No separate data service yet.** Moving fetching out of POE into a third
  repo would be tidier, but it adds a moving part. It becomes worth it if a
  third consumer of the data appears.

### The observation protocol

Each observation is four fields:

| Field | Example |
|---|---|
| `series` | `CPIAUCSL` |
| `measured` (the date the value describes) | 2008-09-01 |
| `value` | 218.8 |
| `public` (the date it became known) | 2008-10-16 |

The one query is **everything public as of date D**, for a domain's series.
A revised series has one row per published version, with the same
`measured` and different `public` dates. As of D, the newest version public
by D is the one that counts, which is ALFRED's model. The `public` field is
what keeps a replay honest: no week sees a number before it was published,
or a revision before it was made.

- **Live rows:** `public` is the date POE fetched the value. That is an
  upper bound on when it became known.
- **History:** POE's replay files fill the store with the publication dates
  its replays already use, as first published for CPI and unemployment.

The same rows can be exported to a file, so a 23-year replay runs without
POE's server.

**What changes in POE.** Every change only adds; none alters how POE learns.
- A table of raw observations, filled as it fetches.
- A read-only "as of D" route.
- A file export.
- A backfill of macro's history from `evals/data`.

## 3. Observations (what is given)

*EPISTEMOLOGY.md §3.*

For macro, the eight FRED series POE uses, read through the protocol. Each
week (Friday), the engine apprehends the observations that became public
since the last week.

What it predicts and is scored on each week is the change in each series
since its previous published value:
- log change for positive series: CPI, the Fed's balance sheet, NASDAQ, VIX,
  dollars per euro;
- plain difference for the rest: yield curve, credit spread, unemployment.

A series is scored only in weeks it publishes a new value, so monthly CPI is
scored monthly. The observation language is chosen by us, on purpose, so
that rival schemes have common ground (section 6).

## 4. Concepts (what is formed)

*EPISTEMOLOGY.md §§4–5.*

Every concept is built from observations under a fixed **table of forms**.
The engine never changes the table. A concept outside the table cannot be
expressed, so none comes from nowhere.

### Defined concepts

A defined concept is a rule assigning a state each week. It combines four
choices:

| Choice | Category | Options |
|---|---|---|
| Which series | quantity | one series (unity); an aggregate of several (plurality); all of the domain's (totality) |
| How the past is held | schema of reproduction | change over k weeks; level against its trailing n weeks (z-score); level |
| Over what window | judgment (practice) | k, n from a fixed set: 4, 13, 26, 52 weeks |
| In what degrees | quality | two or three ordered states separated by cut points |

Example: "VIX against its trailing 52 weeks, above a z-score of 1.2" is one
series, z-score, a 52-week window, and two degrees. POE's eight signals are
all defined concepts of this kind, so POE's vocabulary is one point in this
space. The engine can rediscover it, or do better.

Each concept records its pedigree: the observations, form, window and cut
points it was built from, and the anomaly or principle that occasioned it
(section 7).

### Hidden concepts

A hidden concept has no definition in observables. It is inferred from what
it explains, and posited only under a category of relation:
- **substance:** one series' persistent state, for example a regime that
  endures while its observations vary;
- **community:** a state several series share, which makes them move
  together.

A hidden concept must make a difference to some observation, or it is empty
and dropped (EPISTEMOLOGY.md §8).

### Status (modality)

Every concept is **possible** (proposed), **actual** (has earned credit on
observations after it was proposed), or **necessary** (actual, invariant
across regimes, and held by every surviving scheme).

## 5. Levels of belief

Levels 1–3 follow POE's specification (POE `SPEC.md` §§4–5). Level 4 is new.

| Level | What is believed | From |
|---|---|---|
| 4. Concepts | which concepts exist (the vocabulary) | new: formation under the table, section 7 |
| 3. Structure | rival whole schemes, ranked by evidence | POE §4.3, §5.1 |
| 2. Links | each link's probability of existing | POE §4.2 (`DependencyEdge.existence_probability`), §5.1 |
| 1. Parameters | the conditional distributions | POE §4.2 (`CONDITIONAL_LINEAR_GAUSSIAN` family), §5.1 |

From POE, as built:
- **Directed conditionals** with a Bayesian existence probability.
- **Last-week companions,** so a scheme can hold that this week follows from
  last week (POE `lag_of`, REFACTOR_SPEC D19).
- **Rival whole structures,** compared by evidence. This is how a direction
  is settled when the evidence can settle it.

From POE's specification, designed but never built, and needed here:
- **Association links** (POE `FACTOR_LINK`): a dependence with no direction
  claimed.
- **Hidden variables** (POE `Variable.hidden`).
- **Kinds of relation** (POE `RelationSemantics`: causal, correlational,
  temporal), recorded on each link.

One departure from POE as built: level 2 compares the evidence with and
without a link prequentially, not by BIC (section 6).

### Connections (three grades)

*EPISTEMOLOGY.md §6.*

| Grade | Link | Direction |
|---|---|---|
| Association | factor link | none claimed |
| Directed dependence | directed conditional, same week or from an earlier week | claimed only when the evidence breaks the tie |
| Community | association, or a shared hidden state | reciprocal |

A causal link may hold within one week; a cause need not come earlier. Where
the two directions of a link predict the observations equally well, the
engine holds it as an association. It claims a direction only when one of
these breaks the tie:
- temporal order (changes in one come first);
- an asymmetric pattern (two unrelated causes of one effect);
- invariance across regimes.

A directed dependence that holds through changed regimes earns the status
**necessary**.

### Schemes and programmes

A **scheme** is one vocabulary with its structure and parameters. A
**programme** (in Lakatos's sense) is a vocabulary and every scheme
descended from it.
- **Conceptual shift:** the leading programme changes, and the engine now
  thinks in different concepts. This is Kuhn's revolution, which POE cannot
  have.
- **Structural shift:** the leading scheme changes within one programme.
  This is Kuhn's normal science, and POE's "revision".

## 6. Scoring rival schemes

*EPISTEMOLOGY.md §8.*

Schemes with different concepts are compared on what both must answer to:
the observations. Each week, before seeing them, every scheme gives a
probability distribution for that week's observations (section 3). It is
scored by the log-probability it gave them. The score is prequential, earned
week by week out of sample, and windowed with a half-life as in POE.

**Unity:** a scheme is scored as one whole, on every observation. A series
it has no concept for is still predicted, if crudely, and counts against
it.

**The model.** Each scheme is a dynamic Bayesian network:
- **Concepts:** discrete, defined or hidden.
- **Observations:** continuous.
- **Links:** each observed change is Gaussian given its parent concepts'
  states (conditional linear Gaussian).
- **Hidden concepts:** filtered exactly (forward algorithm). At most three,
  each with two or three states, so the joint hidden space has at most 27
  states and is cheap.

**Agreed 2026-10-24:**
- **Credit only for novel predictions.** A new concept is scored only on
  observations that arrive after it was proposed. It may learn its
  parameters from the past, as every scheme does. This is Lakatos's
  progressive programme as a rule.
- **A fair yardstick** (section 8): the baselines allow for calm and wild
  stretches, so a scheme cannot win merely by noticing that volatility comes
  and goes.
- **Refutation unchanged from POE.** It is kept until a replay shows it
  fails; if it does, it is revisited.

**Lessons carried over from POE's replays:**
- **No BIC.** A prequential score already charges a scheme for the
  parameters it has to learn. Replay 10 found BIC charged them twice and
  refuted rivals before the evidence did.
- **Refuting a scheme takes evidence.** A scheme is dropped only when a
  rival beats it by a log Bayes factor above ln 100, compared on the
  observations both have been scored on.
- **At least one scheme per programme survives until refuted.** Otherwise
  whichever programme leads early wins by default (POE's replays 1–9).
- **Nothing is scored as certain for free.** A link whose parent is unknown
  this week is averaged over that parent's distribution.

## 7. Forming concepts

*EPISTEMOLOGY.md §7.*

Every new concept has an occasion: an anomaly, or one of reason's
regulative principles. The engine never proposes at random, and no language
model takes part.

### Anomaly (reflecting judgment)

After each week, the leading scheme's surprise at each series is compared
with its usual surprise. A run of surprise well above usual is an anomaly.
The proposal is shaped by the anomaly:

| Anomaly | Proposal | Category |
|---|---|---|
| One series' surprises change in size or sign for a stretch | a hidden persistent state of that series | substance |
| Several series surprised in the same weeks | a hidden state they share | community |
| A rule over past observations would have expected the surprises | a defined concept recognizing that rule, linked to the surprised series | causality |

For the third row, the engine searches the table of forms for the defined
concept that best anticipates the anomaly. The search runs only over past
observations, and the concept is then scored only on what follows.

### Regulative principles (between anomalies)

| Principle | Operation |
|---|---|
| Homogeneity | **merge** two concepts that almost always agree |
| Specification | **split** a concept whose cases behave in two distinct ways |
| Continuity | **add a middle degree,** or an intermediate concept |

Also: **retire** a concept that connects to nothing (unity, section 6).

Merging also catches links that are true by definition: two concepts that
agree because they read the same source (POE's open problem 6).

### Judgment (mother wit)

Cut points and windows are settled by practice. Candidates from the fixed
sets are tried, and the evidence keeps the ones that predict well.

### Variants and programmes

Each proposal starts a new scheme as a variant of the leader. A changed
vocabulary starts a new programme. Changes to links only (add, remove,
reverse) are structural variants within the programme, as in POE.

### The random control

A separate run replaces every occasioned proposal with a random one from the
same table. It exists only to test whether occasioned concept formation does
better than blind variation (question 5). It is not part of the engine.

## 8. Baselines

Every scheme is scored on the same observations as these:

1. **Independence:** each series' change is Gaussian, ignoring the past.
2. **Persistence:** each series' change depends on its own last change. This
   is the baseline POE could not beat. Its spread tracks recent volatility
   (an exponentially weighted variance), so calm and wild stretches are
   already allowed for. A formed concept has to explain something beyond
   that to beat it.
3. **POE's vocabulary:** POE's eight signals as a fixed set of defined
   concepts, with structure learned as here. This is the direct yardstick:
   does forming concepts beat the hand-written ones on the same evidence?
4. **Later, on POE's own terms:** the leader's probability for POE's eight
   yes/no signals (sampled from its predictive distribution), against POE
   replay 10's −3.35 nats a week.

## 9. The first replay

Fixed before it runs:
- **Data:** the same weeks as POE replay 10 (2003-04-04 to 2026-10-16), as
  first published.
- **Events:** POE's events table.
- **Seeds:** 0–4, where anything is random (starting values for hidden
  states, and the control's proposals).

Questions:
1. Does any formed scheme beat persistence?
2. Does it beat POE's vocabulary?
3. Do conceptual shifts follow the events within 26 weeks, more often than
   the same number of shifts placed at random would?
4. What do the surviving concepts track? This is reported, not scored: for
   example, whether a hidden state turns on in 2008 and 2020. Which concepts
   reach actual and necessary, and when?
5. Does occasioned concept formation do better than the random control: do
   its concepts survive longer, and do its schemes score better?

A negative answer is a result. As with POE's replays, the engine is not
tuned until the questions come out well. A change suggested by one replay is
measured on the next.

## 10. Build order

Each step has passing tests before the next starts, test first.

0. **In POE.** The additions in section 2 (raw observation table, "as of
   D" route, file export, macro backfill), with POE's own tests. These
   include that "as of D" never returns a value or revision public after D.
1. **Reading observations.** A client for the protocol, over HTTP and from
   an exported file, and the weekly observations of section 3 built from
   it. There are no imports from POE; the protocol is the only contact.
2. **Scoring and baselines.** Prequential scoring, plus independence,
   persistence and POE's vocabulary as fixed schemes.
3. **Defined concepts.** The table of forms, defined concepts with their
   pedigrees, and schemes built from them.
4. **Links and programmes.** Levels 1–3 after POE's specification, with
   association links; variants; refutation by Bayes factor; conceptual and
   structural shifts.
5. **Hidden concepts.** Exact filtering, and parameter learning with a
   half-life.
6. **Concept formation.** Anomaly detection, the occasioned proposals,
   the regulative operations and modal status (section 7).
7. **Replay.** The run and the random control; written up with charts.

Not in scope until the replay is written up:
- **Live data, an API, the dashboard.**
- **Art.** Its evidence is text, which is testimony, not observation
  (EPISTEMOLOGY.md §9). A language model would read: it reports what each
  text asserts. The engine would judge: it forms concepts from those
  assertions under the same table and tests them. The model never proposes
  what to believe.

## 11. Stack

Python 3.12, uv, numpy, pytest. Possibly scipy.

No pgmpy, which POE uses. Its strength is fixed discrete networks; this
engine needs hidden states, continuous observations and online filtering,
all small enough to write directly. That also keeps every step of the
inference readable.

Like POE, everything is seeded and replayable: same data and seed, same
result.

## 12. Open

- **Observation choice** (section 3). Weekly change in each series is the
  default. The alternative, raw levels, would let concepts be about levels
  too, but levels drift over 23 years in ways that are hard to model
  honestly.
- **Name.** `abductive_engine` for now. It must not reuse
  `probabilistic_ontology_engine_abductive`, the old prototype's repo, which
  will sit beside it.
- **Old prototype.** When it is back on this machine, read it for its
  concept-forming method before step 6.
- **Art's boundary** between the model that reads and the engine that
  judges. Settled in the art phase.
