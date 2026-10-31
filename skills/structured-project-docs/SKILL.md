---
name: "structured-project-docs"
description: "Organize project documentation into a clean, navigable file tree of small, single-topic Markdown files instead of large monolithic docs. Use this whenever creating, structuring, or reorganizing a project's docs, notes, specs, or design records in a folder or repo — especially in Claude Cowork — or whenever a Markdown file is growing large or starts covering more than one topic, even if the user doesn't explicitly ask for \"structure.\" Trigger when setting up a new project's documentation, when a doc needs splitting, or when a folder layout has become messy or ad hoc."
---

# Structured Project Docs

Keep a project's documentation as a **clean, navigable file tree of small, single-topic Markdown files**. The file tree is the project's memory: someone should understand the project's shape by scanning the folders, and grasp any one file in a single sitting.

Apply this by default to documentation work. Briefly say what you did and why.

**The meta-principle: state each thing once, link or generate everywhere else.** Facts have one owner. Status lives in front matter and indexes are generated from it. Names live in the glossary. Rules live in the conventions file.

## Scope

- **Applies to:** multi-file documentation in a folder or repo — Cowork projects, connected folders, code repositories.
- **Other skills cover:** a single standalone document (one Docs artifact) and chat replies (report-style).
- **Project conventions win.** If the project has a conventions file, it overrides this skill where the two differ.
- **Related skills:** **design-capture** decides what goes into spec vs. decision history vs. parking lot; **layered-design-facilitation** decides which layer a thought belongs to; **playbook** writes repeatable workflow guides and their run logs; **doc-kit** holds the lint and the file templates. This skill decides structure and how persistent docs are written.

## Core principles

1. **One concern per file.** Split by topic, not by length. A second distinct concern is the signal to split, however short the file is.
2. **Size the structure to the project.** A tiny project may be `README.md` + `docs/`. Create folders when they hold real content; give a large project enough folders to stay scannable.
3. **Navigability over dogma.** A root index almost always earns its keep; a per-folder index once scanning the folder gets hard. Relative links, so the tree is traversable from any entry point. Add tables of contents and cross-links only where someone will use them.
4. **Many small linked files over one big one.** Cross-link to the owner of a fact.
5. **Predictable naming.** `kebab-case`, descriptive names; numeric prefixes only when order matters.

## Entry files

For any project beyond a handful of files, set up these entry points (templates in **doc-kit**; trim to what the project needs):

| File | Job |
|---|---|
| `README.md` | What this is + a short *Start here* list of links |
| `PROJECT_STRUCTURE.md` | The folder tree, plus a **"Where does X go?"** list that answers placement before it becomes a question |
| `docs/CONVENTIONS.md` | Binding rules: doc types, front matter, writing rules, workflows. **Changes need the user's explicit approval** |
| `docs/GLOSSARY.md` | Naming authority. Row: **Term · Means · Owner · Not to be confused with**. Retired names in their own table |
| `docs/MAP.md` (or `SYSTEM_MAP.md`) | Index of docs with type and status, **generated** from front matter |
| `docs/parking-lot.md` | One line per idea not yet placed; a separate *Out of scope* section for ideas ruled out |

## Content folders (adapt to the project)

```
docs/
├── <area>/      # one folder per topic area (design/<domain>/ in design projects)
├── decisions/   # decision records or per-spec decision history
├── playbooks/   # repeatable workflow guides; runs/ holds their run logs
├── research/    # sourced external knowledge
├── planning/    # open-question index, roadmaps, audits
└── archive/     # finished point-in-time docs; nothing here is current
```

If a folder would hold a single short file, keep the file one level up until it grows. Propose the tree (and why it fits) before creating it.

## Doc types

Define the project's doc types in CONVENTIONS as a table with a **Never contains** column. Defining a type by what it excludes is what stops drift (a spec holds no history; an index holds no discussion; a playbook holds no dead ends).

- **Indexes point.** An index line is ID or title + one line + link; the content lives in its owner. Resolved entries are deleted.
- **Load-bearing files get stricter rules.** Files every session reads (glossary, vision, map, conventions) are where an error spreads furthest; give each its own short rule set in CONVENTIONS.
- **Front matter** (title, type, status, updated, optionally id) on every structured doc, so status is stated once and indexes can be generated.
- **Point-in-time docs** (audits, reviews, logs) move to `archive/` when finished.

## Writing rules for persistent docs

1. **Current state only.** Present tense; history goes to a decision record, run log or git.
2. **Replace superseded text** by deleting it.
3. **Headings are labels**: plain nouns for what follows.
4. **Restrained emphasis.** Bold only defined terms at first use and IDs. Salience survives only when little is highlighted.
5. **Status is metadata.** Tags, table columns or front matter carry it.
6. **No author voice.** Claude's own proposals and corrections stay in chat, decision history or run logs.
7. **One term per concept**, checked against the glossary before naming anything. A term new to the reader is defined by what it does the first time it appears.
8. **One owner per fact.** Everywhere else links to it.

## Enforcement

Mechanical rules (links, front matter, retired names, headings, strikethrough, first person) belong in a lint. For projects past a handful of files, offer to install **doc-kit**'s doclint and pre-commit hook; once installed, run it after every docs change before reporting the change as done.

## When to split a file

- Split when a file covers **more than one distinct topic**. Each result gets one topic and a clear name.
- When you move content, leave a one-line pointer so links keep working.
- Length is only a soft prompt (about 1,500 words): look for hidden sub-topics; keep a coherent topic in one file.

## Reorganizing an existing mess

1. Inventory and group the content by topic; list contradictions between files.
2. Propose a target tree, doc types and the split plan **before** moving anything.
3. Split along topic seams, create the entry files, fix the links, settle contradictions (newer ruling wins; the rest go to the user).
4. Summarize what moved where.

Done when every file has one topic, every link resolves, and the lint (if installed) is clean.

## Working style

Propose the structure or split plan and the reasoning briefly before executing. Keep the docs concise — structure should cut noise, not add ceremony.