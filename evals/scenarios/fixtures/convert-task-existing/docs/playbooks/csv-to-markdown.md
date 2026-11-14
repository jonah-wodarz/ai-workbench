---
title: CSV export to Markdown
type: playbook
status: draft
updated: 2026-10-14
runs: 1
last_run: 2026-10-14
---
# CSV export to Markdown
> Converts the monthly semicolon CSV export into a Markdown table with tools/convert.py.

## When to use
- A fresh export arrives in `data/` and has to become a Markdown table.

## Prerequisites
- Python 3 and `tools/convert.py`.

## Steps
1. **Create the output folder** — `mkdir -p out`. Done when: `out/` exists.
2. **Run the converter** — `OUT_DIR=out python3 tools/convert.py data/<export>.csv --encoding latin-1`. Done when: the command prints `wrote out/<export>.md`.
3. **Check the result** — open `out/<export>.md`. Done when: umlauts display correctly and the table has one row per record.

## Gotchas
- **`KeyError: 'OUT_DIR'`** — the script reads the output folder from the environment; fix: set `OUT_DIR=out`.
- **`output directory ... does not exist`** — the script does not create the folder; fix: `mkdir -p out`.
- **`UnicodeDecodeError`** — the export is Latin-1, the script defaults to UTF-8; fix: pass `--encoding latin-1`.

## Verify
- `out/<export>.md` exists and shows umlauts (ä, ö, ü) correctly.

## See also
- Run log: [`runs/csv-to-markdown.md`](runs/csv-to-markdown.md)
