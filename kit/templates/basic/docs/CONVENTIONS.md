# Documentation Conventions

How every document in `docs/` is structured and written. This file is binding: if a doc and this file disagree, this file wins and the doc gets fixed. `tools/doclint.py` checks the mechanical parts. Changes to this file need <OWNER>'s explicit approval.

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
| `ideas` | `docs/` | `parking-lot`: one line per idea | Discussion, decisions |

`docs/archive/` holds superseded point-in-time documents. Nothing in it is current.

## 3. Front matter

```yaml
---
title: Setup guide
type: doc                 # doc | registry | index | ideas
status: current           # doc only: draft | current | deprecated
updated: 2026-10-31
---
```

## 4. Load-bearing files

- **`GLOSSARY.md`** is the naming authority. Check it before naming anything; update it in the same change as any new or renamed term. One row per term: **Term · Means (one line) · Owner · Not to be confused with**. No numbers or rules. Retired names go only in its *Retired names* table, which the lint reads.
- **`MAP.md`** is generated: `python tools/doclint.py --map`. Only its introduction is hand-written.
- **`tools/stale-terms.txt`** lists retired *facts*, one regex per line.

## 5. Writing rules

1. Present tense, current state. No "now", "previously", "revised" in content.
2. Replace superseded text; never strike it through.
3. Headings are labels. No emoji, dates or verdicts in headings.
4. Bold only defined terms at first use. No decorative markers.
5. Status lives in front matter or tags, never as emoji in prose.
6. No first person.
7. One term per concept; a term new to the reader is defined by what it does the first time it appears.
8. About 1,500 words per doc at most; above that, split by topic.

## 6. Workflows

**Renaming a term:** rename everywhere outside `archive/`, update the glossary row, add the old name to *Retired names* with a lint pattern, run the lint.

**Retiring a fact:** add its old wording to `tools/stale-terms.txt`.

**Before committing:** `python tools/doclint.py`. Enable the hook once per clone: `git config core.hooksPath tools/hooks`.
