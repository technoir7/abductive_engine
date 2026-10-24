# Abductive engine: design

*Draft, 2026-10-24. Nothing is built yet. Decisions marked **Open** wait for
the owner.*

## 1. The question

The Probabilistic Ontology Engine (POE) is handed its variables. For macro
they are eight yes/no signals written by hand ("inflation shock", "credit
spread stress", ...), and it learns only how they connect. Replayed over
2003–2026, no worldview built from them explained the weeks better than
persistence (each signal follows its own last week). POE's own open problem 1
asks whether that is a verdict on the worldviews or on the vocabulary: weekly
yes/no signals may be too coarse to carry how credit or money moves the rest.

This engine is handed only observations. It invents the concepts it reasons
with, keeps rival conceptual schemes alive, and drops a scheme when the
evidence refutes it. It asks:

> Given the same evidence, does an engine that forms its own concepts find
> structure that the hand-written vocabulary could not express, and do its
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
  learns goes back into POE. If POE took in invented concepts, the two
  engines would blur together, and the comparison between hand-written and
  invented concepts (question 2 in section 9) would be lost. POE never
  needs to know this engine exists.
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

## 3. Abduction

Peirce's schema: *the surprising fact C is observed; but if A were true, C
would be a matter of course; hence there is reason to suspect A.* Abduction
is how hypotheses are formed, not how they are confirmed. Here:

- **Surprise drives concept formation.** A new concept is proposed to explain
  observations the leading scheme found surprising. Kuhn's anomalies, made
  operational.
- **Evidence decides which concepts survive.** A proposed concept is
  confirmed or refuted only by how well the scheme that holds it predicts
  later observations.

Blind variation, as POE mutates its candidates, is kept as a control. Each
concept records how it was proposed, so the replay can test whether
abduction beats chance (question 5 in section 9).

## 4. What is given and what is invented

**Given (level 0, observations).** For macro: the eight FRED series POE uses,
as first published, each week seeing only what had been published by that
Friday. The scored observation each week is the change in each series since
its previous published value: log change for positive series (CPI, the Fed's
balance sheet, NASDAQ, VIX, dollars per euro) and plain difference for the
rest (yield curve, credit spread, unemployment). A series is scored only in
weeks it publishes a new value, so monthly CPI is scored monthly.

This is a deliberate choice, and not a neutral one. Which series to watch,
and that "change since last value" is the thing observed, are decided here,
not by the engine. Observation is theory-laden. The engine's concepts are its
own, but its observation language is ours, and it is fixed so that rival
schemes have common ground (section 6).

**Invented (level 4, concepts).** Two kinds:

1. **Defined concepts.** These are predicates built from observations: a
   transform of one series, cut into two or three states. Transforms are
   change over k weeks, z-score against the trailing n weeks, or level.
   Example: "VIX's z-score over 52 weeks is above 1.2." POE's eight signals
   are all of this kind, so POE's vocabulary is one point in this space, and
   the engine can rediscover it or do better.
2. **Theoretical concepts.** Hidden states with no definition in
   observables, inferred only from what they explain. An example is a
   two-state "regime" that makes several series move together and that
   persists from week to week. Positing unobservables to explain
   observables is abduction in its strongest sense.

## 5. Levels of belief

POE's three levels, with one added above them:

| Level | What is believed | Changes by |
|---|---|---|
| 4. Concepts | which concepts exist (the vocabulary) | abduction: propose, merge, retire |
| 3. Structure | which concepts depend on which | variants of the leading schemes |
| 2. Links | how probable each link is | evidence, per scheme |
| 1. Parameters | the conditional distributions | evidence, with a half-life |

A **scheme** is one level-4 vocabulary with its structure and parameters.
A **programme** (in Lakatos's sense) is a scheme and every variant descended
from it.

- **Conceptual shift:** the leading programme changes. The engine now thinks
  in different concepts. This is the strong, Kuhnian sense of a paradigm
  shift, which POE cannot have.
- **Structural shift:** the leading scheme changes within one programme.
  This is POE's "revision" and corresponds to normal science.

## 6. Scoring rival schemes (incommensurability)

Two schemes with different concepts cannot be compared concept by concept,
because they do not describe the world in the same terms. Kuhn called this
incommensurability. They can be compared on what each predicts will be
**observed**. Every scheme gives a probability distribution for each week's
observations (section 4) before seeing them, and is scored by the
log-probability it gave them. The score is prequential, meaning it is earned
week by week, out of sample, and windowed with a half-life as in POE.

Each scheme is a dynamic Bayesian network:
- **Concepts:** discrete, defined or hidden.
- **Observations:** continuous.
- **Links:** each observed change is Gaussian given its parent concepts'
  states (conditional linear Gaussian).
- **Hidden concepts:** filtered exactly (forward algorithm). At most three,
  each with two or three states, so the joint hidden space has at most 27
  states and is cheap.

Agreed 2026-10-24:
- **Credit only for novel predictions.** A new concept is scored only on
  observations that arrive after it was proposed. It was proposed because it
  would have explained recent surprises, so scoring it on those would reward
  hindsight. It may learn its parameters from the past, as every scheme
  does. This is Lakatos's test of a progressive programme: it predicts facts
  it was not built to fit.
- **A fair yardstick** (section 8): the baselines already allow for calm and
  wild stretches, so a scheme cannot win merely by noticing that volatility
  comes and goes.
- **Refutation unchanged from POE** (below). It is kept until a replay shows
  it fails; if it does, it is revisited.

Lessons carried over from POE's replays:
- **No BIC.** A prequential score already charges a scheme for the
  parameters it has to learn. Replay 10 found BIC charged them twice and
  refuted rivals before the evidence did.
- **Refuting a scheme takes evidence.** A scheme is dropped only when a rival
  beats it by a log Bayes factor above ln 100, compared on the observations
  both have been scored on.
- **At least one scheme per programme survives until refuted.** Otherwise
  whichever programme leads early wins by default (POE's replays 1–9).
- **Nothing is scored as certain for free.** A link whose parent is unknown
  this week is averaged over that parent's distribution.

## 7. Proposing concepts

After each week, the leader's surprise per series is compared with its usual
surprise. A run of surprise well above usual is an anomaly, and it triggers
proposals fitted to the anomaly:

| Anomaly | Proposal |
|---|---|
| One series' errors change size or sign for a stretch | a hidden 2-state regime over that series |
| Several series surprised in the same weeks | a hidden state shared by them (a common cause) |
| A transform of past data would have predicted the surprises | a defined concept with that cut, linked to the surprised series |

Housekeeping, on a schedule:
- **Merge** two concepts that agree almost every week. This also catches
  "true by definition" links (POE open problem 6).
- **Retire** a concept nothing depends on.

Each proposal starts a new scheme as a variant of the leader. A changed
vocabulary starts a new programme. Proposals by random change of a
leader's concepts run beside these as the control.

## 8. Baselines

Every scheme is scored on the same observations as these four:

1. **Independence:** each series' change is Gaussian, ignoring the past.
2. **Persistence:** each series' change depends on its own last change. This
   is the baseline POE could not beat. Its spread tracks recent volatility
   (an exponentially weighted variance), so calm and wild stretches are
   already allowed for. An invented concept has to explain something beyond
   that to beat it.
3. **POE's vocabulary:** POE's eight signals as a fixed set of defined
   concepts, with structure learned as here. This is the direct yardstick:
   does inventing concepts beat the hand-written ones on the same evidence?
4. **Later, on POE's own terms:** the leader's probability for POE's eight
   yes/no signals (sampled from its predictive distribution), against POE
   replay 10's −3.35 nats a week.

## 9. The first replay

Fixed before it runs:
- **Data:** the same weeks as POE replay 10 (2003-04-04 to 2026-10-16), as
  first published.
- **Events:** POE's events table.
- **Seeds:** 0–4.

Questions:
1. Does any invented scheme beat persistence?
2. Does it beat POE's vocabulary?
3. Do conceptual shifts follow the events within 26 weeks, more often than
   the same number of shifts placed at random would?
4. What do the surviving concepts track? This is reported, not scored: for
   example, whether a hidden state turns on in 2008 and 2020.
5. Do concepts proposed by abduction survive longer and score better than
   those proposed at random?

A negative answer is a result. Like POE's replays, the engine is not tuned
until the questions come out well. A change suggested by one replay is
measured on the next.

## 10. Build order

Each step has passing tests before the next starts, test first.

0. **In POE.** The additions in section 2 (raw observation table, "as of
   D" route, file export, macro backfill), with POE's own tests. These
   include that "as of D" never returns a value or revision public after D.
1. **Reading observations.** A client for the protocol, over HTTP and from
   an exported file, and the weekly observations of section 4 built from
   it. There are no imports from POE; the protocol is the only contact.
2. **Scoring and baselines.** Prequential scoring, plus independence,
   persistence and POE's vocabulary as fixed schemes.
3. **Defined concepts.** The concept grammar, schemes built from it,
   proposals by random change (the control).
4. **Programmes.** Variants, refutation by Bayes factor, conceptual vs
   structural shifts.
5. **Hidden concepts.** Exact filtering, and parameter learning with a
   half-life.
6. **Abduction.** Anomaly detection and the proposals in section 7.
7. **Replay.** Run it, write up the results with charts.

Not in scope until the replay is written up:
- **Live data, an API, the dashboard.**
- **Art.** Its evidence is text, so concepts would be proposed from language,
  perhaps by a model under POE SPEC §15's rule: the model may propose,
  validation and evidence decide. That is a different proposal mechanism on
  the same scoring.

## 11. Stack

Python 3.12, uv, numpy, pytest. Possibly scipy.

No pgmpy, which POE uses. Its strength is fixed discrete networks; this
engine needs hidden states, continuous observations and online filtering,
all small enough to write directly. That also keeps every step of the
inference readable.

Like POE, everything is seeded and replayable: same data and seed, same
result.

## 12. Open

- **Observation choice** (section 4). Weekly change in each series is the
  default. The alternative, raw levels, would let concepts be about levels
  too, but levels drift over 23 years in ways that are hard to model
  honestly.
- **Name.** `abductive_engine` for now. It must not reuse
  `probabilistic_ontology_engine_abductive`, the old prototype's repo, which
  will sit beside it.
- **Old prototype.** When it is back on this machine, read it for its
  concept-forming method before step 6.
