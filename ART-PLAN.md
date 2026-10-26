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

## 7. Build order

Each step test first.

1. **Texts.** Fetch one year, read nothing yet.
2. **Pilot reading.** One year: assertions, usage, accuracy. Report back
   before going on.
3. **All years**, at the chosen depth and model.
4. **Concepts** from assertions (grouping, degrees, trust), with the random
   control.
5. **Surprises and rival explanations**, scored on what follows.
6. **Replay**, planned first, 2001–2026.
