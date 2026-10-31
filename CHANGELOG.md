# Changelog

All notable changes to doc-kit. Versions follow [SemVer](https://semver.org/).

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
