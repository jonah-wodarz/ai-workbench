---
name: "fair-practice-questions"
description: "Write graded exercises and practice questions that cannot be solved by test-wiseness alone. Use WHENEVER content has right and wrong answers: multiple-choice, true/false, sorting, ordering, matching, fill-in, \"list N things\" questions, flash cards, quizzes, practice or mock exams (Probeklausuren), and exercises embedded in lesson pages (including teach lessons), in any output (chat, quiz widget, quiz artifact, HTML, document). Triggers: \"practice questions\", \"Übungsaufgaben\", \"Probeklausur\", \"MC-Fragen\", \"quiz me\", \"flashcards\", \"Karteikarten\", \"sort these\", \"match the pairs\", even without a mention of fairness. Boundary: lesson design and teaching flow belong to teach; this skill owns how items, options and answer keys are built."
---

# Fair Practice Questions

An item is fair when only subject knowledge answers it. Cues from the form of the question (**test-wiseness**) give false confidence, and the learner then fails the real exam. Apply these steps while writing items, before any rendering.

## Steps

1. **Write the content first**: questions and correct answers, correct before polished.
2. **Build distractors from real misconceptions**: adjacent concepts and classic mistakes from the same domain, each one a plausible belief of a half-informed learner. Choosing it should reveal one specific gap. No joke options, no off-topic options.
3. **Remove the form cues** (below); details and examples in [giveaways.md](references/giveaways.md).
4. **Check the set as a whole** for leaks, key patterns and lesson-content leakage: [set-checks.md](references/set-checks.md).
5. **Run the audit** below and rewrite every failing item.
6. **Render** by the use: [output-formats.md](references/output-formats.md).

## Form cues to remove

| Cue | Rule |
|---|---|
| Length and detail | All options within a few words of each other, same structure and specificity; hedges ("usually", "may") and absolutes ("always", "never") spread evenly, not clustered on key or distractors |
| Item count | In "name N things" items every option has N items; build distractors by swapping members, not by dropping or adding |
| Grammar and echo | The stem fits every option (article, number, case); no distinctive stem word repeated only in the key |
| Overlap and convergence | Options are mutually exclusive; the key is not the option sharing most elements with the others |
| "All/none of the above" | Rare, correct as often as any other position, never the longest option |
| Hints | A hint narrows the reasoning, never names the key or leaves one option by form |
| Sorting and matching | Extra items on one side, no pre-placed pair, a presented order that differs from the key, buckets of unequal size, partner texts without shared words |
| Flash cards | Front never contains the back's wording; one fact per card |

## Audit

For each item:
- [ ] Without the subject knowledge, no cue in the form points to the key.
- [ ] Every distractor is on-topic and reveals a specific gap.
- [ ] Stem, hint and visible explanation do not state the key.

For the set:
- [ ] No item reveals another item's answer ([set-checks.md](references/set-checks.md)).
- [ ] Key positions vary with no repeating cycle.
- [ ] Neither the lesson text, headings, captions nor page source hands over an answer.

If a checklist tell alone answers an item, rewrite it.

## Troubleshooting

- **Skill skipped for an exercise inside a lesson page, a sorting or matching task, or flash cards**: all are in scope; apply steps 2 to 5.
- **Options copied from the lesson sentence above the exercise**: reword the options and test a new case ([set-checks.md](references/set-checks.md)).
