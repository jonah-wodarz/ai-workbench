---
name: "fair-practice-questions"
description: "Write practice questions that can't be answered by test-wiseness alone. Use WHENEVER generating study material that tests knowledge — multiple-choice questions, quizzes, practice/mock exams (Probeklausuren), \"list N things\" questions, or any question set with right/wrong answers — including when it will be shown in the quiz widget or built as a quiz artifact. Trigger on \"practice questions\", \"Übungsaufgaben\", \"Probeklausur\", \"quiz me\", \"MC-Fragen\", even without a mention of fairness."
---

# Fair Practice Questions

## Why this exists

Practice questions are only useful if answering them requires the knowledge they're
supposed to test. When an item can be solved by pattern-matching on the *form* of the
options instead of the *content*, the learner gets false confidence: they "get it right"
in practice and then fail the real exam, where the examiner controlled for those tells.

This phenomenon is called **test-wiseness**: scoring points from cues in how a question
is built rather than from subject knowledge. Your job when authoring practice material is
to make test-wiseness fail — so the only reliable way to answer is to actually know the
answer.

Everything below is about the *content generation* step: the moment you write the
questions, options, and answer keys. It applies whatever the output format — plain text,
Markdown, the quiz widget, or a quiz artifact. Do the fairness work here, before
rendering anything.

## The four giveaways to eliminate

### 1. Length / detail parity (the biggest tell)

The single most common giveaway: the correct option is written more carefully than the
distractors — longer, more qualified, more precise ("... under most circumstances,
provided X holds"), while the wrong ones are terse. Learners learn to just pick the
wordy, hedged one.

Fix the *form* so it carries no signal:

- Make all options roughly the same length (within a few words of each other). If the
  correct answer needs a qualifier to be true, either add comparable qualifiers to
  distractors or rewrite the correct answer to be crisp.
- Match grammatical structure and specificity across options. If the key names a specific
  mechanism, distractors should name specific (wrong) mechanisms too — not vague
  hand-waves.
- Don't let hedging words ("usually", "can", "may", "in general") cluster on the correct
  answer. Absolute words ("always", "never", "only") shouldn't cluster on distractors
  either — that's the inverse tell.

**Example (bad → good), topic: database transactions (ACID)**

Bad — the key is obviously the detailed one:
- A) It's fast.
- B) Isolation ensures that concurrently executing transactions produce a result
  equivalent to some serial execution, so intermediate states are never visible to
  others.
- C) It saves space.
- D) It uses SQL.

Good — every option is a specific, comparable claim; you must know isolation to pick B:
- A) Durability ensures committed changes survive a crash by persisting them to
  non-volatile storage.
- B) Isolation ensures concurrent transactions don't see each other's intermediate,
  uncommitted state.
- C) Atomicity ensures a transaction either fully completes or leaves no effect at all.
- D) Consistency ensures every transaction moves the database between valid states that
  satisfy all defined constraints.

Note the good version also turns the distractors into *real* ACID properties — so the
item now tests whether the learner can tell the four apart, which is the actual learning
objective.

### 2. Enumeration count parity ("name N things")

When the answer is a set — "name the components of X", "welche vier Ebenen hat …" — a
frequent tell is that the correct list has N items and every wrong option has N−1 (or is
padded to a different length). Count alone reveals the answer.

- Give every option the **same number of items** as the correct one.
- Build distractor lists by swapping in plausible-but-wrong members, not by dropping or
  adding members. Keep genuine parallelism: same granularity, same category of thing.
- If the question is open-ended ("list the steps"), don't accidentally encode the count in
  the prompt unless the count is itself part of what's being taught.

**Example, topic: OSI layers**

Bad (counts differ — pick the 3-item one):
- A) Physical, Data Link, Network
- B) Physical, Data Link
- C) Physical
- D) Physical, Data Link, Network, and it's the standard model

Good (all three-item; you must know the actual sequence):
- A) Physical, Data Link, Network
- B) Physical, Data Link, Session
- C) Physical, Transport, Network
- D) Data Link, Network, Transport

### 3. On-topic, plausible distractors

If a wrong option has nothing to do with the subject, it's free elimination — it teaches
nothing and shrinks the effective choice set. Every distractor should be something a
learner who *half*-understands the material might actually believe.

