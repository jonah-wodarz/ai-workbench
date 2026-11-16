# Set checks

## Spoiler decoupling

A later question can reveal an earlier answer (Q1 asks which of A/B/C, Q3 asks "explain why it is B").

- Scan stems, options, hints and any explanation visible before later items are answered for another item's answer.
- Reformulate; reordering alone does not help on review. Make the later item self-contained ("Given a system that uses optimistic locking, explain ...") or probe different instances.
- Keep references such as "as in Q1" and named earlier answers out of stems.
- Chained items: Q1 asks to identify the mechanism from a scenario, Q2 names the mechanism and asks to apply it to a new twist.

## Key patterns

Count key positions across the set. Avoid a repeating cycle (A, B, C, D, A, B, C, D), strict alternation, a fixed slot, and runs of the same slot. Check the pattern over the whole key, including across sections of an exam. For true/false sets, mix the ratio and the order.

## Lesson-content leakage

Exercises inside a lesson page can be answered from the page itself.

- Reword options so no option copies the sentence, heading, bold term or caption that sits next to the exercise. Test a new case that applies the lesson's idea.
- Feedback shown after item 1 must not state the answer to item 2.
- The answer is absent from headings, alt text, image captions, tooltips and the introduction of the same page.
- Static HTML carries the key in its source (a `data-correct` attribute or script). Say so when the exercise is graded for the learner and not for the user.
- Exercise and lesson text come from the same source: write the exercise from the learning objective, then check it against the lesson text for verbatim overlap.
