# explainer data

Common keys: `title` (2 to 4 word name, max 60), `date`, `source`, `bottom_line` (max 260), optional `ask`.

`sections`: list, 1 to 10, one idea each. Keys: `id`, `heading` (max 70), `idea` (one sentence, max 210), optional `body` (up to 4 paragraphs, max 620 each), `blocks` (up to 5), `check` (up to 3).

| Block `type` | Keys |
|---|---|
| `callout` | `kind` (`definition`, `pitfall`, `example`), `text` (max 420), optional `title` |
| `flow` | `steps` (2 to 7 of `{label, note?}`), optional `loop` (return-path text), `caption` |
| `table` | `columns` (2 to 6), `rows` (1 to 10 lists, one cell per column), optional `caption` |
| `chart` | `kind` (`bar` horizontal or `line`), `labels` (2 to 12), `series` (1 to 3 of `{name, values}`, one value per label), optional `title`, `unit`, `caption` |
| `layers` | `layers` (2 to 8 of `{label, note, tag?}`, top first), optional `title`, `direction`, `caption` |
| `list` | `items` (2 to 8), optional `ordered`, `title` |

`check` entries: `q`, `options` (2 to 4, similar length, plausible), `answer` (0-based index), `explain`. Inline markup in text: `**term**` and backticked code.

```json
{"title": "How retries work", "date": "2026-11-14", "source": "docs/client.md", "bottom_line": "Cap attempts and grow the waits.",
 "sections": [{"id": "s1", "heading": "Why retry", "idea": "Most failures are brief.",
   "blocks": [{"type": "flow", "steps": [{"label": "Send"}, {"label": "Fail"}, {"label": "Wait"}], "loop": "Stop at the cap"}]}]}
```

Answer block (only when any `check` exists): per question correct, missed or not checked. Worked example: `assets/examples/explainer.json`.
