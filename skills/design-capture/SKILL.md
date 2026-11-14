---
name: "design-capture"
description: "Turn a user's free-form design talk (rambling ideas, answers to questions, batches of decisions) into structured project documentation. Use whenever the user is working through an open-ended design project with a docs tree — game design, system architecture, product concepts, requirements — and their message contains decisions, ideas, or answers that need recording."
---

# Design Capture — turning talk into documentation

A repeatable procedure for converting design conversation into docs that state the **current design precisely**, keep the **reasoning retrievable**, and **stay consistent**.

## 0. Project conventions win

Before writing anything, look for a conventions file (e.g. `docs/CONVENTIONS.md`) and a lint (e.g. `tools/doclint.py`). **If they exist, they are binding and override this skill wherever the two differ.** Read them at the start of every session; run the lint before and after editing. A new design project without conventions gets them from **doc-kit**'s `design` templates and preset (propose first).

## 1. The model

**Division of labor.** **layered-design-facilitation** owns altitude in the conversation and defines the layer stack and the moves between layers: **L0 vision → L1 intent → L2 mechanics → L3 parameters → L4 implementation**; park, probe, ascend. This skill owns recording. **structured-project-docs** owns the file tree and the writing rules for persistent docs.

**Layers in the docs.** Know which (system, layer) you are recording for. Content settles at most one layer below where the system is. Above L3, quantities are recorded as **orderings** ("A above B") or **tiers**; a number that has to stay is tagged `placeholder`.

**Two kinds of document per system:**
- **The spec** states the current design only: intent, numbered rules, parameters, open questions.
- **The decision history** (a separate file at a mirrored path) holds immutable entries for **pivotal decisions**: what was decided, why, what was rejected, what it supersedes.

Specs answer "what is true?"; history is loaded only to answer "why?". Keeping them apart keeps specs short and stops readers (human or model) from picking a superseded version.

**Pivotal decisions.** A decision gets a history entry when it does at least one of these:
1. It reverses or supersedes a recorded rule.
2. It chooses among alternatives that were seriously considered.
3. Its reason could not be inferred from the spec's intent.
4. It is hard to reverse.

Every other rule is written into the spec only; version control keeps its history.

**One owner per fact.** Every rule, number and definition lives in exactly one file. Summary files (glossary, stat registry, system map, vision) define and link to the owner.

**Default vocabulary** (when the project defines none):

