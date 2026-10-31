# Changelog

All notable changes to doc-kit. Versions follow [SemVer](https://semver.org/).

## 0.2.0 — Playbooks and run logs as doc types
Supports the `playbook` skill: workflows worked out by trial and error get a checked home next to the other docs.

- **Added**
  - `kit/templates/*/docs/templates/playbook.md`, `run-log.md` — playbook (steps with done-conditions, gotchas, verify) and its run log (dated attempts table).
  - Presets: types `playbook` (requires `runs`; prose rules apply; ~1,200-word budget) and `runlog` (exempt from prose rules); `last_run` date field.
  - `tests/test_doclint.py` — `Playbooks`: templates lint clean in both presets, per-type statuses, required fields, first person allowed in run logs.
- **Changed**
  - `kit/tools/doclint.py` — `check_front_matter`: `types.<type>.enums` override the global enums, so a design project's playbooks use `draft · current · deprecated` while specs keep their lifecycle.
  - Templates: CONVENTIONS doc-type tables and PROJECT_STRUCTURE list `playbooks/`.
  - `CONFIG.md`, `SKILL.md` — document the above.

## 0.1.1 — Separate in-scope ideas from ruled-out ones
The parking lot mixed ideas waiting for their layer with ideas rejected for the project; the first graduate, the second never should.

- **Changed**
  - `kit/templates/*/docs/parking-lot.md` — added an *Out of scope* section (one line + reason; never graduates).
  - `kit/templates/*/docs/CONVENTIONS.md` — parking-lot rules describe both lists.
  - `kit/tools/doclint.py` — version 0.1.1 (no behaviour change).

## 0.1.0 — Initial kit, generalized from Wayfarer's doclint
Wayfarer's lint proved that mechanical doc rules work best as a deterministic check; this release makes it reusable across projects via config.

- **Added**
  - `kit/tools/doclint.py` — config-driven lint core (stdlib only, Python 3.7+).
    - `Project` / `Doc` — discovery, front matter parsing, section-aware line walk.
    - Checks: links, stale terms + glossary retired names, front matter (types, required keys, enums, dates, code table, id-path match, unique ids), decision logs, mirror files, rule/question IDs and tags (incl. section-only tags), cross-file ID references, index listing, prose rules, custom regex patterns, word budget.
    - `build_map` — generated index from the code table (`source: codes`) or from every file's front matter (`source: files`).
    - Plugin hooks: `check_any`, `check_migrated`, `check_project`, `summary`, `verbose`.
  - `kit/tools/doclint_plugins/style.py` — optional warnings: long sentences, bold density (IDs excluded), emoji in prose.
  - `kit/presets/basic.json`, `kit/presets/design.json` — starting configs.
  - `kit/templates/basic/`, `kit/templates/design/` — entry files (README, PROJECT_STRUCTURE, CONVENTIONS, GLOSSARY, map) and, for design, spec/decisions/data templates, vision, parking lot, open-questions index.
  - `kit/tools/hooks/pre-commit` — errors block commits, warnings don't.
  - `examples/wayfarer/` — Wayfarer config + plugin (migration inbox, provisional-rule citations, legacy open-question entries).
  - `tests/test_doclint.py` — 27 unit tests incl. clean-scaffold checks for both template sets.
  - `tests/regression_wayfarer.py` — fault-injection comparison against Wayfarer's original lint.
  - `CONFIG.md` — configuration reference.
- **Changed** (vs. Wayfarer's original lint)
  - First-person check also catches sentence-initial "My".
  - Three messages reworded to be project-neutral (code table, changelog heading, provisional tag).
  - Design preset: release-scheduling pattern also catches "v2." at a sentence end; Wayfarer's example config keeps the original pattern.
- **Fixed**
  - Unknown front-matter `type` reported as an error; the original lint crashed with a `TypeError`.
