---
name: "structured-project-docs"
description: "Organize project documentation into a clean, navigable file tree of small, single-topic Markdown files instead of large monolithic docs. Use this whenever creating, structuring, or reorganizing a project's docs, notes, specs, or design records in a folder or repo — especially in Claude Cowork — or whenever a Markdown file is growing large or starts covering more than one topic, even if the user doesn't explicitly ask for \"structure.\" Trigger when setting up a new project's documentation, when a doc needs splitting, or when a folder layout has become messy or ad hoc."
---

# Structured Project Docs

Keep a project's documentation as a navigable tree of small, single-topic Markdown files: the project's shape is visible from the folders, and any one file can be grasped in a single sitting.

**State each thing once; link or generate everywhere else.** Facts have one owner. Status lives in front matter and indexes are generated from it. Names live in the glossary. Rules live in the conventions file.

A project's own conventions file overrides this skill. Propose a tree or a split plan, with the reason, before creating or moving files.

## Structure

1. **One concern per file.** Split by topic. A second distinct concern is the signal to split, however short the file is; length (about 1,500 words) is only a prompt to look for one.
2. **Size the tree to the project.** A tiny project is `README.md` plus `docs/`. A folder exists once it holds real content; a single short file stays one level up.
3. **Predictable names.** `kebab-case`, descriptive; numeric prefixes only when order matters.
4. **Relative links** to the owner of a fact. When content moves, leave a one-line pointer.

## Entry files

For a project beyond a handful of files (templates in **doc-kit**; trim to what the project needs):

| File | Job |
|---|---|
| `README.md` | What this is, plus a short *Start here* list |
| `PROJECT_STRUCTURE.md` | The folder tree and a "Where does X go?" list |
| `docs/CONVENTIONS.md` | Binding rules: doc types, front matter, writing rules, workflows. Opens with a *Skills in use* table (when → skill), the pointer that loads the right skill by name. Changes need the user's approval |
| `docs/GLOSSARY.md` | Naming authority. Row: Term · Means · Owner · Not to be confused with. Retired names in their own table |
| `docs/MAP.md` or `SYSTEM_MAP.md` | Index of docs with type and status, generated from front matter |
| `docs/parking-lot.md` | One line per idea not yet placed; a separate *Out of scope* section |

## Content folders

```
docs/
├── <area>/      # one folder per topic area (design/<domain>/ in design projects)
├── decisions/   # decision history (pivotal decisions)
├── playbooks/   # repeatable workflow guides; runs/ holds their run logs
├── research/    # sourced external knowledge
├── planning/    # open-question index, roadmaps, audits
└── archive/     # finished point-in-time docs; nothing here is current
```

## Doc types

Define the project's doc types in CONVENTIONS as a table with a **Never contains** column: a type defined by what it excludes resists drift (a spec holds no history, an index holds no discussion).

- **Front matter** (title, type, status, updated, optionally id) on every structured doc.
- **Indexes point**: ID or title, one line, link. Resolved entries are deleted.
- **Files every session reads** (glossary, vision, map, conventions) get their own short rule set in CONVENTIONS, because an error there spreads furthest.
- **Point-in-time docs** (audits, reviews, logs) move to `archive/` when finished.

## Writing rules for persistent docs

1. Current state, present tense. History goes to a decision history, a run log or git.
2. Replace superseded text.
3. Headings are plain noun labels.
4. Bold marks defined terms at first use and IDs.
5. Status lives in tags, table columns or front matter.
6. Impersonal wording. Claude's proposals and corrections stay in chat, decision history or run logs.
7. One term per concept, checked against the glossary before naming anything. A new term is defined by what it does at first use.
8. One owner per fact; everywhere else links to it.

## Writing rules for instruction files

Conventions files, `CLAUDE.md` or `AGENTS.md`, and skills are read as instructions, often in every session.

1. A rule that must always hold is enforced by a script (lint, hook, test). The file points to the check.
2. A rule that should usually hold stays as prose, as short as its impact allows. A rule with little impact is cut.
3. Rules say what to do: "write the current state" in place of "don't write history".
4. An always-read file holds what the tree cannot show and the lint cannot check.

## Enforcement

Mechanical rules (links, front matter, retired names, headings, coupling) belong in a lint. For a project past a handful of files, offer **doc-kit**'s doclint and pre-commit hook. Once installed, run it after every docs change before reporting the change as done.

## Reorganizing an existing tree

1. Inventory the content by topic and list contradictions between files.
2. Propose the target tree, the doc types and the split plan.
3. Split along topic seams, create the entry files, fix the links, settle contradictions (the newer ruling wins; the rest go to the user).
4. Summarize what moved where.

Done when every file has one topic, every link resolves, and the lint is clean.

## Related skills

**design-capture** decides what goes into spec, decision history and parking lot. **layered-design-facilitation** decides which layer a thought belongs to. **playbook** writes workflow guides and run logs. **doc-kit** holds the lint and the templates. A single standalone document or a chat reply is outside this skill (see **report-style**).
