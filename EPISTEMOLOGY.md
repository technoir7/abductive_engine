# The epistemology of the abductive engine

*Draft, 2026-10-24. This is the philosophical account of how the engine forms
concepts, holds beliefs and gives them up. `DESIGN.md` is the technical plan
and follows from this document. Where the two disagree, this one states the
intent. For art, `ART-PLAN.md` is the plan of record: every plan, prediction
and result, and each departure from this account, dated (section 9).*

References to the *Critique of Pure Reason* use the standard A (1781) and B
(1787) pagination. Other works are cited by section. Quotations are kept
short; the rest is paraphrase.

## 1. What the engine is meant to be

The Probabilistic Ontology Engine (POE) is given its concepts and learns how
they connect. This engine is given only what is observed. It forms the
concepts it reasons with, holds rival conceptual schemes, and lets the
evidence decide between them.

It is modelled on one account of how that is possible: Kant's, in the
*Critique of Pure Reason*. Kant asked what must be true of a mind for
experience of an ordered world to be possible at all. His answer was that the
mind does not passively receive order from the world. Raw sensation is
organized by forms the mind brings to it: space and time in perception, and a
fixed set of pure concepts (the categories) in thought. Experience is what
results when the given is synthesized under those forms into one connected
whole.

The engine takes this account as its architecture:
- what is given to it is fixed and comes from outside;
- the forms under which it may organize what is given are fixed and come from
  us, its builders, as the categories come from the understanding;
- the concepts it forms are its own, and are always formed from the given,
  under those forms;
- every concept it holds must belong to one connected scheme that answers to
  every observation.

Two consequences follow, and both are deliberate:

1. **No concept comes from nowhere.** The engine never conjures a hypothesis,
   neither by unconstrained random guessing nor by asking a language model
   for one. A concept is admissible only if it can be shown to be built from
   observations through the fixed forms. In Kant's terms, its origin can be
   given a deduction.
2. **The forms do not change.** The engine learns empirical concepts and
   empirical laws, never new categories. What it is able to think is fixed
   in advance. What it does think is learned.

### What is and is not claimed

Kant's inquiry is *transcendental*: it concerns the conditions under which
experience is possible, not the psychology of any actual mind. He warns
against confusing the two. An engine is a mechanism, and a mechanism belongs
to the empirical side of that line. So the claim here is not that the engine
has experience, a self or understanding. The claim is narrower: the
conditions Kant argued any experience must meet can be stated precisely
enough to be built. A system that meets them shows what those conditions
demand when they are taken literally. Where they cannot be met literally,
this document says so (section 10).

## 2. The problem it answers: Hume

Hume argued that experience gives us only *constant conjunction*. We see
that events of one kind are regularly followed by events of another, and we
never see a *necessary connection* between them (*Enquiry concerning Human
Understanding*, §7; *Treatise* 1.3.6). Our idea of causal necessity is,
on his account, a habit of expectation formed by repetition, projected onto
the world.

A statistical learner is Hume's mind made exact. From data alone it can
learn which observations go together, how strongly, and in what order.
Nothing in the data marks a regularity as necessary rather than so far
unbroken. POE faces this problem already: its links are learned
associations, ranked by how well they predict.

Kant's reply was that necessity is not found in experience but brought to
it. The concept of cause is a rule the understanding applies a priori, and
only under such rules does a sequence of perceptions become an objective
order of events at all (Second Analogy, A189/B232ff). The engine cannot
have a priori knowledge in Kant's sense (section 10). What it can do is
separate the two things Hume ran together: the bare association the
evidence gives, and the claim that one thing *depends on* another by a rule,
which is a further claim the evidence must earn (section 6).

## 3. What is given: intuitions

For Kant, all knowledge begins with intuition: something given to us
immediately, through sensibility, under the forms of space and time. And
"thoughts without content are empty, intuitions without concepts are blind"
(A51/B75). Neither faculty can do the other's work.

**In the engine,** what is given is an *observation*: a series (for
example, consumer prices), the date the value describes, the value, and the
date it became public. For the economic domains, observations arrive from
POE, which fetches them; the engine fetches nothing and never sees anything
else. Art is the exception: the engine fetches the press itself and has it
read, and what is given is testimony (section 9).

