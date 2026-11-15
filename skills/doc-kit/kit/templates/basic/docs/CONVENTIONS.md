# Documentation Conventions

How every document in `docs/` is structured and written. This file is binding: when a doc and this file disagree, the doc gets fixed. **Instruction-writing rule:** a rule that must always hold is enforced by `tools/doclint.py` and marked (lint) here, pointing to the check; the other rules are short and say what to do. Changes need <OWNER>'s explicit approval.

## Skills in use

Skills are loaded by name at the start of the session; this table is what triggers them.

| When | Skill |
|---|---|
| Creating, moving or splitting files | `structured-project-docs` |
| Setting up or running the lint | `doc-kit` |
| A recurring workflow needs figuring out | `playbook`, where installed |

## 1. Principles

1. **Every fact has one owner.** Everywhere else links to it.
2. **State once, generate the rest.** Status lives in front matter; the [map](MAP.md) is generated from it.
3. **Docs describe the current state.** How it got there lives in git history or a decision record.

## 2. Document types

| Type | Lives in | Contains | Never contains |
|---|---|---|---|
| `doc` | `docs/<area>/` | One topic | A second topic; history; debate |
| `registry` | `docs/` | `GLOSSARY` | Behaviour or numbers owned elsewhere |
| `index` | `docs/` | `MAP` (generated), other lists of links | Content; discussion |
| `playbook` | `docs/playbooks/` | One repeatable workflow: steps with done-conditions, gotchas, verification | Run history, dead ends |
| `runlog` | `docs/playbooks/runs/` | Dated runs of one playbook: what was tried, results, why | Current procedure |
| `ideas` | `docs/` | `parking-lot`: one line per in-scope idea; *Out of scope* section for ideas ruled out | Discussion, decisions |

`docs/archive/` holds superseded point-in-time documents. Nothing in it is current.

## 3. Front matter

```yaml
---
title: Setup guide
type: doc                 # doc | registry | index | ideas | playbook | runlog
status: current           # doc and playbook: draft | current | deprecated
updated: 2026-10-31
---
```

## 4. Load-bearing files

- **`GLOSSARY.md`** is the naming authority. Check it before naming anything; update it in the same change as any new or renamed term. One row per term: **Term · Means (one line) · Owner · Not to be confused with**. Numbers and rules live with their owners. Retired names go in its *Retired names* table, which the lint reads.
- **`MAP.md`** is generated: `python tools/doclint.py --map`. Only its introduction is hand-written.
- **`tools/stale-terms.txt`** lists retired *facts*, one regex per line.

## 5. Writing rules

1. Present tense, current state; words like "now", "previously" or "revised" belong in git history or a decision record.
2. Replace superseded text. (lint)
3. Headings are topic labels. (lint: emoji, dates)
4. Bold marks defined terms at first use. (lint: bold density, ★)
5. Status lives in front matter or tags. (lint: emoji)
6. Use impersonal wording. (lint)
7. One term per concept; a term new to the reader is defined by what it does the first time it appears.
8. About 1,500 words per doc; above that, split by topic. (lint)

## 6. Workflows

**Renaming a term:** rename everywhere outside `archive/`, update the glossary row, add the old name to *Retired names* with a lint pattern, run the lint.

**Retiring a fact:** add its old wording to `tools/stale-terms.txt`.

**Before committing:** `python tools/doclint.py`. Enable the hook once per clone: `git config core.hooksPath tools/hooks`.