- Draw distractors from the same domain and the same conceptual neighborhood as the key.
- Prefer **common misconceptions, adjacent concepts, and classic mistakes** as
  distractors — these are the most instructive, because falling for one reveals a real
  gap. (E.g., for "normalization removes redundancy", a great distractor is "indexing
  removes redundancy" — a real thing people confuse it with.)
- Avoid joke options, obviously-from-another-chapter options, and distractors that are
  false for a reason unrelated to the concept being tested.
- Keep "all of the above" / "none of the above" rare; when used, make sure they're the
  correct answer about as often as any other position, and never the longest option.

### 4. Spoiler decoupling in multi-question sets (Probeklausuren)

In an exam or a longer set, a later question can reveal the answer to an earlier one:
Q1 asks *which* of A/B/C it is; Q3 asks "explain why it's B" — now Q1 is free. This
destroys the value of the earlier question.

Before finalizing a set, read it as a whole and decouple:

- **Scan for leaks:** does any question's stem, options, or answer state a fact that is
  the answer to another question? This includes hints and explanations if they'll be
  visible before later questions are answered.
- **Fix by reformulating, not just reordering.** Reordering alone often doesn't help
  (the later item still spoils on review). Instead: make the later question
  self-contained ("Given a system that uses optimistic locking, explain …" rather than
  "Explain why the answer to Q1 is optimistic locking"), or make earlier and later
  questions probe *different* instances so neither reveals the other.
- **Keep answer keys and rationales out of question stems.** Don't reference "as we saw in
  Q1" or name the earlier answer.
- If two questions genuinely must chain (building on the same scenario), design them so
  the second tests something the first didn't already give away — e.g., Q1 asks the
  learner to *identify* the mechanism from a scenario, Q2 gives the mechanism explicitly
  and asks them to *apply* it to a new twist.

## Also worth avoiding (secondary tells)

Keep these in mind; they're the same idea applied to smaller cues:

- **Answer-position bias:** don't let the correct answer sit in the same slot repeatedly
  (e.g., always B). Distribute correct positions roughly evenly across a set, ideally
  shuffled.
- **Grammatical agreement:** the stem shouldn't grammatically fit only the correct option
  ("an ___" ruling out consonant-start distractors, or singular/plural agreement; in German
  also article/case agreement).
- **Verbal echo:** avoid repeating a distinctive word from the stem only in the correct
  option — repetition acts as a pointer.
- **Convergence:** don't let the correct answer be the one that shares the most elements
  with the other options (the "average" of the distractors is a known test-taking heuristic).
- **Overlapping / non-mutually-exclusive options** that let a test-taker use logic (if two
  options can't both be wrong, one must be right) instead of knowledge.
- **Hint leakage:** a hint should narrow the reasoning, not name the key or rule out all
  but one option by form.

## Workflow

1. **Author the content normally** — get the questions and the *correct* answers right
   first. Substance before polish.
2. **Generate distractors deliberately** using misconceptions and adjacent concepts (see
   giveaway #3), not filler.
3. **Run the self-audit** below over the whole set.
4. **Revise** any item that fails, then render it in the target format (see Output).

## Self-audit checklist (run before delivering)

For **each MC item**:
- [ ] Options are within a few words of the same length; no option is conspicuously the
      most detailed/hedged.
- [ ] Every distractor is on-topic and plausible to a partial learner (ideally a real
      misconception or adjacent concept).
- [ ] "List N" options all have the same item count as the key.
- [ ] Grammar of the stem fits every option equally; no verbal echo between stem and key.
- [ ] No absolute/hedge-word clustering; "all/none of the above" not overused.
- [ ] The hint doesn't give the answer away.

For the **set as a whole**:
- [ ] No question (stem, options, hint, or visible explanation) reveals the answer to
      another.
- [ ] Correct-answer positions are distributed, not clustered in one slot.
- [ ] Each distractor, if chosen, would reveal a *specific* gap worth learning from.

If you can answer any item correctly using only the checklist tells above — without the
subject knowledge — rewrite it. That's the whole test.

## Output

Pick the format by how the questions will be used; the fairness work is identical.

| Use | Format |
|---|---|
| Quick self-test in the chat | **Quiz widget** (also offers a flashcard view of the same questions) |
| A set the user will keep, redo, or share (e.g. a Probeklausur) | **Quiz artifact** (self-contained HTML page) |
| Printable exam or Musterlösung | Document / text, answer key separate from the questions |

**Quiz widget mapping:** each item gets `options` with short ids (`a`–`d`), a
`correct_option_id`, an `explanation` (why the key is right *and* why the most tempting
distractor is wrong), and optionally a `hint`. Give each question its own short
`correct_feedback` / `incorrect_feedback`. The widget may shuffle options, but still
distribute correct positions yourself — don't rely on the shuffle.

**Language:** write questions in the language of the course material; explanations
follow the user's language (German explanations for German-taught courses unless the user
asks otherwise). Keep established technical terms in English.

**Pure recall cards** (term → definition) are less affected by option tells, but still
apply spoiler decoupling across the deck.