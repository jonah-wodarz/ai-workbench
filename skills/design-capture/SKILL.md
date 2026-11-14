---
name: "design-capture"
description: "Turn a user's free-form design talk (rambling ideas, answers to questions, batches of decisions) into structured project documentation. Use whenever the user is working through an open-ended design project with a docs tree — game design, system architecture, product concepts, requirements — and their message contains decisions, ideas, or answers that need recording."
---

# Design Capture

Converts design conversation into docs that state the current design precisely, keep the reasoning retrievable, and stay consistent.

**First:** read the project's conventions file (e.g. `docs/CONVENTIONS.md`) and find its lint (e.g. `tools/doclint.py`). They are binding and override this skill. Run the lint before and after editing. A design project without conventions gets them from **doc-kit**'s `design` preset (propose first); until then use the defaults in [references/vocabulary.md](references/vocabulary.md).

## Model

- **layered-design-facilitation** owns the layers (L0 vision to L4 implementation) and the moves between them (park, probe, ascend). This skill records. **structured-project-docs** owns the file tree and the writing rules.
- Each system has a **spec** (current design only: intent, interface, rules, parameters, open questions) and a **decision history** at a mirrored path (immutable entries for pivotal decisions). The spec answers "what is true?"; the history is read only to answer "why?".
- **One owner per fact.** Summary files (glossary, system map, vision) define and link to the owner.
- A decision is **pivotal** when it reverses or supersedes a recorded rule, chooses among seriously considered alternatives, has a reason that the spec's intent does not explain, or is hard to reverse. Every other rule goes into the spec only; version control keeps its history.
- Content settles at most one layer below the system's layer. Above L3, quantities are **orderings** or **tiers**.
- A spec's **interface** lists what other systems may rely on, as interface items (`ARC-I1`). A rule that refers to another system cites that system's code or one of its interface items.

## Procedure for each message

### 1. Check
For each decision in the message, search the owning spec and the specs it names for rules it touches.

- **A recorded rule conflicts with it:** quote the rule verbatim with its ID and the date it was decided, and ask which holds: the new statement supersedes the rule, the rule stays, or both stay tagged `conflicting` with an open question that tracks them. Record after the answer.
- **It restates a recorded rule:** cite the ID and move on.
- **It contradicts something said earlier in the session:** same procedure; the quoted rule is the reminder.

### 2. Sort

| In the message | Goes to |
|---|---|
| Decision | Rule in the owning spec; a history entry if it is pivotal |
| Reversal | Rule replaced; a history entry naming what it supersedes. Say in the reply that a past ruling is reversed |
| Idea for the current system | A rule if decided, an open question if not, working notes while the system is drafting |
| Idea for another system or layer | Parking lot, one line: `- [combat, L3] crit chance scales with stamina` |
| Idea ruled out | *Out of scope*, one line with the reason |
| New term or rename | Glossary in the same change; the old name goes to *Retired names* |
| Open question | The owner's open questions, tagged and sized to one decision; an index entry if `blocking` or cross-system |
| Quantity above L3 | The ordering or tier it implies, as a rule; the raw number is parked for L3 |
| Probe finding | *Provisional rules* (`leaning`) or a `placeholder` value, citing the question the probe serves. At the end of the probe the question is answered, reworded, or stays open |
| Lower-layer finding that breaks an upper rule | The upper rule goes through step 1 at its own layer; the outcome is pivotal; the sweep in step 4 runs upward |
| Something needed from another system | An interface item in that system's spec, or an open question there |
| Timing ("in v2", "later") | Planning docs, from L3 on |

### 3. Write
- Replace superseded text; the decision history keeps the old version.
- Rules are atomic, present tense, ID'd and tagged. Anything undecided is a question.
- Specs carry the design only. Claude's proposals and corrections stay in the chat; a rejected proposal worth remembering is a one-line "Rejected" item in the history.
- A system in `idea` or `drafting` may keep free-form *Working notes*. When it settles, distil them into rules and pivotal entries and delete the section.
- Decision entries are immutable; the only edit is appending `· superseded by D-…`.

### 4. Sweep
Search the whole tree for the old fact or name and fix it at the owner or delete it elsewhere. Sweep across and upward: a change that came from a lower layer also checks the system map, the vision and every spec that relies on the changed interface. Retired names go to the glossary's *Retired names* table and retired facts to the stale-terms list, so the lint catches them from then on.

Run the lint after each round and repeat until a round changes nothing. Done when the old wording remains only in the decision history, the retired-names table, and rules tagged `conflicting`.

### 5. Report
The reply for a capture turn:

1. **State**: system · layer · status, one line.
2. **Recorded**: every rule and question written or changed, by ID, with its text as written.
3. **Reversals and conflicts**.
4. **Needed from you**: the next questions, one decision each.

Reasoning and background follow on request. At a checkpoint (end of a session, a layer change, the end of a probe, a whole-project review, or a report longer than about one screen) build a page with the **handoff** skill in place of a long report.

## Review while capturing

Check new material for contradictions with recorded rules, ripple effects, gaps that other rules depend on, scope creep, and conflicts with the vision's pillars. Report them as findings; the user decides.

- A capture-only request gets capture plus flagged blockers; a critique request gets critique.
- Verify the premises a decision depends on (external facts, version-specific behaviour) before building on them, and say what could not be verified.
- An unknown detail becomes an open question.

## Housekeeping

- Keep a spec within about 1,500 words; split a system that outgrows it.
- Delete resolved questions from indexes. Move superseded documents to the archive.
- Before descending to numbers or implementation, audit the tree for drift and contradictions.
- After a build or play round: close the `needs-build` questions it answered, record what it overturned, and set a system to `validated` once its rules are confirmed.
- Bringing older docs under conventions: [references/migration.md](references/migration.md).
