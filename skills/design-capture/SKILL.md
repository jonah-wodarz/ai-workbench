---
name: "design-capture"
description: "Turn a user's free-form design talk (rambling ideas, answers to questions, batches of decisions) into structured project documentation. Use whenever the user is working through an open-ended design project with a docs tree — game design, system architecture, product concepts — and their message contains decisions, ideas, or answers that need recording."
---

# Design Capture — turning talk into documentation

A repeatable procedure for converting design conversation into docs that state the **current design precisely**, keep the **reasoning retrievable**, and **stay consistent**.

## 0. Project conventions win

Before writing anything, look for a conventions file (e.g. `docs/CONVENTIONS.md`) and a lint (e.g. `tools/doclint.py`). **If they exist, they are binding and override this skill wherever the two differ.** Read them at the start of every session; run the lint before and after editing. A new design project without conventions gets them from **doc-kit**'s `design` templates and preset (propose first).

## 1. The model

**Division of labor.** **layered-design-facilitation** owns altitude in the conversation and defines the layer stack: **L0 vision → L1 intent → L2 mechanics → L3 parameters → L4 implementation**. This skill owns recording. **structured-project-docs** owns the file tree and the writing rules for persistent docs.

**Layers in the docs.** Know which (system, layer) you are recording for. Content settles at most one layer below where the system is; numbers given during L2 work are **placeholders** and are marked as such.

**Two kinds of document per system:**
- **The spec** states the current design only: intent, numbered rules, parameters, open questions.
- **The decision history** (a separate file at a mirrored path) holds immutable entries: what was decided, why, what was rejected, what it supersedes.

Specs answer "what is true?"; history is loaded only to answer "why?". Keeping them apart is what keeps specs short and stops readers (human or model) from picking a superseded version.

**One owner per fact.** Every rule, number and definition lives in exactly one file. Summary files (glossary, stat registry, system map, vision) define and link to the owner.

**Default vocabulary** (when the project defines none):

| Item | Values |
|---|---|
| System status | `idea` · `drafting` (working notes allowed) · `settled` (L2 decided; changes need a decision entry) · `locked` (frozen on purpose) · `deferred` |
| Rule tag | `locked` · `leaning` (only under *Provisional rules*, citing its open question) · `placeholder` (a number that only ranks things) |
| Question tag | `blocking` (gates the next status/layer; listed in the open-questions index) · `major` · `minor` · `deferred` |
| IDs | Rule `ARC-R7`, question `ARC-Q2`, decision `D-ARC-006`; never reused |

**Parking lot vs. out of scope.** Two separate lists:
- **Parking lot** — in-scope ideas not yet ready: out-of-layer or out-of-system, one line each, grouped by system and tagged with the target layer, e.g. `- [combat, L3] crit chance scales with stamina`. Location: `parking-lot.md` at the docs root, or a *Parked* section in the owning spec if the project prefers. When the system reaches that layer, pull the entries into the spec and delete them from the lot.
- **Out of scope** — ideas consciously ruled out of this project: one line each with the reason, in an *Out of scope* section of the parking lot (or the vision's *Scope*). These never graduate; they return only if the project's scope is redrawn.

## 2. Procedure for each message

### 2.1 Sort first
| Bucket | Destination |
|---|---|
| **Decision** | Rule in the owning spec + entry in its decision history |
| **Reversal of an earlier decision** | Same, and the new entry names what it supersedes. **Say explicitly in the reply that a past ruling is being reversed**, even if the user didn't |
| **New idea, current system** | Spec (as a rule if decided, as an open question if not, or in working notes while drafting) |
| **Idea for another system or layer** | Parking lot, one line, in the canonical format |
| **Idea ruled out** | *Out of scope*, one line with the reason |
| **New term or rename** | Glossary in the same change; the old name goes to *Retired names* |
| **Open question** | Owner's open-questions section, tagged; an index entry only if `blocking` or cross-system |
| **Number** | Parameters, tagged as a placeholder unless the system is at L3 |
| **Timing ("in v2", "later")** | Planning docs, once the design reaches L3–L4; specs state what a system does |

### 2.2 Write
- **Replace superseded text.** Delete it from the spec; the decision history keeps the old version.
- **Rules are atomic, present tense, ID'd and tagged** (e.g. `ARC-R7 … \`locked\``). Anything undecided is a question.
- **Headings are labels.**
- **Specs have no author voice.** The assistant's own proposals, mistakes and corrections live outside the spec; a rejected proposal worth remembering is a one-line "Rejected" item in the decision history.
- **Restrained emphasis.** Bold only defined terms at first use and IDs.
- **Brainstorming has a home.** Systems in `idea`/`drafting` may keep a free-form *Working notes* section. When the system settles, distil the notes into rules and decision entries and delete the section.
- **Decision entries are immutable.** The only edit is appending `· superseded by D-…`.

### 2.3 Ripple sweep
After every change, search the whole tree for the old fact or name and fix it at the owner or delete it elsewhere. A decision usually invalidates a line in two other files; finding them in the same pass keeps the tree consistent. Retired names go to the glossary's *Retired names* table, retired facts to the stale-terms list, so the lint catches them from then on.

Done when the search for the old wording returns only the decision history and the retired-names table.

### 2.4 Close the loop
Run the lint until clean. In the reply: what was recorded, which past rulings it reverses, what is now open.

## 3. Critical review

Capture is not stenography. Check new material for contradictions with existing rules, ripple effects, load-bearing gaps, scope creep, and violations of the project's stated pillars. Report them as findings; the user decides.

- **Match the requested mode.** Capture-only requests get capture plus flagged blockers; critique requests get critique, sized to what matters.
- **Verify premises a decision depends on** (game numbers, physics, external facts, version-specific behavior) before building on them, and say when something could not be verified.
- **Unknown detail becomes an open question.**

## 4. Migrating an existing doc set

When bringing older docs under conventions, one file or small domain at a time:

1. Read the file; grep the tree for its key terms to find every file that restates its facts. List contradictions; settle those a newer ruling covers, take the rest to the user.
2. Write the new spec from the template: current state only, IDs and tags.
3. Create the mirror decision file; backfill only decisions that still explain a current rule or stop a rejected idea from returning (mark them `backfilled`).
4. Delete changelogs, struck text, resolved-question lists, reviews and debate from the old version.
5. Fix every file that restated the migrated facts: link by ID or delete.
6. Run the lint until clean; the user reviews and commits. From the commit on, IDs are permanent.

## 5. Housekeeping

- History lives in version control and the decision history.
- Keep specs within a size budget (about 1,500 words); split a system that outgrows it.
- Resolved questions are deleted from indexes.
- Superseded documents move to an archive folder with a "historical" note.
- Before descending to numbers or implementation, audit the tree for drift and contradictions.