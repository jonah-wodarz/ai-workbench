---
title: Stage a folder from the user's computer for workspace tooling
type: playbook
status: draft
updated: 2026-10-31
runs: 1
last_run: 2026-10-31
---
# Stage a folder from the user's computer for workspace tooling
> Copy a project folder from the user's linked computer into the cloud workspace, so tools that only exist there (test harnesses, renderers, packages) can run on a faithful copy while the original stays untouched.

## When to use
- The work needs tools, packages or network access the computer's shell lacks.
- The task runs destructive or experimental steps (fault injection, migrations) that must never touch the original.

## Prerequisites
- The folder is connected to the session (the user adds it; request access otherwise).
- The device tools are available: shell, file listing, staging.

## Steps
1. **Inventory on the device** — list every file the tool will read with the device shell, e.g. `find docs tools -type f`. Add every file outside them it may follow (root-level Markdown, linked assets). Done when the list covers every path the tool can reach.
2. **Convert to device paths** — staging takes the device's absolute paths (on Windows: backslashes, drive letter). Build them from the connected folder's root. Done when every entry is an absolute device path.
3. **Stage in batches of 50** — the staging tool accepts at most 50 files per call; split the list. Files land under `/mnt/user-data/uploads/<folder-name>/<relative path>`. Done when every result entry reports `ok`.
4. **Copy into a scratch folder** — work on `scratchpad/<name>/`, never in the uploads folder. Done when the copy's file count matches the inventory.
5. **Fill unreachable references** — binary assets the tool only checks for existence (images, reference folders) can be empty placeholders. Done when a baseline run of the tool on the copy matches the result on the device.
6. **Deliver results back** — results that belong on the computer go back through the device tools (write directly for text, commit staged outputs for binaries). The staged copy is never written back wholesale.

## Gotchas
- **Missed files** — staging only `docs/` misses root-level files the tool also scans; symptom: counts differ from the device run. Fix: inventory from the tool's own discovery logic, not from the folder you expect.
- **Stale snapshot** — staged files are a point-in-time copy; if the user edits meanwhile, re-check modification times before deriving results.
- **Unstageable paths** — files outside connected folders (device home, temp) can't be staged; move or request access instead.

## Verify
- A baseline run on the copy reproduces the device result exactly.

## See also
- Run log: [`runs/stage-device-folder.md`](runs/stage-device-folder.md)
- Used by: [generalize-project-lint](generalize-project-lint.md)