| Item | Values |
|---|---|
| System status | `idea` · `drafting` (working notes allowed) · `settled` (L2 decided; changes need a decision entry) · `validated` (rules confirmed by a probe, a prototype or the implementation) · `locked` (frozen on purpose) · `deferred` |
| Rule tag | `locked` (decided) · `leaning` (only under *Provisional rules*, citing its open question) · `placeholder` (a number that only ranks things) · `conflicting` (contradicts another rule and is knowingly left open; cites the other rule's ID) |
| Question tag | `blocking` (gates the next status/layer; listed in the open-questions index) · `major` · `minor` · `needs-build` (closable only by building or playing) · `deferred` |
| IDs | Rule `ARC-R7`, question `ARC-Q2`, decision `D-ARC-006`; never reused |

**Parking lot vs. out of scope.** Two separate lists:
- **Parking lot**: in-scope ideas not yet ready, one line each, grouped by system and tagged with the target layer, e.g. `- [combat, L3] crit chance scales with stamina`. Location: `parking-lot.md` at the docs root, or a *Parked* section in the owning spec if the project prefers. When the system reaches that layer, pull the entries into the spec and delete them from the lot.
- **Out of scope**: ideas consciously ruled out of this project, one line each with the reason, in an *Out of scope* section of the parking lot (or the vision's *Scope*). They return only if the project's scope is redrawn.

## 2. Procedure for each message

### 2.1 Check before writing
For each decision in the message, search the owning spec and the specs it names (by glossary term and rule ID) for rules it touches.

- **A recorded rule conflicts with it:** quote that rule verbatim with its ID and the date it was decided, and ask which holds: the new statement supersedes the rule, the rule stays, or both stay tagged `conflicting` with an open question that tracks them. Record after the answer.
- **It restates a recorded rule:** cite the ID and move on.
- **It contradicts something the user said earlier in the session:** same procedure. The quoted rule is the reminder.

### 2.2 Sort
| Bucket | Destination |
|---|---|
| **Decision** | Rule in the owning spec; plus a decision-history entry if it is pivotal |
| **Reversal of an earlier decision** | Rule replaced, and a history entry that names what it supersedes. **Say explicitly in the reply that a past ruling is being reversed**, even if the user didn't |
| **New idea, current system** | Spec (as a rule if decided, as an open question if not, or in working notes while drafting) |
| **Idea for another system or layer** | Parking lot, one line, in the canonical format |
| **Idea ruled out** | *Out of scope*, one line with the reason |
| **New term or rename** | Glossary in the same change; the old name goes to *Retired names* |
| **Open question** | Owner's open-questions section, tagged and sized to one decision (split a larger one, framing part first); an index entry only if `blocking` or cross-system |
| **Quantity above L3** | The ordering or tier it implies, as a rule; the raw number goes to the parking lot for L3 |
| **Number at L3** | Parameters |
| **Probe finding** | *Provisional rules* (`leaning`) or a `placeholder` value, citing the question the probe serves. When the probe ends: the question is answered (a rule), reworded, or stays open |
| **Lower-layer finding that breaks an upper rule (ascend)** | The upper rule goes through 2.1 at its own layer; the outcome is a pivotal decision; the sweep in 2.4 runs upward |
| **Timing ("in v2", "later")** | Planning docs, once the design reaches L3–L4; specs state what a system does |

### 2.3 Write
- **Replace superseded text.** Delete it from the spec; the decision history keeps the old version.
- **Rules are atomic, present tense, ID'd and tagged** (e.g. `ARC-R7 … \`locked\``). Anything undecided is a question.
- **Headings are labels.**
- **Specs have no author voice.** The assistant's own proposals, mistakes and corrections live outside the spec; a rejected proposal worth remembering is a one-line "Rejected" item in the decision history.
- **Restrained emphasis.** Bold only defined terms at first use and IDs.
- **Brainstorming has a home.** Systems in `idea`/`drafting` may keep a free-form *Working notes* section. When the system settles, distil the notes into rules and pivotal decision entries and delete the section.
- **Decision entries are immutable.** The only edit is appending `· superseded by D-…`.

### 2.4 Ripple sweep
After every change, search the whole tree for the old fact or name and fix it at the owner or delete it elsewhere. Sweep **across and upward**: a change that came from a lower layer also checks the system map, the vision and every spec that traces to the changed rule. Retired names go to the glossary's *Retired names* table, retired facts to the stale-terms list, so the lint catches them from then on.

A sweep round can introduce new inconsistencies. Run the lint after each round and repeat until a round changes nothing.

Done when the search for the old wording returns only the decision history, the retired-names table, and rules tagged `conflicting` with their open question.

### 2.5 Report
Run the lint until clean. The reply for a capture turn has this shape:

1. **State**: system · layer · status, one line.
2. **Recorded**: every rule and question written or changed, by ID, with its text as written. The user reviews the rules themselves.
3. **Reversals and conflicts**: what was superseded, what is tagged `conflicting`.
4. **Needed from you**: the next questions, each sized to one decision.

Reasoning, alternatives and background follow on request.

### 2.6 Handoff page
At a checkpoint, build an **HTML handoff page** (an artifact where the session offers one) in place of a long Markdown report. Checkpoints: the end of a session, a layer change, the end of a probe, a whole-project review, or any report that would run past about one screen.

The page shows:
- The state of each system (layer, status) as a map or diagram.
- What changed since the last checkpoint: rules by ID, grouped by system.
- Reversals, conflicts and overrides.
- Open decisions as selectable options that assemble into one answer block the user copies back into the chat.
- Diagrams wherever a structure, flow or dependency is easier to see than to read.
- Parking-lot additions.

The page is a view generated from the docs tree. The tree owns every fact: answers given on the page come back through the chat and are captured by this procedure.

## 3. Critical review

Capture includes review. Check new material for contradictions with existing rules, ripple effects, load-bearing gaps, scope creep, and violations of the project's stated pillars. Report them as findings; the user decides.

- **Match the requested mode.** Capture-only requests get capture plus flagged blockers; critique requests get critique, sized to what matters.
- **Verify premises a decision depends on** (game numbers, physics, external facts, version-specific behavior) before building on them, and say when something could not be verified.
- **Unknown detail becomes an open question.**

## 4. Migrating an existing doc set

When bringing older docs under conventions, one file or small domain at a time:

1. Read the file; grep the tree for its key terms to find every file that restates its facts. List contradictions; settle those a newer ruling covers, take the rest to the user.
2. Write the new spec from the template: current state only, IDs and tags.
3. Create the mirror decision file; backfill only pivotal decisions that still explain a current rule or stop a rejected idea from returning (mark them `backfilled`).
4. Delete changelogs, struck text, resolved-question lists, reviews and debate from the old version.
5. Fix every file that restated the migrated facts: link by ID or delete.
6. Run the lint until clean; the user reviews and commits. From the commit on, IDs are permanent.

## 5. Housekeeping

- History lives in version control and the decision history.
- Keep specs within a size budget (about 1,500 words); split a system that outgrows it.
- Resolved questions are deleted from indexes.
- Superseded documents move to an archive folder with a "historical" note.
- Before descending to numbers or implementation, audit the tree for drift and contradictions.
- After a build or play round: close the `needs-build` questions it answered, record what it overturned as an ascend, and set a system to `validated` once its rules are confirmed.
