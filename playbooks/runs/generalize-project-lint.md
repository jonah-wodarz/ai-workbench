---
title: Generalize a project lint into a reusable tool — run log
type: runlog
updated: 2026-10-31
---
# Generalize a project lint into a reusable tool — run log
Playbook: [`../generalize-project-lint.md`](../generalize-project-lint.md). One entry per run, newest at the bottom.

### Run 1 — 2026-10-31 — doc-kit from a game-design project's doclint
Goal: make a 517-line, project-specific docs lint reusable, cross-device, without breaking the project.

| # | Tried | Result | Why / lesson |
|---|---|---|---|
| 1 | Staged `docs/` and `tools/` only, ran the original lint | 2 broken-link errors | The docs link into a `references/` folder that wasn't copied. Placeholders fixed it; later also staged root-level `README.md` and `PROJECT_STRUCTURE.md`, which the lint scans too |
| 2 | Read the whole script, sorted checks into generic / config / project-only | ~70% generic; project-only: migration inbox, provisional-rule citations, legacy entries | The mapping drove the config schema and the plugin boundary |
| 3 | Kept output format identical, made three messages project-neutral | Comparison by location still works | Identical format is what makes old-vs-new comparison cheap |
| 4 | Fault-injection harness, 38 scenarios | 37 identical on the first full run | One "difference" was the original crashing on an unknown `type:`; harness reported it as a pass because the traceback exited with 1. Switched to detecting `Traceback` |
| 5 | Unit tests (25) | 3 failures | Two were my own miscounted line numbers; one was real: first-person check missed capital "My". Fixed in the core, re-ran the regression: clean tree still 0 findings, one expected stricter catch |
| 6 | Same audit for the release-scheduling pattern | "v2." at a sentence end slipped through | Fixed only in the new design preset; the project's own config stays faithful |
| 7 | Scaffold tests for both template sets | Design template failed | A placeholder link in the open-questions template. The test exists exactly for this |
| 8 | Packaging: skill zip + git bundle | Zip upload under Settings worked | Confirms a multi-file skill with scripts can be distributed this way |

**Outcome:** done. doc-kit 0.1.0, later 0.2.0. Playbook drafted from this run.
