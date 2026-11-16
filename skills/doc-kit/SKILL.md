---
name: doc-kit
description: "Set up and check a multi-file Markdown docs project: scaffold a new docs project or repo from templates (basic or design preset), install and run the config-driven lint doclint and its pre-commit hook, generate the docs index and the interactive system map page, and migrate an existing doc tree onto checked conventions. Use for 'set up the docs for my new project', 'set up the documentation structure', 'lint my docs', 'add a docs pre-commit hook', 'show me the system map'."
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
| `kit/presets/design.json` | Design projects (design-capture): specs + decision history, IDs, tags, L0-L4, open-questions index, early-quantity and coupling warnings |
| `kit/templates/basic/`, `kit/templates/design/` | Entry files: README, PROJECT_STRUCTURE, CONVENTIONS, GLOSSARY, map, parking lot; `docs/templates/` with playbook and run-log (+ spec/decisions/data for design) |
| `CONFIG.md` | Every config key and plugin hook |
| `kit/tools/doclint_assets/system-map.html` | Page template that `--system-map` fills |
| `examples/bike-shop/` | A small complete project (requirements for a bike shop), for reference |

Find this skill's folder first (the folder containing this SKILL.md) and copy from there.

## New project

1. **Pick the preset**: `design` if the project is a design effort with systems, layers and decisions; otherwise `basic`. Ask if unclear.
2. **Propose the tree** (from the template's `PROJECT_STRUCTURE.md`, trimmed to what the project needs) and get a yes before creating files.
3. **Copy**: `kit/templates/<preset>/` → project root; `kit/tools/` → `<root>/tools/`; `kit/presets/<preset>.json` → `<root>/tools/doclint.json`.
4. **Fill placeholders**: project name, `<OWNER>` in CONVENTIONS, today's date for every `YYYY-MM-DD`. For `design`: add each system to the code table in `CONVENTIONS.md` §5 before creating its file.
5. **Run** `python tools/doclint.py` until it reports 0 errors. Generate the map with `--map` and paste it under the map file's introduction. For `design`, `python tools/doclint.py --system-map` also writes the interactive page `docs/system-map.html`.
6. **Hook** (git projects): `git config core.hooksPath tools/hooks`.

If the project is on the user's linked computer, write files there with the device tools; run the lint there if Python is available, otherwise in the workspace on a staged copy.

## Existing project

1. Inventory: what doc types exist, what front matter (if any), where names and statuses live.
2. Start from the closer preset; adapt `types`, `enums`, `codes`, exemptions to what the project already does. **Fit the config to the project's conventions, not the reverse**; propose convention changes separately.
3. Run once with `--verbose`. Files without front matter are "not yet migrated" and get only link and stale-term checks, so migration can go file by file.
4. Report findings grouped by kind; fix mechanical ones, take judgment calls to the user.

## Extending

- A new project rule that is a pattern on one line → `prose.patterns` in the config.
- Numbers in rules above L3 → `early_quantity`; rules citing another system's rules, high fan-out, dependency cycles → `coupling`, with `--coupling` as report (both enabled in the design preset; keys in `CONFIG.md`).
- A new retired name → the glossary's *Retired names* table. A retired fact → `tools/stale-terms.txt`.
- Anything config can't express → a plugin in `tools/doclint_plugins/` (hooks in `CONFIG.md`). Keep project-specific plugins in the project.

## Running in a session

- Run the lint after every docs change you make, before reporting the change as done.
- Errors block; warnings are reported, not necessarily fixed.
- Never edit a generated map table or `docs/system-map.html` by hand; regenerate them.
- When the user wants to see the state of the systems or their dependencies, run `--system-map` and deliver the page (as an Artifact where the session offers them). The lint writes it from front matter, so it costs no writing.
- Changes to `CONVENTIONS.md` or `doclint.json` need the user's approval: they change what "correct" means.
