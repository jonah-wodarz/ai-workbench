---
name: doc-kit
description: Scaffold, lint and enforce conventions for a multi-file Markdown docs project with a config-driven checker (doclint) and entry-file templates. Use when setting up a new docs project or repo, adding a docs lint or pre-commit hook, running or extending doclint, or migrating an existing doc tree onto checked conventions.
---

# doc-kit

Mechanical doc rules get a deterministic check; prose rules are kept for judgment. This kit holds the check (`doclint`), two presets and two template sets. **structured-project-docs** decides the structure and writing rules; **design-capture** decides how design talk becomes specs. This skill installs and runs the tooling.

## Contents (paths relative to this skill's folder)

| Path | What it is |
|---|---|
| `kit/tools/doclint.py` | The lint. Stdlib only, Python 3.7+ |
| `kit/tools/doclint_plugins/style.py` | Optional style warnings (sentence length, bold density, emoji) |
| `kit/tools/hooks/pre-commit` | Runs the lint before commits; errors block |
| `kit/presets/basic.json` | Any docs project: front matter, links, glossary retired names, prose rules, generated map |
| `kit/presets/design.json` | Design projects (design-capture): specs + decision history, IDs, tags, L0-L4, open-questions index |
| `kit/templates/basic/`, `kit/templates/design/` | Entry files: README, PROJECT_STRUCTURE, CONVENTIONS, GLOSSARY, map, parking lot (+ spec/decisions/data templates for design) |
| `CONFIG.md` | Every config key and plugin hook |
| `examples/wayfarer/` | A real project's config + plugin, for reference |

Find this skill's folder first (the folder containing this SKILL.md) and copy from there.

## New project

1. **Pick the preset**: `design` if the project is a design effort with systems, layers and decisions; otherwise `basic`. Ask if unclear.
2. **Propose the tree** (from the template's `PROJECT_STRUCTURE.md`, trimmed to what the project needs) and get a yes before creating files.
3. **Copy**: `kit/templates/<preset>/` → project root; `kit/tools/` → `<root>/tools/`; `kit/presets/<preset>.json` → `<root>/tools/doclint.json`.
4. **Fill placeholders**: project name, `<OWNER>` in CONVENTIONS, today's date for every `YYYY-MM-DD`. For `design`: add each system to the code table in `CONVENTIONS.md` §5 before creating its file.
5. **Run** `python tools/doclint.py` until it reports 0 errors. Generate the map with `--map` and paste it under the map file's introduction.
6. **Hook** (git projects): `git config core.hooksPath tools/hooks`.

If the project is on the user's linked computer, write files there with the device tools; run the lint there if Python is available, otherwise in the workspace on a staged copy.

## Existing project

1. Inventory: what doc types exist, what front matter (if any), where names and statuses live.
2. Start from the closer preset; adapt `types`, `enums`, `codes`, exemptions to what the project already does. **Fit the config to the project's conventions, not the reverse**; propose convention changes separately.
3. Run once with `--verbose`. Files without front matter are "not yet migrated" and get only link and stale-term checks, so migration can go file by file.
4. Report findings grouped by kind; fix mechanical ones, take judgment calls to the user.

## Extending

- A new project rule that is a pattern on one line → `prose.patterns` in the config.
- A new retired name → the glossary's *Retired names* table. A retired fact → `tools/stale-terms.txt`.
- Anything config can't express → a plugin in `tools/doclint_plugins/` (hooks in `CONFIG.md`). Keep project-specific plugins in the project.

## Running in a session

- Run the lint after every docs change you make, before reporting the change as done.
- Errors block; warnings are reported, not necessarily fixed.
- Never edit a generated map table by hand; regenerate it.
- Changes to `CONVENTIONS.md` or `doclint.json` need the user's approval: they change what "correct" means.
