# overview data

Presents a finished large task to the person who commissioned it and has to judge it. Order on the page: what is required from the reader, what changed, results, open decisions, next steps.

Common keys: `title` (2 to 4 word name, max 60), `date`, `source`, `bottom_line` (the outcome, max 260), optional `ask`.

| Key | Type | Notes |
|---|---|---|
| `task` | optional string, max 220 | What was commissioned, one line |
| `actions` | list, 0 to 8 | Required. What the reader must do: `{id, kind, text, ref?}`; `kind` is `decide`, `review` or `do`; `ref` names the change or decision it points to. An empty list shows "Nothing is required from you" |
| `changes` | optional object | `{checkpoint, areas, items}`, see below |
| `results` | optional list, 1 to 8 | `{id, heading, summary?, blocks?}`; up to 4 blocks each |
| `decisions` | optional list, 1 to 8 | `{id, question, context?, options?, recommended?}`; `options` are 2 to 4 strings, `recommended` is the 0-based index. Without `options` the question is answered in the chat |
| `next_steps` | optional list, 1 to 8 | Strings, max 170 |

At least one of `changes`, `results`, `decisions`, `next_steps` is needed. Decisions whose options need pros and cons belong on a `decision-brief` page.

**Changes** (before/after with word-level differences and a "Reviewed" tick per item):

| Key | Type | Notes |
|---|---|---|
| `checkpoint` | string, max 140 | The state the changes are measured from |
| `areas` | list, 1 to 12 | `{id, label}`; groups on the page |
| `items` | list, 1 to 60 | `id`, `area`, `kind`, `title` (max 100); optional `why` (max 220), `ref`, `review`, `before`, `after` (max 700), `before_label`, `after_label` |
| `items[].kind` | enum | `added` (needs `after`), `removed` (needs `before`), `changed`, `reversed`, `conflict` (need both). Use `reversed` when a change undoes the earlier direction, `conflict` for two statements that contradict each other |
| `items[].review` | boolean | Flags "needs review"; flagged items start open |

**Result blocks:**

| `type` | Keys |
|---|---|
| `stats` | `items`: 2 to 6 of `{label, value, note?, tone?}`; tone is `good`, `warn` or `bad`. For the few numbers that carry the result |
| `table` | `columns` (2 to 6), `rows` (1 to 10, same cell count), optional `caption` |
| `chart` | `kind` (`bar` or `line`), `labels` (2 to 12), `series` (1 to 3 of `{name, values}`), optional `title`, `unit`, `caption` |
| `list` | `items` (2 to 8), optional `ordered`, `title` |

Answer block: actions done, changes reviewed and still open, the option picked per decision. Worked example: `assets/examples/overview.json`.