**Time is the form of the given.** Each observation carries two dates. The
engine is never shown an observation before the date it became public. This
is not a convenience; it is what makes the engine's experience a sequence
at all, in which later can depend on earlier but not the reverse. Kant
treats time as the form of inner sense, under which all representations
stand. The engine's ordering by publication date plays that role.

**Space has no direct analogue.** Kant's outer sense presents objects as
outside one another in space. The engine's observations are distinguished
only by which series they belong to. That a series has an identity across
time is assumed, not earned. It is the nearest thing here to an object
standing in space, and it is a weaker thing.

**The given is not innocent.** Two concessions belong here.
1. *We chose what is given.* Which series the engine watches, and that what
   it observes each week is the change in each since its last value, are
   decided by its builders. Philosophy of science since Hanson
   (*Patterns of Discovery*, 1958) and Kuhn holds that observation is
   theory-laden. The engine's concepts are its own, but its observation
   language is ours, and it is fixed on purpose: rival schemes need common
   ground on which to be compared (section 8).
2. *The given is already conceptualized.* "Consumer prices" is not a
   sensation. It is a concept made by a statistical agency: an index built
   from a basket of goods, with choices about weights and quality. The
   engine's intuitions are, from the world's side, the products of other
   minds' concepts. Kant's intuitions are prior to all concepts; the
   engine's are prior only to its own.
3. *For art, the given is a model's reading of testimony.* What the engine
   takes up is not the text but what a model reports the text asserts, in a
   form we fixed. The form is ours, as in concession 1, and it has been
   extended once after the data had been seen, openly and with the
   extension stated before it was used (each claim's subject, and whether it
   is about a life: ART-PLAN 15.2).

## 4. Synthesis: how a concept is formed from the given

Kant holds that combining a manifold into a unity is never given by the
senses. It is an act of the mind, which he calls synthesis. The first-edition
Deduction (A98–110) describes three aspects of it.

1. **Apprehension in intuition** (A98–100). The manifold must be run through
   and held together as one: this week's observations, taken as this
   week's.
   *In the engine:* each week's fresh observations are collected as one
   manifold, the week.
2. **Reproduction in imagination** (A100–102). What was apprehended must be
   carried forward, or every moment would start afresh and nothing could be
   compared with anything.
   *In the engine:* a memory of past observations over fixed windows. This
   is what makes "higher than usual" or "rising for a quarter" thinkable at
   all.
3. **Recognition in a concept** (A103–110). What is reproduced must be
   recognized as the same under a rule. For Kant, a concept is exactly
   such a rule for unifying a manifold.
   *In the engine:* a concept is a rule that takes the reproduced
   observations and assigns a state, for example "volatility above its
   usual level, by a z-score of 1.2 over 52 weeks".

**Empirical concepts are made this way.** In the *Jäsche Logic* (§6), Kant
describes how an empirical concept arises: by *comparing* representations,
*reflecting* on what they have in common, and *abstracting* from the rest.
The engine's concept formation follows these three acts:
- comparing observations across weeks and series;
- reflecting on which grouping would make them intelligible together;
- abstracting into a rule that keeps one aspect (a degree, a direction, a
  co-movement) and discards the rest.

So every concept the engine holds has a pedigree: these observations,
apprehended this way, reproduced over this window, recognized under this
rule. That pedigree is recorded with the concept and can always be shown.

## 5. The categories and their schemata: the fixed forms

Kant's categories are the pure concepts of the understanding. There are
twelve, in four groups of three, and every judgment about objects is made
under them. Pure concepts cannot be applied to intuitions directly, because
they share nothing with sensation. The *schematism* (A137/B176ff) bridges
them: each category has a *schema*, a rule for determining time, through
which it applies to what is given in time.

The engine's fixed table of forms is built the same way. Each category
appears through a schema concrete enough to compute. The table is written
by us and never changed by the engine. It is the engine's a priori.

### Quantity (Axioms of Intuition, A162/B202)

Schema: number, the successive addition of unit to unit.

| Category | Form a concept may take |
|---|---|
| Unity | a concept over one series |
| Plurality | a concept over several series taken together (their aggregate) |
| Totality | a concept over every series in the domain ("broad stress") |

### Quality (Anticipations of Perception, A166/B207)

Schema: degree, how much of the real fills a moment. Kant's principle is that
in every appearance the real has a degree, an intensive magnitude.

