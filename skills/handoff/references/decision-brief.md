# decision-brief data

Common keys on every template: `title` (a 2 to 4 word name, max 60), `date`, `source` (path or command the content came from), `bottom_line` (one sentence, max 260), optional `ask` (what the reader does, max 220).

| Key | Type | Notes |
|---|---|---|
| `decisions` | list, 1 to 12 | More than 12: split into batches |
| `decisions[].id` | string | `D1`, `D2`; shown on the page and in the answer block |
| `.question` | string, max 170 | Sized to one decision |
| `.context` | string, max 300 | Two lines |
| `.options` | list, 2 to 4 | Each: `id`, `label` (max 70), optional `summary` (max 160), `pros` and `cons` (max 3 each, max 110 characters; at least one entry in total) |
| `.recommended`, `.reason` | option id, string | Both or neither; `reason` max 260 |
| `.affects` | list of strings, max 6 | Chips, such as system codes |
| `.tag` | string, max 16 | `blocking` renders red, any other tag amber |

Inline markup in text: `**term**` and backticked code.

```json
{"title": "Caching decisions", "date": "2026-11-14", "source": "docs/cache.md",
 "bottom_line": "Two decisions block the cache layer.",
 "decisions": [{"id": "D1", "question": "Where does the cache live?", "context": "Reads dominate writes.",
   "options": [{"id": "a", "label": "In memory", "pros": ["No new service"], "cons": ["Lost on restart"]},
               {"id": "b", "label": "Redis", "pros": ["Survives restarts"], "cons": ["New service"]}],
   "recommended": "b", "reason": "Restarts empty a memory cache daily."}]}
```

Answer block: `D1: chose b (Redis). Note: ...` per decision, `open` when unanswered, and a closing count. Worked example: `assets/examples/decision-brief.json`.
