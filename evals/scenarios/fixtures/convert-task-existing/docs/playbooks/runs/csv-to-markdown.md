---
title: CSV export to Markdown — run log
type: runlog
updated: 2026-10-14
---
# CSV export to Markdown — run log
Playbook: [`../csv-to-markdown.md`](../csv-to-markdown.md). One entry per run, newest at the bottom. This is the thinking behind the playbook: what was tried, what failed, why the steps are what they are.

### Run 1 — 2026-10-14 — convert the October export
| # | Tried | Result | Why / lesson |
|---|---|---|---|
| 1 | `python3 tools/convert.py data/export.csv` | failed: `KeyError: 'OUT_DIR'` | The script reads the target folder from the environment. |
| 2 | `OUT_DIR=out python3 tools/convert.py data/export.csv` | failed: output directory does not exist | The script does not create the folder. |
| 3 | `mkdir -p out`, then the same command | failed: `UnicodeDecodeError` | The export is Latin-1. |
| 4 | Same command with `--encoding latin-1` | worked | Added all three to the gotchas. |

**Outcome:** done; the playbook gained all steps and gotchas.
