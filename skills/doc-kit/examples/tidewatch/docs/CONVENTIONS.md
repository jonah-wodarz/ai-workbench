# Documentation Conventions

How every document in `docs/` is structured and written. This file is binding: when a doc and this file disagree, the doc gets fixed. **Instruction-writing rule:** a rule that must always hold is enforced by `tools/doclint.py` and marked (lint) here, pointing to the check; the other rules are short and say what to do. Changes need the design lead's explicit approval.

## Skills in use

Skills are loaded by name at the start of the session; this table is what triggers them.

| When | Skill |
|---|---|
| Start of a design session, or the talk drifts between layers | `layered-design-facilitation` |
| A message contains decisions, ideas or answers to record | `design-capture` |
| Creating, moving or splitting files | `structured-project-docs` |
| Setting up or running the lint | `doc-kit` |
| A recurring workflow needs figuring out | `playbook`, where installed |

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
| `playbook` | `docs/playbooks/` | One repeatable workflow: steps with done-conditions, gotchas, verification. Status `draft` · `current` · `deprecated` | Run history, dead ends |
| `runlog` | `docs/playbooks/runs/` | Dated runs of one playbook: what was tried, results, why | Current procedure |
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

Content settles at most one layer below where a system is. Above L3, quantities are **orderings** ("A above B") or **tiers** (low / mid / high, or named); a number that must be kept is tagged `placeholder` (lint: warns below L3).

- **Park** — file an out-of-layer or other-system idea in the parking lot.
- **Probe** — a bounded descent to a lower layer that answers one named open question of the layer above. Findings sit under *Provisional rules*, cite that question, and are reported back up.
- **Ascend** — a lower-layer finding that breaks an upper-layer rule reopens that rule.

## 4. Front matter

Keys as in `docs/templates/spec.md` (lint: keys, values, dates). `layer` is the deepest layer reached; `depends_on` lists system codes; `id` is the code from section 5.

| `status` | Meaning |
|---|---|
| `idea` | Intent only. Working notes allowed |
| `drafting` | Rules forming. Working notes allowed |
| `settled` | L2 decided. Changes require a decision entry |
| `validated` | Rules confirmed by a probe, a prototype or the implementation |
| `locked` | Frozen on purpose. Reopening requires a decision entry that says so |
| `deferred` | Out of current scope |

## 5. IDs

| Item | Format | Example |
|---|---|---|
| Interface item | `<CODE>-I<n>` | `ARC-I1` |
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
| `WEA` | design/world/weather.md |
| `SHP` | design/world/ships.md |
| `LMP` | design/keeper/lamp.md |

## 6. Spec structure

Sections in this order; omit a section only if it would be empty, except *Rules*. Template: `docs/templates/spec.md`. Budget: about 1,500 words excluding working notes; above that, split the system.

**Interface** — one line per **interface item**: what other systems may rely on. A rule or parameter that refers to another system cites its code or one of its interface items, never its rule ID. Keep `depends_on` short and free of cycles. The limit is five systems; a project that needs another limit changes `coupling.max_fan_out` in `tools/doclint.json` and states the reason here. (lint: foreign rule IDs, fan-out, cycles, interface IDs)

**Rule tags** (lint) — one per rule, at the end: `locked` (decided), `leaning` (preferred, not final; only under *Provisional rules*, citing its open question), `placeholder` (a number that must be kept for now), `conflicting` (contradicts another rule and is knowingly left open; each cites the other's ID and an open question tracks it). Other undecided content is an open question, not a rule.

**Question tags** (lint) — one per question, at the end: `blocking` (gates the next status or layer; listed in `planning/OPEN_QUESTIONS.md`), `major` (changes a rule here or elsewhere), `minor` (tuning, L3), `deferred` (waits on something), `needs-build` (closable only by building or playing; leaves the discussion queue and is listed under *Needs build* in `planning/OPEN_QUESTIONS.md` for the next probe). Resolved questions are deleted; the answer becomes a rule and, if pivotal, a decision entry. **Question size:** one question asks for one decision, answerable in a sentence or by choosing among named options; a larger question is split, framing question first.

## 7. Decision history

Entry format: `docs/templates/decisions.md` (lint: heading ID, file code). Optional field: `supersedes D-ARC-003`.

Entries are immutable; the only edit is appending `· superseded by D-…`. Newest at the bottom. A cross-system decision lives in the history of the spec that owns the resulting rule.

**Pivotal decisions only:** an entry exists when a decision (1) reverses or supersedes a recorded rule, (2) chooses among seriously considered alternatives, (3) has a reason not inferable from the spec's intent, or (4) is hard to reverse. Other rules are written into the spec; git keeps their history.

## 8. Load-bearing files

- **`GLOSSARY.md`** — naming authority. Check before naming anything; update in the same change. One row per term: **Term · Means · Owner · Not to be confused with**. Numbers and rules live with their owners. Retired names go in its *Retired names* table (read by the lint).
- **`design/DESIGN_VISION.md`** — L0 and L1 only; mechanics, numbers and rule IDs live in specs. Pillars carry IDs (`VIS-P1`).
- **`SYSTEM_MAP.md`** — generated by `python tools/doclint.py --map`. Only the introduction is hand-written. `system-map.html` is the same state as an interactive page with the dependency graph, written by `--system-map`.
- **`planning/OPEN_QUESTIONS.md`** — an index: ID · question · link, one line each; discussion stays in the spec, resolved entries are deleted.
- **`design/parking-lot.md`** — in-scope ideas not yet ready: one line per idea, under its system and target layer; deleted when the system absorbs it. Its *Out of scope* section holds ideas ruled out, with the reason; they never graduate.
- **`tools/stale-terms.txt`** — retired facts, one regex per line.

## 9. Writing rules

1. Present tense, current state; dates, verdicts and words like "now", "previously" or "revised" belong in decision history.
2. Replace superseded text. (lint)
3. Headings are topic labels. (lint: emoji, dates)
4. Bold marks defined terms at first use and IDs. (lint: bold density, ★)
5. Status lives in tags and front matter. (lint: emoji)
6. Use impersonal wording. (lint)
7. One owner per fact; one claim per rule.
8. A term new to the reader is defined by what it does the first time it appears.
9. Specs state what a system does, not when it ships. Scheduling waits for L3–L4 and then gets one home in planning.

**Working notes** are exempt from these rules and the lint while a system is `idea` or `drafting`. When it settles, they are distilled into rules and pivotal decision entries and the section is deleted.

## 10. Workflows

**Capturing a ruling:** search for recorded rules it conflicts with and settle them first (supersede, keep, or tag both `conflicting`) → edit the rule in its owner → add a decision entry if the ruling is pivotal → search the tree for the old fact and fix or delete it → update `updated:` → run the lint.

**Renaming a term:** rename everywhere outside `decisions/` and `archive/` → update the glossary row and add the old name to *Retired names* → decision entry → lint.

**Retiring a fact:** add its old wording to `tools/stale-terms.txt`.

**Before committing:** `python tools/doclint.py`. Enable the hook once per clone: `git config core.hooksPath tools/hooks`.
