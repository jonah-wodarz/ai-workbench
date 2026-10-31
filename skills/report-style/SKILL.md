---
name: "report-style"
description: "House style for written deliverables and work summaries: bottom line first, one term per concept, terms defined by what they do, visuals where they carry the comparison. Use when writing a document, report, review, README or write-up, or the summary at the end of multi-step work."
---

# Report Style

The reader should get the point from the first lines, find any detail by scanning, and never wonder what a word means. Applies in English and German.

**Scope:** written deliverables (documents, reports, reviews, READMEs, write-ups) and the chat summary after multi-step work. Quick conversational answers follow the user's preferences only.

**Project conventions win:** if the project defines its own doc conventions, they override this skill where the two differ.

## 1. Bottom line first (BLUF)

- Open with the result: the answer, conclusion, or decision needed, in one to three lines.
- Then the support, ordered by importance, not by the order the work happened.
- If the reader must act, say so up front: "Decision needed: X" / "Action: Y".
- Start directly with content; the work's steps stay out of the text.

## 2. Terms

- **One term per concept.** Pick a term and keep it across the whole text, including headings and tables (one thing is always "skill", never also "module" or "plugin").
- **Define by function.** When a term is ambiguous, new to the reader, or a proper name the reader may not know, say what it *does* in this context the first time it appears: not just "doclint", but "doclint (the script that checks the docs against the conventions)".
- After that first definition, use the bare term.
- Different concepts get different terms, even if related.
- **Refer by name; IDs ride inside.** Write "the Archery spec (ARC)" or "the precision rule (ARC-R13)", so a line of references stays readable at a glance.

## 3. Sentences

- One idea per sentence. Active voice; passive only when the actor is unknown or irrelevant.
- Aim for under ~25 words. Split long chains of clauses.
- Prefer the verb over a noun construction: "decide", not "make a decision".
- **German:** write verbal style instead of Nominalstil ("Durchführung einer Prüfung" -> "prüfen") and split Schachtelsätze into separate sentences. Keep established technical terms in English.

## 4. Structure

- Headings are labels for what follows.
- Bullets for parallel items; numbered lists for sequences; prose for reasoning that depends on its own steps.
- Keep each section to one topic; split long documents into sections or files (see structured-project-docs).
- Put uncertainty next to the claim it affects ("unverified", "assumption").

## 5. Visuals

Use a visual when it carries the content better than text.

| Content | Visual |
|---|---|
| 3+ items compared on shared attributes | Table |
| Process, flow, dependencies, structure | Diagram |
| Numbers over time or across categories | Chart |
| Status of many items | Table with a status column |

- A visual must be readable on its own: clear headers, units, a one-line title or caption if needed.
- After a visual, state its takeaway in one sentence and let the visual carry the details.

## 6. Summary after multi-step work

1. **Outcome:** what exists now or what was found (one to three lines).
2. **Decisions needed / open points:** only if any.
3. **Details:** the essentials, usually a table; point to files for the rest.
4. **Next steps:** one or more, concrete.

## Self-check before delivering

- [ ] Could the reader stop after the first three lines and know the result?
- [ ] Every concept has exactly one term; unfamiliar terms are defined by what they do; references read as names.
- [ ] Every sentence reads correctly the first time.
- [ ] Every comparison of 3+ items is a table; every flow is a diagram or a numbered list.
- [ ] Prose adds the takeaway to each visual, nothing more.