| Category | Form a concept may take |
|---|---|
| Reality | a state of a concept: present to a degree ("above usual") |
| Negation | its absence ("not above usual") |
| Limitation | a bounded degree between the two ("within usual") |

This is why the engine's concepts may be graded, with two or three ordered
states, and are not confined to yes and no. POE found that yes-or-no
evidence may be too coarse to carry how the economy moves (its open problem
1). On Kant's account, degree is a condition of perception itself.

### Relation (Analogies of Experience, A176/B218)

These are the heart of the matter, and section 6 treats causality at length.

| Category | Schema | Form in the engine |
|---|---|---|
| Substance and accident (First Analogy, A182/B224) | permanence of the real in time | persistence: what a concept is this week depends on what it was last week; a hidden state that endures while observations vary |
| Cause and effect (Second Analogy, A189/B232) | succession according to a rule | a directed conditional: one concept's state depends on another's, in the same week or from an earlier week |
| Community (Third Analogy, A211/B256) | coexistence of substances in reciprocal determination | an association between concepts with no direction claimed, or a hidden state that several series share |

A remark on POE's main finding. Replayed over 2003–2026, no hand-written
worldview explained the weeks better than persistence: each signal
following its own last week. In these terms, POE's experience was organized
under the First Analogy and had not yet earned the Second. POE now forms
its own hypotheses (its D24) and puts its leader's core on trial (D27).
Replayed so (replays 11–14), it still found nothing persistence did not:
from 2009 every seed held each signal's persistence and no more.

### Modality (Postulates of Empirical Thought, A218/B265)

Kant's modal categories do not add to what a concept says about its object.
They state its relation to our faculty of knowledge. The engine uses them as
the status of every concept it holds:

| Category | Kant's postulate | Status in the engine |
|---|---|---|
| Possibility | agrees with the formal conditions of experience | **proposed**: well formed under the table, but not yet tested |
| Actuality | connected with perception | **actual**: has earned credit predicting observations made after it was proposed |
| Necessity | connected with the actual by universal laws | **necessary**: holds stably across regimes and across every surviving scheme |

### The table is fixed, and how its forms combine is not

A defined concept combines:
- a quantity: one series, several, or all;
- a schema of reproduction over a window, from a fixed set: change over k
  weeks, level against its trailing n weeks, or level;
- a quality: two or three degrees, separated by cut points.

A hidden concept is posited under substance (one series' persistent state)
or under community (a state several series share). Relations between
concepts take the three forms of relation. Nothing else is admissible.

## 6. Causality

### Kant's causality is about order, not elapsed time

It is tempting to read the Second Analogy as "a cause comes before its
effect". Kant explicitly rejects that reading. His examples are a stove that
warms a room, and a ball that presses a hollow into a cushion: in both,
cause and effect are simultaneous (A202–203/B247–248). What makes one the
cause is the *order* of time, meaning which is the condition of the other,
not a *lapse* of time between them. Their order can be determined even when
the interval between them vanishes.

So the engine does not equate causation with "earlier". A causal link may
hold within the same week. Temporal precedence matters as *evidence* about
direction, as described below, not as the definition of a cause.

### Three grades of connection

POE's specification already distinguishes kinds of relation (causal,
correlational, temporal) and kinds of link (a directed conditional, an
undirected factor). It built only directed conditionals, each with a
Bayesian probability that it exists, and links from last week's values. The
engine takes POE's design and completes it:

