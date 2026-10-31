---
title: Package a skill for upload
type: playbook
status: draft
updated: 2026-10-31
runs: 1
last_run: 2026-10-31
---
# Package a skill for upload
> Get a skill into the user's account when a skill proposal card can't carry it: skills with scripts or extra files, and third-party skills installed unchanged.

## When to use
- The skill has more than a SKILL.md (scripts, templates, reference files).
- A third-party skill is installed as-is.

Single-file skills the assistant writes go through a skill proposal card instead.

## Prerequisites
- The skill folder, with `SKILL.md` at its root and valid front matter (`name`, `description`).
- For third-party skills: their license allows redistribution.

## Steps
1. **Shape the folder** — `<name>/SKILL.md` at the top, supporting files beside or below it; no caches (`__pycache__`, `.git`). Done when `SKILL.md` is the only file the description depends on to make sense.
2. **Include the license** — for third-party skills, copy the source repo's license into the folder. Done when the folder carries the license text.
3. **Zip the folder itself** — the archive contains `<name>/…`, not the folder's contents loose: `zip -r <name>.zip <name> -x '<name>/.git/*'`. Done when `unzip -l` shows `<name>/SKILL.md`.
4. **Hand it over** — send the zip to the user; they upload it under Settings → Skills. A new upload of the same name replaces the installed version.
5. **Confirm the install** — the skill appears in the session's available-skills list (often from the next turn on). Done when it is listed.
6. **Keep a source of truth** — the folder lives in a git repo; the zip is a build artifact, rebuilt on every change.

## Gotchas
- **Card can't carry it** — skill proposal cards transmit only `SKILL.md`; extra files are lost. Use the zip.
- **References to dropped files** — after rewriting a third-party SKILL.md through a card, its pointers to bundled files may dangle; check every relative path.

## Verify
- The skill is listed, and its first use can read its bundled files from the skill's folder.

## See also
- Run log: [`runs/package-skill-for-upload.md`](runs/package-skill-for-upload.md)
