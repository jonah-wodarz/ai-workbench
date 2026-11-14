# system-map data

Common keys: `title` (2 to 4 word name, max 60), `date`, `source`, `bottom_line` (max 260), optional `ask`.

| Key | Type | Notes |
|---|---|---|
| `layers` | list, 1 to 8 | `{id, label}`; columns when `columns` is `layer` |
| `groups` | optional list, 1 to 10 | `{id, label}`; columns when `columns` is `group` |
| `statuses` | optional list | `{id, label, tone}`; tone is `good`, `warn`, `bad`, `info` or `muted`. Default: idea, drafting, settled, validated, locked, deferred |
| `columns` | `layer` or `group` | Default `layer`; the reader can switch when `groups` exists |
| `fan_out_warn` | integer, default 8 | Fan-out above this is flagged |
| `nodes` | list, 1 to 60 | `id` (max 10), `label` (max 40), `layer`, `status`; optional `group`, `summary` (max 240), `open` (open questions, integer) |
| `edges` | list, 0 to 300 | `{from, to, note?}`: `from` depends on `to`. No self edges or duplicates |

The page computes fan-in and fan-out, mutual pairs (two nodes that depend on each other) and dependency cycles. Do not supply them. Legibility: up to about 60 nodes and 300 edges; the table view stays readable beyond that.

```json
{"title": "Service map", "date": "2026-11-14", "source": "docs/architecture.md", "bottom_line": "Billing and Search depend on each other.",
 "layers": [{"id": "core", "label": "Core"}],
 "nodes": [{"id": "BIL", "label": "Billing", "layer": "core", "status": "drafting", "open": 3},
           {"id": "SRC", "label": "Search", "layer": "core", "status": "settled"}],
 "edges": [{"from": "BIL", "to": "SRC"}, {"from": "SRC", "to": "BIL"}]}
```

No answer block: the page is read and explored. Worked example: `assets/examples/system-map.json`.
