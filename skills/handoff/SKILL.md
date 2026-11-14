---
name: handoff
description: Builds a self-contained HTML handoff page (decision brief, system map, change report or explainer) instead of a wall of Markdown. Use for "handoff page", "visual summary", "show me instead of a wall of text", "checkpoint", "decisions needed", "review of changes", "explain this visually", or when results with structure, flow, comparison or quantity go to the reader. Stop for a short answer (reply in chat) and for prose people edit (write a document).
---

# Handoff

A **handoff page** is a view of results. The files stay the source of truth. The agent writes only a data JSON; `scripts/build.py` validates it and injects it into a fixed template.

## Templates

| Template | Use when | Reader does | Schema |
|---|---|---|---|
| `decision-brief` | Decisions are open | Picks options, copies the answers | `references/decision-brief.md` |
| `system-map` | The state of a project with parts and dependencies | Explores, finds the hot spots | `references/system-map.md` |
| `change-report` | Something changed since a checkpoint | Reviews flagged items, ticks them off | `references/change-report.md` |
| `explainer` | A topic needs teaching or a method explaining | Reads step by step, may self-check | `references/explainer.md` |

## Procedure

1. Pick the template that matches the reader's next action. Two needs mean two pages.
2. Read that template's schema, then write the data JSON (examples: `assets/examples/`). Take facts from the files and name them in `source`.
3. Build: `python3 scripts/build.py <template> <data.json> -o <out.html>`. Add `--artifact` when publishing as an Artifact. Fix each reported problem and rebuild until it passes.
4. Where a browser is available, view the built file at desktop and phone width.
5. Deliver the page as an Artifact where the session offers them, otherwise save it beside the work and give its path.
6. When the reader pastes the answer block back, apply it to the files. The page is not edited.

## Content rules

- Lead with what the reader must do or decide: `ask` and `bottom_line` say it in two sentences.
- Every section earns its place; cut the rest.
- Write short units: one decision per question, one idea per section, two lines of context.
- Use a visual wherever structure, flow, comparison or quantity is involved (graph, table, chart, diff).
- Answers return through the one copyable answer block.
- Mark illustrative content (such as a recommendation the files do not state) as illustrative in `source`.

## Troubleshooting

- A build error names the JSON path and the fix. Cut content before raising a limit.
- After editing `assets/shared/base.css` or `base.js`, run `python3 scripts/sync_shared.py`. The `--check` flag reports templates out of step.
