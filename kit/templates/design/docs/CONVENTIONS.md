# Documentation Conventions

How every document in `docs/` is structured and written. This file is binding: if a doc and this file disagree, this file wins and the doc gets fixed. `tools/doclint.py` checks the mechanical parts. Changes to this file need <OWNER>'s explicit approval.

## 1. Principles

1. **Specs describe the current design only.** How it got there lives in decision history and git.
2. **Every fact has one owner.** Everywhere else links to it by ID.
3. **Everything decided is addressable.** Rules, questions and decisions carry stable IDs.
4. **Settled content is strict; drafting content is free.** See *Working notes*.
5. **State once, generate the rest.** Status lives in front matter; the system map is generated from it.

## 2. Document types

| Type | Lives in | Contains | Never contains |
|---|---|---|---|
| `spec` | `docs/design/<domain>/` | One system's intent, rules, parameters, open questions | History, rejected options, debate |
| `data` | `docs/design/<domain>/` | Tables keyed by stable row ID, one short header | Reviews, prose between rows |
| `decisions` | `docs/decisions/<same path>` | Immutable decision entries for one spec or data doc | Current-state descriptions |
| `registry` | `docs/` | `GLOSSARY`, `SYSTEM_MAP` | Numbers or mechanics owned elsewhere |
| `vision` | `docs/design/` | `DESIGN_VISION`: L0/L1 pillars and intent | Mechanics, numbers |
| `ideas` | `docs/design/` | `parking-lot`: one line per idea | Discussion, decisions |
| research | `docs/research/` | Sourced external knowledge (no front matter needed) | Project decisions |
| planning | `docs/planning/` | `OPEN_QUESTIONS` index, roadmaps, audits | Design content |

`docs/archive/` holds superseded point-in-time documents. Nothing in it is current.

Every `spec` and `data` file has a decision-history file at the **same relative path** under `docs/decisions/`, so loading `docs/design/` yields current state only.

## 3. Layers

| Layer | Question | Lives in |
|---|---|---|
| L0 Vision | Why? | `DESIGN_VISION` |
| L1 Intent | What is each system for? | `DESIGN_VISION`, each spec's *Intent* |
| L2 Mechanics | What are the rules and entities? | The spec's *Rules* |
| L3 Parameters | How much? | The spec's *Parameters*, `minor` questions |
| L4 Implementation | How, in code? | `architecture/`, code |

Never let content settle two layers below where a system is. Ideas from another system or a deeper layer go to the parking lot.

## 4. Front matter

```yaml
---
id: ARC                    # system code, section 5
title: Archery
type: spec                 # spec | data | decisions | registry | vision | ideas
domain: combat
layer: L2                  # spec only: deepest layer reached
status: drafting           # spec/data: idea | drafting | settled | locked | deferred
updated: YYYY-MM-DD
depends_on: [CHA]          # spec/data: system codes
---
```

| `status` | Meaning |
|---|---|
| `idea` | Intent only. Working notes allowed |
| `drafting` | Rules forming. Working notes allowed |
| `settled` | L2 decided. Changes require a decision entry |
| `locked` | Frozen on purpose. Reopening requires a decision entry that says so |
| `deferred` | Out of current scope |

## 5. IDs

| Item | Format | Example |
|---|---|---|
| Rule | `<CODE>-R<n>` | `ARC-R7` |
| Open question | `<CODE>-Q<n>` | `ARC-Q2` |
| Decision | `D-<CODE>-<nnn>` | `D-ARC-006` |

IDs are never reused. Reference across files by ID plus link.

### System codes

A new system gets its code here before its file is created.

| Code | File |
|---|---|
| `VIS` | design/DESIGN_VISION.md |
| `PRK` | design/parking-lot.md |
| `GLO` | GLOSSARY.md |
| `MAP` | SYSTEM_MAP.md |

## 6. Spec structure

Sections in this order; omit a section only if it would be empty, except *Rules*. Template: `docs/templates/spec.md`. Budget: about 1,500 words excluding working notes; above that, split the system.

**Rule tags** — every rule ends with exactly one: `locked` (decided), `leaning` (preferred, not final; only under *Provisional rules*, citing its open question), `placeholder` (a number that only ranks things). Anything undecided is an open question, not a rule.

**Question tags** — every open question ends with exactly one: `blocking` (gates the next status or layer; listed in `planning/OPEN_QUESTIONS.md`), `major` (changes a rule here or elsewhere), `minor` (tuning, L3), `deferred` (waits on something). Resolved questions are deleted; the answer becomes a rule and, if it changes anything, a decision entry.

## 7. Decision history

```markdown
### D-ARC-006 — Precision scales velocity per draw stage
YYYY-MM-DD · accepted · supersedes D-ARC-003 · rules ARC-R7, ARC-R8
**Decision:** …
**Why:** …
**Rejected:** option — reason; option — reason.
```

Entries are immutable; the only permitted edit is appending `· superseded by D-…`. Newest at the bottom. A cross-system decision lives in the history of the spec that owns the resulting rule.

## 8. Load-bearing files

- **`GLOSSARY.md`** — naming authority. Check before naming anything; update in the same change. One row per term: **Term · Means · Owner · Not to be confused with**. No numbers or rules. Retired names only in its *Retired names* table (read by the lint).
- **`design/DESIGN_VISION.md`** — L0 and L1 only. No mechanics, numbers or rule IDs. Pillars carry IDs (`VIS-P1`).
- **`SYSTEM_MAP.md`** — generated by `python tools/doclint.py --map`. Only the introduction is hand-written.
- **`planning/OPEN_QUESTIONS.md`** — an index: ID · question · link, one line each. Never discusses; resolved entries are deleted.
- **`design/parking-lot.md`** — one line per idea, under its system. Deleted when the system absorbs it.
- **`tools/stale-terms.txt`** — retired facts, one regex per line.

## 9. Writing rules

1. Present tense, current state. No "now", "previously", "revised", dates or verdicts in rule text.
2. Replace superseded text; never strike it through.
3. Headings are labels. No emoji, dates or verdicts in headings.
4. Bold only defined terms at first use and IDs. No decorative markers.
5. Status lives in tags and front matter, never as emoji in prose.
6. No first person.
7. One owner per fact; one claim per rule.
8. A term new to the reader is defined by what it does the first time it appears.
9. Specs state what a system does, not when it ships. Scheduling waits for L3–L4 and then gets one home in planning.

**Working notes** are exempt from these rules and the lint while a system is `idea` or `drafting`. When it settles, they are distilled into rules and decision entries and the section is deleted.

## 10. Workflows

**Capturing a ruling:** edit the rule in its owner → add a decision entry if something changed, was added or rejected → search the tree for the old fact and fix or delete it → update `updated:` → run the lint.

**Renaming a term:** rename everywhere outside `decisions/` and `archive/` → update the glossary row and add the old name to *Retired names* → decision entry → lint.

**Retiring a fact:** add its old wording to `tools/stale-terms.txt`.

**Before committing:** `python tools/doclint.py`. Enable the hook once per clone: `git config core.hooksPath tools/hooks`.
