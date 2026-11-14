# change-report data

Common keys: `title` (2 to 4 word name, max 60), `date`, `source`, `bottom_line` (max 260), optional `ask`.

| Key | Type | Notes |
|---|---|---|
| `checkpoint` | string, max 140 | The state the changes are measured from |
| `areas` | list, 1 to 12 | `{id, label}`; groups on the page |
| `items` | list, 1 to 60 | See below |
| `items[].id`, `.area`, `.title` | strings | `area` is an area id; title max 100 |
| `.kind` | enum | `added`, `changed`, `removed`, `reversed`, `conflict` |
| `.before`, `.after` | strings, max 700 | `added` needs `after`; `removed` needs `before`; the other kinds need both. The page highlights word-level differences |
| `.why` | string, max 220 | One line of rationale |
| `.ref` | string, max 30 | Rule or decision id |
| `.review` | boolean | Flags "needs review" |
| `.before_label`, `.after_label` | strings, max 22 | Replace "Before" and "After", useful for a `conflict` |

Use `reversed` when a change undoes the earlier direction, and `conflict` for two statements that contradict each other.

```json
{"title": "Config changes", "date": "2026-11-14", "source": "git diff v1.2..HEAD", "checkpoint": "release v1.2",
 "bottom_line": "One setting was reversed.", "areas": [{"id": "auth", "label": "Authentication"}],
 "items": [{"id": "C1", "area": "auth", "kind": "reversed", "review": true, "title": "Sessions no longer expire",
   "before": "A session ends after 15 idle minutes.", "after": "A session lasts until sign-out."}]}
```

Answer block: reviewed ids and the items still to review, with kind and review flag. Worked example: `assets/examples/change-report.json`.
