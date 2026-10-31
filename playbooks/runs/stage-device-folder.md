---
title: Stage a folder from the user's computer — run log
type: runlog
updated: 2026-10-31
---
# Stage a folder from the user's computer — run log
Playbook: [`../stage-device-folder.md`](../stage-device-folder.md). One entry per run, newest at the bottom.

### Run 1 — 2026-10-31 — 83 files of a docs project for a lint regression
| # | Tried | Result | Why / lesson |
|---|---|---|---|
| 1 | Listed `docs/` and `tools/` on the device with `find`, converted to Windows paths with a one-line Python pipe | 80 paths | Doing the conversion on the device avoided hand-typing paths |
| 2 | Staged in two calls (50 + 30) | All `ok`, landed under `uploads/<folder>/` | The 50-file cap per call is a hard limit |
| 3 | Baseline lint on the copy | 2 broken links | Linked `references/` assets weren't staged; empty placeholders fixed it |
| 4 | Noticed the lint walks the whole repo, not just `docs/` | 3 more Markdown files at the root and in `mod/` | Staged them; baseline then matched the device (0 errors) |

**Outcome:** done; baseline reproduced, original never modified.