1. **Association** (Hume's constant conjunction). Two concepts tend to go
   together, in the same week or across weeks. Nothing is claimed about
   which depends on which. This is what the evidence most directly gives.
2. **Directed dependence** (Kant's causality as an empirical law). One
   concept depends on another by a rule, in the same week or from an
   earlier one. It carries a Bayesian probability that it exists, as in
   POE, and it is a hypothesis the evidence must support.
3. **Community** (the Third Analogy). Concepts determine one another, or
   jointly depend on a hidden state they share. The engine posits a shared
   hidden state when several series are surprised together. That is a posit
   under the category of community, not an invention ex nihilo.

### When the evidence cannot decide a direction

From observation alone, "A depends on B" and "B depends on A" often predict
exactly the same observations. Where structures cannot be told apart in this
way, no amount of passive data will distinguish them (the Markov equivalence
of causal graphs; Verma and Pearl, 1990). This is Hume's problem in exact
form. The engine therefore holds such a link only as an association, unless
something breaks the tie:

- **Temporal order.** Changes in A come before changes in B, and not the
  reverse. This is the legitimate use of time in causal judgment: as a sign
  of the order of dependence.
- **An asymmetric pattern.** A and B are unrelated, but each is related to
  C. Only arrows pointing into C fit that pattern.
- **Invariance under changed circumstances.** See the next subsection.

POE does not mark this. When two of its structures predict the same, it keeps
whichever happens to lead. The engine reports what the evidence could not
settle.

### Necessity as invariance

For Kant, a causal connection is necessary because it falls under a rule,
and a rule holds universally. No finite evidence can give necessity in that
sense (section 10). But the evidence can give a mark of it. A mere
conjunction is the kind of thing that breaks when circumstances change; a
law is the kind of thing that does not.

So a dependence that holds through changed regimes (through 2008, through
2020) earns the modal status *necessary*. One that held only within one
regime and broke when the regime changed is reclassified as a conjunction of
that regime. Modern causal inference makes a related argument, that
invariance across environments is what distinguishes a causal mechanism from
a correlation (Peters, Bühlmann and Meinshausen, 2016).

POE gives a reason to care. Its learned associations held for seventeen
years and broke during COVID. On this account, that is what learning
conjunctions and mistaking them for laws looks like.

## 7. Judgment, mother wit, and the origin of hypotheses

### Determining judgment and mother wit

Kant defines judgment as the faculty of subsuming under rules: deciding
whether a case falls under a given rule (A132/B171). He then argues that
judgment cannot be fully taught by rules. A rule for applying rules would
itself need judgment to apply, and so on without end. Judgment is therefore
a particular talent that can be exercised but not taught, and its lack is
what is properly called stupidity. Kant's word for the natural gift is
*Mutterwitz*, mother wit (A133/B172).

The engine meets the same regress in a concrete form:
- the table fixes that a concept may be "a series above its usual level";
- it cannot fix *how far* above, or *what* counts as usual: which cut point,
  which window.

These are matters of judgment. In the engine they are settled by practice:
the candidate cut points and windows are tried, and the evidence keeps the
ones that predict well. That is judgment improved by exercise. What the
engine lacks is the gift. Its judgment is all practice and no native wit,
which is one honest measure of how far it is from a mind.

### Reflecting judgment: finding a concept for what does not fit

In the *Critique of Judgment* (Introduction IV, Ak 5:179), Kant
distinguishes two kinds of judgment:
- **determining judgment** applies a universal already given to a particular;
- **reflecting judgment** is given only the particular and must find the
  universal.

Forming a new empirical concept is reflecting judgment. Reflecting judgment
works under a presupposition: that nature is ordered in a way our faculties
can grasp. Kant calls this the purposiveness of nature for our cognition.
It is not known to be true; it is the assumption without which looking
would be pointless. The engine makes the same assumption when it treats a
surprise as something to be explained, rather than as noise to be endured.

### Peirce: abduction begins with surprise

Peirce gave the logical form of this act and named it *abduction*: "The
surprising fact, C, is observed; but if A were true, C would be a matter of
course; hence, there is reason to suspect that A is true" (*Collected Papers*
5.189). Abduction is not proof. It is the only inference that introduces a
new idea, and it licenses only *suspicion*, which then needs testing.

Kuhn locates the same moment in the history of science. A new paradigm
begins with an *anomaly*: something the reigning one led us to expect
otherwise, which persists and resists adjustment (*The Structure of
Scientific Revolutions*, ch. VI).

**In the engine as designed, every proposal begins with an anomaly.** (Not
yet built: as built, macro proposes every four weeks the link its recent
surprises most support beyond chance, which is closer to POE's D24 than to
an anomaly. Art's concepts are formed differently again: every claim is
taken up in the order it was published and joins the nearest live concept
or founds one, a synthesis in time, with no anomaly needed.) After each week,
the leading scheme's surprise at each series is compared with its usual
surprise. A run of surprise well above usual is an anomaly, and only an
anomaly occasions a new concept. The proposal is shaped by the anomaly it
answers:

| The anomaly | What reflecting judgment proposes | Under the category of |
|---|---|---|
| One series' surprises change in size or sign for a stretch | a hidden state of that series that persists | substance |
| Several series surprised in the same weeks | a hidden state they share | community |
| A rule over past observations would have expected the surprises | a defined concept recognizing that rule, on which the surprised series depends | causality |

### Reason's regulative principles: how the search is guided

In the Appendix to the Transcendental Dialectic (A642–668/B670–696), Kant
describes principles by which reason seeks systematic unity in what the
understanding knows:
- **homogeneity:** seek the common kind under which different things fall;
- **specification:** seek the finer kinds within a kind;
- **continuity:** seek the intermediate kinds between any two.

These principles are *regulative*: they direct inquiry. They are not
*constitutive*: they do not say how nature is. Kant treats taking them as
constitutive as a source of illusion.

The engine uses them as its only means of revising its vocabulary between
anomalies:

| Principle | Operation |
|---|---|
| Homogeneity | **merge** two concepts that almost always agree into one |
| Specification | **split** a concept whose cases behave in two distinct ways |
| Continuity | **add a middle degree** between a concept's states, or an intermediate concept between two |

Being regulative, these operations only *propose*. The evidence decides
whether the proposal stands.

Homogeneity also catches a defect POE cannot see in itself. Some pairs of
POE's variables are read from the same source series, so a strong link
between them is true by definition and says nothing about the world (POE's
open problem 6). Two concepts that agree because they are the same
observation are exactly what homogeneity merges.

### Where this engine and POE differ

POE first took Popper's side of the old dispute over whether discovery has
a logic: its hypotheses were worldviews written in advance or varied
blindly, and the data only judged them (POE's REFACTOR_SPEC D3). It has
since changed sides (its D24). The worldviews had been written with
knowledge of the history they were tested on, so POE now begins with no
hypotheses and forms its own: for each programme's best explanation, the
connection the remembered evidence most supports, judged only on evidence
that comes after (POE's EPISTEMOLOGY.md §2).

So both engines now reason toward hypotheses from the evidence, and both
meet the risk Popper saw the same way: evidence that suggests a hypothesis
is not counted as confirming it, because a hypothesis earns credit only
for observations after it was proposed (section 8 here).

What remains different is the level at which they form:
- **POE forms judgments from given concepts.** Its concepts are a domain's
  hand-written signals; it forms the connections between them.
- **This engine forms the concepts as well.** It is given only
  observations, and forms the concepts it then connects.

Run on the same observations, they put a sharper question to the test than
the old one (DESIGN.md §9):
- question 2 compares formed concepts with POE's given ones, now with
  hypotheses formed from the evidence on both sides, so the comparison is
  of concepts alone;
- question 5 compares formation from anomalies with blind variation inside
  this engine.

### What the engine does not do

- **It does not guess at random.** POE still revises the hypotheses it
  forms by random change. This engine does not; every proposal has an anomaly or a
  regulative principle as its occasion. A separate experiment is to run a copy
  with random proposals instead (not yet built). Its only purpose is to test whether
  disciplined concept formation does better than blind variation. That copy
  is a control, not part of the engine's cognition. In art the controls
  that exist are of the same spirit: claims dealt at random into concepts
  of the same sizes, a feature dealt at random among the year's cases, and
  next year's features as a placebo (section 8).
- **It does not ask a language model what to think.** For economic data,
  no language model takes part in forming concepts. Art is a different
  case (section 9).

## 8. Justification: how rival schemes are judged

### The unity of apperception

At the centre of Kant's Deduction is the claim that "the *I think* must be
able to accompany all my representations" (B131–132). All my
representations belong to one self-consciousness, and only by being combined
into that one unity do they become knowledge of objects. Representations
that cannot be brought into it are, for me, nothing.

In the engine this becomes three requirements on every scheme:
1. **One whole.** A scheme is a single connected structure. It is judged as
   a whole, by the one probability it assigns to everything observed. It is
   never judged concept by concept.
2. **Answering to everything.** A scheme must give a probability to every
   observation of every week. It may not ignore a series it cannot explain.
   An observation it has no concept for is still predicted, if only crudely,
   and counts against it.
3. **No idle concepts.** A concept that connects to nothing, and makes no
   difference to what the scheme expects to observe, does not belong to the
   unity and is dropped. Kant says categories have meaning only in their
   application to possible experience (A239/B298). A hidden state that
   predicts no observable difference is, in his phrase, empty.

### Incommensurability and the common ground

Kuhn argued that rival paradigms are *incommensurable*: they divide the world
with different concepts, so there is no neutral language in which to compare
them point by point. Two of the engine's schemes with different vocabularies
are incommensurable in exactly this sense.

They are compared on what both must answer to: the observations. Each scheme
states, before each week, the probability of what will be observed; it is
scored by the probability it gave to what was observed. This is the
*prequential* principle: judge a forecaster only by its forecasts (Dawid,
1984). Its cost is the theory-ladenness conceded in section 3: the common
ground is a language we chose. Kuhn would say no ground is neutral. The
engine's answer is that its ground is at least shared and fixed in advance,
and that this is the most an engine can offer.

### Lakatos: research programmes and novel prediction

Lakatos replaced the single theory with the *research programme*: a hard core
of commitments, kept fixed, surrounded by a protective belt of auxiliary
hypotheses that is adjusted to meet the evidence ("Falsification and the
Methodology of Scientific Research Programmes", 1970). A programme is
*progressive* if its adjustments predict new facts, and *degenerating* if
they merely accommodate facts already known.

In the engine:
- **Programme:** a vocabulary, with every scheme descended from it.
- **Hard core:** its concepts.
- **Protective belt:** its links and their strengths.
- **Novel prediction:** a new concept earns credit only for observations
  made after it was proposed. It was proposed because it would have
  explained surprises already seen, so scoring it on those would reward
  accommodation, which is hindsight. This is the line between a progressive
  programme and a degenerating one, made into a rule.

### Refutation

A scheme is abandoned only when a rival has outpredicted it, on observations
both have answered to, by odds above 100 to 1. Jeffreys called a Bayes
factor of that size "decisive" (*Theory of Probability*). At least one
scheme of every programme is kept until the evidence refutes it, so that no
programme wins merely by leading early.

### Kuhn's two kinds of change

| Kuhn | In the engine |
|---|---|
| Normal science: puzzle-solving within a paradigm | the leading scheme changes *within one programme*, with the same concepts and revised links |
| Revolution: the paradigm itself is replaced | the leading *programme* changes: the engine now thinks in different concepts |

POE can have only the first kind, because its concepts are fixed. This
engine is built so that the second kind is possible, and its replays ask
whether it happens and when.

### Judging across cases (art)

In art, aggregates carried no structure and links between particular
concepts read as coincidences (ART-PLAN §8). The humanities reason
otherwise: from particular cases to what holds across them (Ginzburg's
clues; Bourdieu's consecration is a claim about every career; Moretti
reads the life cycles of genres). So in art a hypothesis is a
*mechanism*, a claim about every case at once: "a case in this state this
year tends to this outcome next year". A case is an artist, a concept or
a trend. The mechanism is judged prequentially, each year predicted from
earlier years only, against each case's own past graded finely, since any
feature that grows with size passes for a mechanism if size is graded
coarsely. Rival sets of mechanisms are kept side by side; the leader
changes when a rival stands 3 nats ahead (Jeffreys' "strong"), on
evidence that decays with a five-year half-life, and a combination must
beat each of its parts. Three controls ask what a gain means: the feature
dealt at random among the same year's cases (meaning), a case's years
shuffled (fame), and next year's feature as a placebo (order).

### Planned before it runs

Every art test was written down before it ran: what it measures, what
would count against the design, and predictions. Departures are dated and
said to be departures; failed predictions are recorded as failed; nothing
was tuned until an answer came out well (ART-PLAN throughout). A
prediction's worth is that it could have failed.

## 9. Art: knowledge from testimony

The economic domains give the engine observations: numbers measured by
others, but numbers. The art domain gives it texts, such as critics'
reviews and publications' judgments. Text is not perception. It is
*testimony*: what others assert. The epistemology of testimony is a
separate subject. Hume treated testimony as a kind of evidence whose
reliability is itself learned from experience ("Of Miracles", *Enquiry*
§10); later work, such as Coady (*Testimony*, 1992), argues that we depend
on testimony more basically than that.

Testimony must be *understood* before it can be weighed, and understanding a
text is not something counting words can do. So the art engine needs a
language model, and its epistemology differs from the economic one. The
proposed boundary:

- **The model reads.** It reports what each text asserts, in a fixed form:
  who asserts, about what, what is asserted (in the text's own words), its
  force (reports, judges, predicts, doubts) and its stance (approval,
  disapproval, neither). Since ART-PLAN 15.2 it also reports each claim's
  subject (a person, a work, an institution, something else) and whether
  it is about the life of a person who makes art. No categories of ours:
  the model does not sort claims into themes we chose.
- **The engine judges.** From those reported assertions it forms concepts
  under the same table, tests them, and gives them up, exactly as it does
  with numbers. Learning how far each source is to be trusted is planned,
  not built (ART-PLAN §4).

The model's role is then that of apprehension: taking up the given. The
engine's role is understanding and judgment. Where hypotheses come from
stays principled, because the model never proposes what to believe. The
boundary is settled (ART-PLAN §2) and was amended once, with the user's
approval, for the two parts added in 15.2: both record what a claim
refers to, not what it means or whether it is right.

### The engine judges the reader

The reading is checked by code, not trusted. An answer outside the form is
refused, never repaired. Every name and number a claim uses must be in its
article or byline; about 2% fail, and analysis reads only the checked copy
(ART-PLAN §6).

Two other models shape what is shown, and neither proposes a belief. An
embedding model decides which claims are near in meaning, so it shapes
concepts and trends, under thresholds fixed by rule on a pilot month. A
local model names each trend, says whether it is a particular theme or art
in general, and checks whether its name fits ten of its claims; a trend is
listed only if half fit. That decides what is displayed, not what is
predicted (ART-PLAN §§6, 11).

### The model writes; code and the readers judge

The art reports end with an imagined artist: a short life, built from what
critics said about the lives of real artists who had a kind of success
(ART-PLAN 15.1, 15.9–15.19). Here a model writes, and the boundary has to
hold the other way round: what it writes must say nothing the claims do
not.
- **Every sentence cites its claims;** code refuses a sentence that cites
  none, or a claim it was not given.
- **The word rule.** Every word must be in the claims the sentence cites,
  or in a fixed list of words that assert nothing; no word of time, cause
  or contrast unless a claim has it. A sentence that fails is cut. This is
  the engine judging, by a rule anyone can read.
- **Two readers.** Two models from different makers each read every
  sentence beside its claims and answer y or n in a fixed form: n if it
  adds an event, feeling, place, date, reason or judgement, reverses a
  claim, or makes it more certain or more general. Code keeps a sentence
  only if both say y.
- **Write again, edit, check again.** A life left short is written again,
  and the write kept is chosen by a count of sentences, never by what they
  say. The writer may then edit the life to read well; the edit passes the
  same checks and is kept only if it still uses every claim the checked
  life used.
- **Open to check.** Every cut sentence is shown with why, beside the life
  as first checked.

This must be faced squarely: the readers are models making judgments of
entailment. The boundary is no longer "the model only reads". It is that
models give verdicts in a fixed form, and code decides by a rule (both must
say y, and the word rule), so no model's verdict alone keeps a sentence.
The same pattern governs the reports: their verdicts (too small to claim,
overwhelming, what a control shows) are fixed by code, and the writer only
states them. The imagined artist is labelled fiction. It is not knowledge
about anyone; it is the discourse, recast, under a check that it adds
nothing.

### Description is not prediction

Some of what art shows describes the present and claims nothing about what
comes next: this year's trend lists, the market's image (which shows what goes
with a place at the top of the market, by the user's choice), and the lives
told about the artists who succeeded. Each is said to be
description where it is shown. And nothing is written into the inputs to
make a thesis come out: features are the table's headings applied to every
case alike, and word lists used to audit a result are fed into nothing
(ART-PLAN 15.11).

## 10. Where the engine departs from Kant

These departures are known and accepted:

1. **No a priori knowledge.** For Kant, the principle that every event has a
   cause is synthetic a priori: known independently of experience and
   necessarily true of it. The engine's table of forms is fixed in advance,
   but it is a design choice, not knowledge. The engine's "necessity" is
   invariance across observed regimes, which is a mark of necessity, not
   necessity itself.
2. **Particular laws are empirical, as in Kant.** Kant held that particular
   laws of nature cannot be derived from the categories and must be learned
   from experience (B165). Here the engine agrees with him. Its links are
   learned, and the table only limits their form.
3. **No space.** The engine has a form of time but none of outer space
   (section 3).
4. **The given is conceptualized by others.** Its intuitions are the
   products of statistical agencies' concepts (section 3).
5. **Judgment without the gift.** Its judgment is practice alone; it has
   no mother wit (section 7).
6. **The schemata are our reading.** Taking substance as persistence,
   community as a shared hidden state, and necessity as invariance are
   interpretations. Each is defended above, but none is the only reading of
   Kant.
7. **No transcendental subject.** The unity of apperception is modelled as a
   structural requirement on schemes, not as a self-consciousness. The
   engine has no "I think", only the formal requirement that anything which
   could be accompanied by one must hang together.
8. **In art, the given is testimony as a model reads it.** Kant's
   intuitions are received; art's are a model's report of what others
   asserted, checked by code (section 9).
9. **Recognition by nearness.** Kant's synthesis of recognition brings a
   new intuition under a concept. In art, an embedding model's nearness
   stands in for it: a claim joins the concept it is nearest (section 9).
10. **Models judge what a model wrote.** Whether a sentence of the imagined
    artist says more than its claims is judged by two models, and kept by a
    rule of code. Their verdict is not the engine's own understanding
    (section 9).

## Glossary

| Term | Meaning here |
|---|---|
| Observation (intuition) | one published value of one series, with the date it describes and the date it became public |
| Concept | a rule, built under the table of forms, that assigns a state from observations; or a hidden state posited under substance or community |
| Table of forms | the fixed set of forms a concept or link may take; the engine's analogue of the categories through their schemata |
| Scheme | one set of concepts with the links among them and their strengths |
| Programme | a vocabulary and every scheme descended from it |
| Anomaly | a run of surprise well above the leading scheme's usual |
| Association / directed dependence / community | the three grades of connection (section 6) |
| Possible / actual / necessary | a concept's status: proposed; earned credit on new observations; invariant across regimes and held by every surviving scheme |
| Claim (assertion) | in art, one thing a text asserts, as the model reports it: who, about what, what, force, stance; with subject and life since 15.2 |
| Case | in art, something with a history in the discourse: an artist, a concept, a trend |
| Mechanism | a hypothesis about every case at once: a case in this state this year tends to this outcome next year |
| Own past | a case's earlier outcomes, graded finely; what every mechanism must beat |
| Dealt control | a feature dealt at random among the cases of the same year, keeping how common it is and breaking its tie to the case |
| Year-after placebo | next year's features in place of this year's; if they do as well, the feature goes with the outcome rather than ahead of it |
| Trend | claims grouped by idea, followed across years; needs many writers and many subjects |
| Theme / life block | a trend that is a particular subject; a life block counts only its claims about a life |
| Word rule | every word of a written sentence must be in the claims it cites, or assert nothing |
| Reader | a model that judges, y or n, whether a written sentence says more than its claims |

## References

- Coady, C. A. J. *Testimony: A Philosophical Study*. Oxford, 1992.
- Dawid, A. P. "Statistical theory: the prequential approach." *Journal of
  the Royal Statistical Society A* 147 (1984).
- Ginzburg, C. *Clues, Myths, and the Historical Method*. 1989.
- Hanson, N. R. *Patterns of Discovery*. Cambridge, 1958.
- Hume, D. *A Treatise of Human Nature* (1739–40), 1.3.6; *An Enquiry
  concerning Human Understanding* (1748), §§7, 10.
- Jeffreys, H. *Theory of Probability*. Oxford, 1939; 3rd ed. 1961.
- Kant, I. *Critique of Pure Reason* (A 1781, B 1787); *Critique of the Power
  of Judgment* (1790), Introduction IV; *Jäsche Logic* (1800), §6.
- Kuhn, T. S. *The Structure of Scientific Revolutions*. Chicago, 1962.
- Lakatos, I. "Falsification and the Methodology of Scientific Research
  Programmes." In Lakatos and Musgrave (eds.), *Criticism and the Growth of
  Knowledge*. Cambridge, 1970.
- Moretti, F. *Graphs, Maps, Trees*. 2005.
- Peirce, C. S. *Collected Papers*, vol. 5, §189 (Harvard lectures, 1903).
- Peters, J., Bühlmann, P. and Meinshausen, N. "Causal inference by using
  invariant prediction." *Journal of the Royal Statistical Society B* 78
  (2016).
- Verma, T. and Pearl, J. "Equivalence and synthesis of causal models."
  *Proceedings of UAI*, 1990.
