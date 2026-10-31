---
title: Generalize a project lint into a reusable tool
type: playbook
status: draft
updated: 2026-10-31
runs: 1
last_run: 2026-10-31
---
# Generalize a project lint into a reusable tool
> Turn a lint script written for one project into a config-driven tool other projects can install, with proof that it still behaves exactly like the original.

## When to use
- A project has a working lint or checker, and its rules would help other projects.
- The original must keep working unchanged until the new tool has proven itself.

## Prerequisites
- Read access to the project: its docs, the lint script, its conventions file.
- Python 3 in the workspace (the lint runs there on a copy, never on the original).
- The project's conventions document, to tell project rules from generic ones.

## Steps
1. **Copy the project into the workspace** — see [stage-device-folder](stage-device-folder.md) when it lives on the user's computer. Done when the copy contains every file the lint reads.
2. **Run the original lint on the copy** — record the result as the baseline. Done when the baseline matches what the user sees on their machine (usually 0 errors).
3. **Map every check** — list each check in the script as *generic* (any project), *config* (generic logic, project-specific values) or *project-only*. Done when every function and constant is in one column.
4. **Write the core + config + plugin** — generic checks read their values from a JSON config; project-only checks move into a plugin file loaded by name. Keep output format and message wording identical where possible. Done when the core has no project names in it.
5. **Write the project's config** — reproduce the original behaviour exactly, including its quirks. Fix quirks in new presets, not in this config. Done when the config loads and runs.
6. **Build a fault-injection regression** — a harness copies the project and injects one fault per scenario (broken link, missing tag, duplicate ID, bad front matter, …). It runs old and new lint and compares findings as multisets of (level, file, line) plus exit code. Cover every check from step 3. Done when every scenario matches, or each difference is explained (deliberate rewording, a stricter check, a crash in the original).
7. **Write presets and templates for new projects** — at least one preset per project kind and the entry-file templates. Done when a scaffold test (fresh project from each template set, dates filled in) lints clean.
8. **Write unit tests for the core** — one small fixture project per check. Done when all pass from a clean clone.
9. **Version and package** — SemVer changelog, git repo with tags; as a skill: zip with SKILL.md at the folder root (see [package-skill-for-upload](package-skill-for-upload.md)). Done when the package installs and the regression still passes from a clean clone.

## Gotchas
- **False "broken link" errors in the baseline** — the copy lacks files the docs link to (images, reference folders); fix: create empty placeholders at those paths in the copy.
- **A crash looks like a normal failure** — a Python traceback also exits with code 1; fix: detect `Traceback` in stderr, not the exit code.
- **Comparison shows phantom message differences** — several findings on the same line get paired wrongly; fix: compare per location as sorted sets of messages.
- **Inherited regex gaps** — e.g. a first-person check missing a sentence-initial `My`, or a version pattern missing `v2.` at a sentence end. Fix: keep the project config faithful, fix the gap in the core or the new presets, and mark the difference as expected in the harness.
- **Template placeholders break the lint** — a placeholder written as a Markdown link points at a file that doesn't exist. Fix: the scaffold test catches it; write placeholders as code or plain text.

## Verify
- Regression: all scenarios identical or explained; generated outputs (e.g. an index map) byte-identical.
- Unit and scaffold tests pass from a clean clone.

## See also
- Run log: [`runs/generalize-project-lint.md`](runs/generalize-project-lint.md)
- Result of the first run: [doc-kit](../skills/doc-kit/SKILL.md)
